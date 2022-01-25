# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
The RemoteSync plugin makes it possible to synchronize songs, custom slides and service files.
There is currently 2 different Synchronizer backends: FolderSynchronizer and FtpSynchronizer.
When synchronizing there is 3 things to do:
  1. Pull updates from the remote.
  2. Push updates to the remote.
  3. Handle conflicts.
"""
import logging
import uuid
from sqlalchemy.sql import and_
from PyQt5 import QtWidgets, QtCore

from openlp.core.common.settings import Settings
from openlp.core.common.registry import Registry
from openlp.core.common.i18n import translate
from openlp.core.lib import build_icon
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.ui.icons import UiIcons
from openlp.core.lib.db import Manager
from openlp.core.common.enum import SyncType
from openlp.plugins.remotesync.lib.backends.synchronizer import SyncItemType, SyncItemAction, ConflictException, \
    LockException
from openlp.core.state import State
from openlp.plugins.songs.lib.db import Song

from openlp.plugins.remotesync.lib import RemoteSyncTab
from openlp.plugins.remotesync.lib.backends.foldersynchronizer import FolderSynchronizer
from openlp.plugins.remotesync.lib.backends.ftpsynchronizer import FtpSynchronizer
from openlp.plugins.remotesync.lib.db import init_schema, SyncQueueItem, RemoteSyncItem

log = logging.getLogger(__name__)


class RemoteSyncPlugin(Plugin):
    log.info('RemoteSync Plugin loaded')

    def __init__(self):
        """
        remotes constructor
        """
        super(RemoteSyncPlugin, self).__init__('remotesync', None, RemoteSyncTab)
        self.weight = -1
        self.manager = Manager('remotesync', init_schema)
        self.icon = UiIcons().network_stream
        self.icon_path = self.icon
        self.synchronizer = None
        State().add_service('remote_sync', self.weight, is_plugin=True)
        State().update_pre_conditions('remote_sync', self.check_pre_conditions())

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.manager.session is not None

    def initialise(self):
        """
        Initialise the remotesync plugin
        """
        log.debug('initialise')
        super(RemoteSyncPlugin, self).initialise()
        if not hasattr(self, 'remote_sync_icon'):
            self.remote_sync_icon = QtWidgets.QLabel(self.main_window.status_bar)
            size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            size_policy.setHorizontalStretch(0)
            size_policy.setVerticalStretch(0)
            size_policy.setHeightForWidth(self.remote_sync_icon.sizePolicy().hasHeightForWidth())
            self.remote_sync_icon.setSizePolicy(size_policy)
            self.remote_sync_icon.setFrameShadow(QtWidgets.QFrame.Plain)
            self.remote_sync_icon.setLineWidth(1)
            self.remote_sync_icon.setScaledContents(True)
            self.remote_sync_icon.setFixedSize(20, 20)
            self.remote_sync_icon.setObjectName('remote_sync_icon')
            self.main_window.status_bar.insertPermanentWidget(2, self.remote_sync_icon)
            self.settings_tab.remote_sync_icon = self.remote_sync_icon
        # TODO: Generate a pc id
        self.settings_tab.generate_icon()
        sync_type = Settings().value('remotesync/type')
        if sync_type == SyncType.Folder:
            self.synchronizer = FolderSynchronizer(self.manager, Settings().value('remotesync/folder path'),
                                                   Settings().value('remotesync/folder pc id'))
        elif sync_type == SyncType.Ftp:
            self.synchronizer = FtpSynchronizer(self.manager, Settings().value('remotesync/ftp data folder'),
                                                Settings().value('remotesync/folder pc id'),
                                                Settings().value('remotesync/ftp type'),
                                                Settings().value('remotesync/ftp server'),
                                                Settings().value('remotesync/ftp username'),
                                                Settings().value('remotesync/ftp password'))
        else:
            self.synchronizer = None
        if self.synchronizer and not self.synchronizer.check_connection():
            self.synchronizer.initialize_remote()
        # TODO: register delete functions
        Registry().register_function('song_changed', self.queue_song_for_sync)
        Registry().register_function('custom_changed', self.queue_custom_for_sync)
        Registry().register_function('service_changed', self.save_service)
        Registry().register_function('synchronize_to_remote', self.push_to_remote)
        Registry().register_function('synchronize_from_remote', self.pull_from_remote)
        Registry().register_function('song_deleted', self.queue_song_for_deletion)
        self.startup_check()
        if self.synchronizer:
            # Set a timer to start the processing of the queue in 10 seconds
            QtCore.QTimer.singleShot(10000, self.synchronize)

    def finalise(self):
        log.debug('finalise')
        super(RemoteSyncPlugin, self).finalise()

    @staticmethod
    def about():
        """
        Information about this plugin
        """
        about_text = translate('RemoteSyncPlugin', '<strong>RemoteSync Plugin</strong>'
                                                   '<br />The remotesync plugin provides the ability to synchronize '
                                                   'songs, custom slides and service-files between multiple OpenLP '
                                                   'instances.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('RemoteSyncPlugin', 'RemoteSync', 'name singular'),
            'plural': translate('RemoteSyncPlugin', 'RemotesSync', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('RemoteSyncPlugin', 'RemoteSync', 'container title')
        }

    def startup_check(self):
        """
        Run through all songs and custom slides to see if they have been synchronized. Queue them if they have not
        """
        song_manager = Registry().get('songs_manager')
        all_songs = song_manager.get_all_objects(Song)
        for song in all_songs:
            # TODO: Check that songs actually exists remotely - should we delete if not?
            synced_songs = self.manager.get_object_filtered(RemoteSyncItem,
                                                            and_(RemoteSyncItem.type == SyncItemType.Song,
                                                                 RemoteSyncItem.item_id == song.id))
            if not synced_songs:
                self.queue_song_for_sync(song.id)
        # TODO: Also check custom slides

    def synchronize(self):
        """
        Synchronize by first pulling data from remote and then pushing local changes to the remote
        """
        self.synchronizer.connect()
        self.pull_from_remote()
        self.push_to_remote()
        self.synchronizer.disconnect()
        # Set a timer to start the synchronization again in 10 minutes.
        QtCore.QTimer.singleShot(600000, self.synchronize)

    def push_to_remote(self):
        """
        Run through the queue and push songs and custom slides to remote
        """
        queue_items = self.manager.get_all_objects(SyncQueueItem)
        song_manager = Registry().get('songs_manager')
        for queue_item in queue_items:
            if queue_item.type == SyncItemType.Song:
                if queue_item.action == SyncItemAction.Update:
                    song = song_manager.get_object(Song, queue_item.item_id)
                    # If song has not been sync'ed before we generate a uuid
                    sync_item = self.manager.get_object_filtered(RemoteSyncItem,
                                                                 and_(RemoteSyncItem.type == SyncItemType.Song,
                                                                      RemoteSyncItem.item_id == song.id))
                    if not sync_item:
                        sync_item = RemoteSyncItem()
                        sync_item.type = SyncItemType.Song
                        sync_item.item_id = song.id
                        sync_item.uuid = str(uuid.uuid4())
                    # Synchronize the song
                    try:
                        version = self.synchronizer.send_song(song, sync_item.uuid, sync_item.version,
                                                              queue_item.first_attempt, queue_item.lock_id)
                    except ConflictException:
                        log.debug('Conflict detected for song %d / %s' % (sync_item.item_id, sync_item.uuid))
                        # TODO: Store the conflict in the DB and turn on the conflict icon
                        continue
                    except LockException as le:
                        # Store the lock time in the DB and keep it in the queue
                        log.debug('Lock detected for song %d / %s' % (sync_item.item_id, sync_item.uuid))
                        queue_item.first_attempt = le.first_attempt
                        queue_item.lock_id = le.lock_id
                        self.manager.save_object(queue_item)
                        continue
                    sync_item.version = version
                    # Save the RemoteSyncItem so we know which version we have locally
                    self.manager.save_object(sync_item, True)
                elif queue_item.action == SyncItemAction.Delete:
                    # Delete the song
                    try:
                        version = self.synchronizer.delete_song(sync_item.uuid, sync_item.version,
                                                                queue_item.first_attempt, queue_item.lock_id)
                    except ConflictException:
                        log.debug('Conflict detected for song %d / %s' % (sync_item.item_id, sync_item.uuid))
                        # TODO: Store the conflict in the DB and turn on the conflict icon
                        continue
                    except LockException as le:
                        # Store the lock time in the DB and keep it in the queue
                        log.debug('Lock detected for song %d / %s' % (sync_item.item_id, sync_item.uuid))
                        queue_item.first_attempt = le.first_attempt
                        queue_item.lock_id = le.lock_id
                        self.manager.save_object(queue_item)
                        continue
                # Delete the SyncQueueItem from the queue since the synchronization is now complete
                self.manager.delete_all_objects(SyncQueueItem, and_(SyncQueueItem.item_id == queue_item.item_id,
                                                                    SyncQueueItem.type == SyncItemType.Song))

            elif queue_item.type == SyncItemType.Custom:
                # TODO: Handle custom slides
                pass

    def queue_song_for_sync(self, song_id):
        """
        Put song in queue to be sync'ed
        :param song_id:
        """
        # First check that the song isn't already in the queue
        queue_item = self.manager.get_object_filtered(SyncQueueItem, and_(SyncQueueItem.item_id == song_id,
                                                                          SyncQueueItem.type == SyncItemType.Song))
        if not queue_item:
            queue_item = SyncQueueItem()
            queue_item.item_id = song_id
            queue_item.type = SyncItemType.Song
            queue_item.action = SyncItemAction.Update
            self.manager.save_object(queue_item, True)

    def queue_custom_for_sync(self, custom_id):
        """
        Put custom slide in queue to be sync'ed
        :param custom_id:
        """
        # First check that the custom slide isn't already in the queue
        queue_item = self.manager.get_object_filtered(SyncQueueItem, and_(SyncQueueItem.item_id == custom_id,
                                                                          SyncQueueItem.type == SyncItemType.Custom))
        if not queue_item:
            queue_item = SyncQueueItem()
            queue_item.item_id = custom_id
            queue_item.type = SyncItemType.Custom
            queue_item.action = SyncItemAction.Update
            self.manager.save_object(queue_item, True)

    def queue_song_for_deletion(self, song_id):
        """
        Put song in queue to be deleted
        :param song_id:
        """
        queue_item = SyncQueueItem()
        queue_item.item_id = song_id
        queue_item.type = SyncItemType.Song
        queue_item.action = SyncItemAction.Delete
        self.manager.save_object(queue_item, True)

    def queue_custom_for_deletion(self, custom_id):
        """
        Put custom slide in queue to be deleted
        :param custom_id:
        """
        queue_item = SyncQueueItem()
        queue_item.item_id = custom_id
        queue_item.type = SyncItemType.Song
        queue_item.action = SyncItemAction.Delete
        self.manager.save_object(queue_item, True)

    def pull_from_remote(self):
        updated = self.synchronizer.get_remote_changes()
        if updated:
            Registry().execute('songs_load_list')

    def save_service(self, service_item):
        pass

    def handle_conflicts(self):
        # (Re)use the duplicate song UI to let the user manually handle the conflicts. Also allow for batch
        # processing, where either local or remote always wins.
        pass