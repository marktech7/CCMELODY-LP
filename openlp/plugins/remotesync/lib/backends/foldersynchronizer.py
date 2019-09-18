# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
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
import datetime
import os
import glob
import shutil

import logging

from openlp.plugins.remotesync.lib.backends.synchronizer import Synchronizer, SyncItemType, ConflictException, \
    LockException, ConflictReason
from openlp.plugins.remotesync.lib.db import RemoteSyncItem

log = logging.getLogger(__name__)


class FolderSynchronizer(Synchronizer):
    """
    The FolderSynchronizer uses xml-files in a simple holder structure for synchronizing data.
    The folder-structure looks like this:
    <base-folder>
    +---songs
    |   +---history
    |   +---deleted
    +---customs
    |   +---history
    |   +---deleted
    +---services
    The files are named after the uuid generated for each song or custom slide, the id of the
    OpenLP instance and the version of the song, like this: {uuid}={version}={computer_id}.xml
    An example could be: bd5bc6c2-4fd2-4a42-925f-48d00de835ec=4=churchpc1.xml
    When a file is updated a lock file is created to signal that the song is locked. The filename
    of the lock file is: {uuid}.lock={computer_id}={version}
    As part of the updating of the file, the old version is moved to the appropriate history folder.
    When a song/custom slide is deleted, its file is moved to the history-folder, and an empty file
    named as the items uuid is placed in the deleted-folder.
    """

    def __init__(self, manager, base_folder_path, pc_id):
        """
        Initilize the synchronizer
        :param manager:
        :type Manager:
        :param base_folder_path:
        :type str:
        :param pc_id:
        :type str:
        """
        super(FolderSynchronizer, self).__init__(manager)
        self.base_folder_path = base_folder_path
        self.pc_id = pc_id
        self.song_folder_path = os.path.join(self.base_folder_path, 'songs')
        self.song_history_folder_path = os.path.join(self.song_folder_path, 'history')
        self.song_deleted_folder_path = os.path.join(self.song_folder_path, 'deleted')
        self.custom_folder_path = os.path.join(self.base_folder_path, 'customs')
        self.custom_history_folder_path = os.path.join(self.custom_folder_path, 'history')
        self.custom_deleted_folder_path = os.path.join(self.custom_folder_path, 'deleted')
        self.service_folder_path = os.path.join(self.base_folder_path, 'services')

    def check_configuration(self):
        return True

    def check_connection(self):
        return os.path.exists(self.base_folder_path) and os.path.exists(
            self.song_history_folder_path) and os.path.exists(self.custom_folder_path)

    def initialize_remote(self):
        os.makedirs(self.song_history_folder_path, exist_ok=True)
        os.makedirs(self.custom_folder_path, exist_ok=True)
        os.makedirs(self.service_folder_path, exist_ok=True)

    def _get_file_list(self, path, mask):
        return glob.glob(os.path.join(path, mask))

    def _remove_lock_file(self, lock_filename):
        os.remove(lock_filename)

    def _move_file(self, src, dst):
        shutil.move(src, dst)

    def _create_file(self, filename, file_content):
        out_file = open(filename, 'wt')
        out_file.write(file_content)
        out_file.close()

    def _read_file(self, filename):
        in_file = open(filename, 'rt')
        content = in_file.read()
        in_file.close()
        return content

    def get_remote_changes(self):
        """
        Check for changes in the remote/shared folder. If a changed/new item is found it is fetched using the
        fetch_song method, and if a conflict is detected the mark_item_for_conflict is used. If items has been deleted
        remotely, they are also deleted locally.
        :return: True if one or more songs was updated, otherwise False
        """
        updated = False
        song_files = self._get_file_list(self.song_folder_path, '*.xml')
        conflicts = []
        for song_file in song_files:
            # skip conflicting files
            if song_file in conflicts:
                continue
            # Check if this song is already sync'ed
            filename = os.path.basename(song_file)
            filename_elements = filename.split('=', 1)
            uuid = filename_elements[0]
            file_version = filename_elements[1].replace('.xml', '')
            # Detect if there are multiple files for the same song, which would mean that we have a conflict
            files = []
            for song_file2 in song_files:
                if uuid in song_file2:
                    files.append(song_file2)
            # if more than one song file has the same uuid, then we have a conflict
            if len(files) > 1:
                # Add conflicting files to the "blacklist"
                conflicts += files
                # Mark song as conflicted!
                self.mark_item_for_conflict(SyncItemType.Song, uuid, ConflictReason.MultipleRemoteEntries)
            existing_item = self.get_sync_item(uuid, SyncItemType.Song)
            song_id = existing_item.item_id if existing_item else None
            # If we do not have a local version or if the remote version is different, then we update
            if not existing_item or existing_item.version != file_version:
                log.debug('Local version (%s) and file version (%s) mismatch - updated triggered!' % (
                    existing_item.version, file_version))
                log.debug('About to fetch song: %s %d' % (uuid, song_id))
                try:
                    self.fetch_song(uuid, song_id)
                except ConflictException as ce:
                    log.debug('Conflict detected while fetching song %d / %s!' % (song_id, uuid))
                    self.mark_item_for_conflict(SyncItemType.Song, uuid, ce.reason)
                    continue
                updated = True
            # TODO: Check for deleted files
        return updated

    def _check_for_lock_file(self, type, path, uuid, first_sync_attempt, prev_lock_id):
        """
        Check for lock file. Raises exception if a valid lock file is found. If an expired lock file is found
        it is deleted.
        :param type:
        :type str:
        :param path:
        :type str:
        :param uuid:
        :type str:
        :param first_sync_attempt:
        :type datetime:
        :param prev_lock_id:
        :type str:
        """
        existing_lock_file = self._get_file_list(path, uuid + '.lock*')
        if existing_lock_file:
            log.debug('Found a lock file!')
            current_lock_id = existing_lock_file[0].split('.lock=')[-1]
            if first_sync_attempt:
                # Have we seen this lock before?
                if current_lock_id == prev_lock_id:
                    # If the lock is more than 60 seconds old it is deleted
                    delta = datetime.datetime.now() - first_sync_attempt
                    if delta.total_seconds() > 60:
                        # Remove expired lock
                        self._remove_lock_file(existing_lock_file[0])
                    else:
                        # Lock is still valid, keep waiting
                        raise LockException(type, uuid, current_lock_id, first_sync_attempt)
                else:
                    # New lock encountered, now we have to wait - again
                    raise LockException(type, uuid, current_lock_id, datetime.datetime.now())
            else:
                # New lock encountered, now we have to wait for it
                raise LockException(type, uuid, current_lock_id, datetime.datetime.now())

    def send_song(self, song, song_uuid, last_known_version, first_sync_attempt, prev_lock_id):
        """
        Sends a song to the shared folder. Does the following:
        1. Check for an existing lock, raise LockException if one found.
        2. Check if the song already exists on remote. If so, check if the latest version is available locally, raise
           ConflictException if the remote version is not known locally. If the latest version is known, create a lock
           file and move the existing file to the history folder. If the song does not exists already, just create a
           lock file.
        3. Place file with song in folder.
        4. Delete lock file.
        :param song: The song object to synchronize
        :param song_uuid: The uuid of the song
        :param last_known_version: The last known version of the song
        :param first_sync_attempt: If the song has been attempted synchronized before,
                                  this is the timestamp of the first sync attempt.
        :param prev_lock_id: If the song has been attempted synchronized before, this is the id of the lock that
                             prevented the synchronization.
        :return: The new version.
        """
        # Check for lock file. Will raise exception on lock
        self._check_for_lock_file(SyncItemType.Song, self.song_folder_path, song_uuid, first_sync_attempt, prev_lock_id)
        # Check if song already exists
        existing_song_files = self._get_file_list(self.song_folder_path, song_uuid + '*.xml')
        counter = -1
        if existing_song_files:
            # Handle case with multiple files returned, which indicates a conflict!
            if len(existing_song_files) > 1:
                raise ConflictException(SyncItemType.Song, song_uuid, ConflictReason.MultipleRemoteEntries)
            existing_file = os.path.basename(existing_song_files[0])
            filename_elements = existing_file.split('=')
            counter = int(filename_elements[1])
            if last_known_version:
                current_local_counter = int(last_known_version.split('=')[0])
                # Check if we do have the latest version locally, if not we flag a conflict
                if current_local_counter != counter:
                    raise ConflictException(SyncItemType.Song, song_uuid, ConflictReason.VersionMismatch)
            counter += 1
            # Create lock file
            lock_filename = '{path}.lock={pcid}={counter}'.format(path=os.path.join(self.song_folder_path, song_uuid),
                                                                  pcid=self.pc_id, counter=counter)
            self._create_file(lock_filename, '')
            # Move old file to history folder
            self._move_file(os.path.join(self.song_folder_path, existing_file), self.song_history_folder_path)
        else:
            # TODO: Check for missing (deleted) file
            lock_filename = '{path}.lock={pcid}={counter}'.format(path=os.path.join(self.song_folder_path, song_uuid),
                                                                  pcid=self.pc_id, counter=counter)
            counter += 1
            # Create lock file
            self._create_file(lock_filename, '')
        # Put xml in file
        version = '{counter}={computer_id}'.format(counter=counter, computer_id=self.pc_id)
        xml = self.open_lyrics.song_to_xml(song, version)
        new_filename = os.path.join(self.song_folder_path, song_uuid + "=" + version + '.xml')
        new_tmp_filename = new_filename + '-tmp'
        self._create_file(new_tmp_filename, xml)
        self._move_file(new_tmp_filename, new_filename)
        # Delete lock file
        self._remove_lock_file(lock_filename)
        return version

    def fetch_song(self, song_uuid, song_id):
        """
        Fetch a specific song from the shared folder
        :param song_uuid: uuid of the song
        :param song_id: song db id, None if song does not yet exists in the song db
        :return: The song object
        """
        # Check for lock file - is this actually needed? should we create a read lock?
        if self._get_file_list(self.song_folder_path, song_uuid + '.lock'):
            log.debug('Found a lock file! Ignoring it for now.')
        existing_song_files = self._get_file_list(self.song_folder_path, song_uuid + '*')
        if existing_song_files:
            # Handle case with multiple files returned, which indicates a conflict!
            if len(existing_song_files) > 1:
                raise ConflictException(SyncItemType.Song, song_uuid, ConflictReason.MultipleRemoteEntries)
            existing_file = os.path.basename(existing_song_files[0])
            filename_elements = existing_file.split('=', 1)
            song_uuid = filename_elements[0]
            version = filename_elements[1]
            xml = self._read_file(existing_song_files[0])
            song = self.open_lyrics.xml_to_song(xml, update_song_id=song_id)
            sync_item = self.manager.get_object_filtered(RemoteSyncItem, RemoteSyncItem.uuid == song_uuid)
            if not sync_item:
                sync_item = RemoteSyncItem()
                sync_item.type = SyncItemType.Song
                sync_item.item_id = song.id
                sync_item.uuid = song_uuid
            sync_item.version = version
            self.manager.save_object(sync_item, True)
            return song
        else:
            return None

    def delete_song(self, song_uuid, first_del_attempt, prev_lock_id):
        """
        Delete song from the remote location. Does the following:
        1. Check for an existing lock, raise LockException if one found.
        2. Create a lock file and move the existing file to the history folder.
        3. Place a file in the deleted folder, named after the song uuid.
        4. Delete lock file.
        :param song_uuid:
        :type str:
        :param first_del_attempt:
        :type DateTime:
        :param prev_lock_id:
        :type str:
        """
        # Check for lock file. Will raise exception on lock
        self._check_for_lock_file(SyncItemType.Song, self.song_folder_path, song_uuid, first_del_attempt, prev_lock_id)
        # Move the song xml file to the history folder
        existing_song_files = self._get_file_list(self.song_folder_path, song_uuid + '*.xml')
        if existing_song_files:
            # Handle case with multiple files returned, which indicates a conflict!
            if len(existing_song_files) > 1:
                raise ConflictException(SyncItemType.Song, song_uuid, ConflictReason.MultipleRemoteEntries)
            existing_file = os.path.basename(existing_song_files[0])
            # Move old file to deleted folder
            self._move_file(os.path.join(self.song_folder_path, existing_file), self.song_history_folder_path)
        # Create a file in the deleted-folder
        delete_filename = os.path.join(self.song_deleted_folder_path, song_uuid)
        self._create_file(delete_filename, '')

    def send_custom(self, custom):
        pass

    def fetch_custom(self):
        pass

    def send_service(self, service):
        pass

    def fetch_service(self):
        pass
