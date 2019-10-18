# -*- coding: utf-8 -*-

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

import logging
import os

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import UiStrings, get_natural_key, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.path import create_paths, path_to_str
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import MediaType, ServiceItemContext, check_item_selected
from openlp.core.lib.mediamanageritem import MediaManagerItem
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import parse_optical_path, format_milliseconds, AUDIO_EXT, VIDEO_EXT
from openlp.core.ui.media.vlcplayer import get_vlc

if get_vlc() is not None:
    from openlp.plugins.media.forms.mediaclipselectorform import MediaClipSelectorForm


log = logging.getLogger(__name__)


CLAPPERBOARD = UiIcons().clapperboard


class MediaMediaItem(MediaManagerItem, RegistryProperties):
    """
    This is the custom media manager item for Media Slides.
    """
    media_go_live = QtCore.pyqtSignal(list)
    media_add_to_service = QtCore.pyqtSignal(list)
    log.info('{name} MediaMediaItem loaded'.format(name=__name__))

    def __init__(self, parent, plugin):
        self.setup()
        super(MediaMediaItem, self).__init__(parent, plugin)

    def setup(self):
        """
        Allow early setup to be mocked.
        """
        self.icon_path = 'images/image'
        self.background = False
        self.automatic = ''
        self.error_icon = UiIcons().delete

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.media_go_live.connect(self.go_live_remote)
        self.media_add_to_service.connect(self.add_to_service_remote)
        self.single_service_item = False
        self.has_search = True
        self.media_object = None
        # self.display_controller = DisplayController(self.parent())
        # Registry().register_function('video_background_replaced', self.video_background_replaced)
        Registry().register_function('mediaitem_media_rebuild', self.rebuild_players)
        # Allow DnD from the desktop
        self.list_view.activateDnD()

    def retranslate_ui(self):
        """
        This method is called automatically to provide OpenLP with the opportunity to translate the ``MediaManagerItem``
        to another language.
        """
        self.on_new_prompt = translate('MediaPlugin.MediaItem', 'Select Media')

    def required_icons(self):
        """
        Set which icons the media manager tab should show
        """
        MediaManagerItem.required_icons(self)
        self.has_file_icon = True
        self.has_new_icon = False
        self.has_edit_icon = False
        if not State().check_preconditions('media'):
            self.can_preview = False
            self.can_make_live = False
            self.can_add_to_service = False
        if State().check_preconditions('media_live'):
            self.can_make_live = True

    def add_list_view_to_toolbar(self):
        """
        Creates the main widget for listing items.
        """
        MediaManagerItem.add_list_view_to_toolbar(self)
        # self.list_view.addAction(self.replace_action)

    def add_start_header_bar(self):
        """
        Adds buttons to the start of the header bar.
        """
        if State().check_preconditions('media'):
            optical_button_text = translate('MediaPlugin.MediaItem', 'Load CD/DVD')
            optical_button_tooltip = translate('MediaPlugin.MediaItem', 'Load CD/DVD')
            self.load_optical = self.toolbar.add_toolbar_action('load_optical', icon=UiIcons().optical,
                                                                text=optical_button_text,
                                                                tooltip=optical_button_tooltip,
                                                                triggers=self.on_load_optical)

    def generate_slide_data(self, service_item, *, item=None, remote=False, context=ServiceItemContext.Service,
                            **kwargs):
        """
        Generate the slide data. Needs to be implemented by the plugin.

        :param service_item: The service item to be built on
        :param item: The Song item to be used
        :param remote: Triggered from remote
        :param context: Why is it being generated
        :param kwargs: Consume other unused args specified by the base implementation, but not use by this one.
        """
        if item is None:
            item = self.list_view.currentItem()
            if item is None:
                return False
        filename = str(item.data(QtCore.Qt.UserRole))
        # Special handling if the filename is a optical clip
        if filename == UiStrings().LiveStream:
            service_item.processor = 'vlc'
            service_item.title = filename
            service_item.add_capability(ItemCapabilities.CanStream)
        elif filename.startswith('optical:'):
            (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(filename)
            if not os.path.exists(name):
                if not remote:
                    # Optical disc is no longer present
                    critical_error_message_box(
                        translate('MediaPlugin.MediaItem', 'Missing Media File'),
                        translate('MediaPlugin.MediaItem',
                                  'The optical disc {name} is no longer available.').format(name=name))
                return False
            service_item.processor = 'vlc'
            service_item.add_from_command(filename, name, CLAPPERBOARD)
            service_item.title = clip_name
            # Set the length
            service_item.set_media_length(end - start)
            service_item.start_time = start
            service_item.end_time = end
            service_item.add_capability(ItemCapabilities.IsOptical)
        else:
            if not os.path.exists(filename):
                if not remote:
                    # File is no longer present
                    critical_error_message_box(
                        translate('MediaPlugin.MediaItem', 'Missing Media File'),
                        translate('MediaPlugin.MediaItem', 'The file {name} no longer exists.').format(name=filename))
                return False
            (path, name) = os.path.split(filename)
            service_item.title = name
            service_item.processor = 'vlc'
            service_item.add_from_command(path, name, CLAPPERBOARD)
            # Only get start and end times if going to a service
            service_item.set_media_length(self.media_controller.media_length(filename))
        service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.add_capability(ItemCapabilities.RequiresMedia)
        if Settings().value(self.settings_section + '/media auto start') == QtCore.Qt.Checked:
            service_item.will_auto_start = True
        # force a non-existent theme
        service_item.theme = -1
        return True

    def initialise(self):
        """
        Initialize media item.
        """
        self.list_view.clear()
        self.service_path = AppLocation.get_section_data_path(self.settings_section) / 'thumbnails'
        create_paths(self.service_path)
        self.load_list([path_to_str(file) for file in Settings().value(self.settings_section + '/media files')])
        self.rebuild_players()

    def rebuild_players(self):
        """
        Rebuild the tab in the media manager when changes are made in the settings.
        """
        # self.populate_display_types()
        self.on_new_file_masks = translate('MediaPlugin.MediaItem',
                                           'Videos ({video});;Audio ({audio});;{files} '
                                           '(*)').format(video=' '.join(VIDEO_EXT),
                                                         audio=' '.join(AUDIO_EXT),
                                                         files=UiStrings().AllFiles)

    def on_delete_click(self):
        """
        Remove a media item from the list.
        """
        if check_item_selected(self.list_view,
                               translate('MediaPlugin.MediaItem', 'You must select a media file to delete.')):
            row_list = [item.row() for item in self.list_view.selectedIndexes()]
            row_list.sort(reverse=True)
            for row in row_list:
                self.list_view.takeItem(row)
            Settings().setValue(self.settings_section + '/media files', self.get_file_list())

    def load_list(self, media, target_group=None):
        """
        Load the media list

        :param media: The media
        :param target_group:
        """
        # TODO needs to be fixed as no idea why this fails
        # media.sort(key=lambda file_path: get_natural_key(file_path.name))
        file_name = translate('MediaPlugin.MediaItem', 'Live Stream')
        item_name = QtWidgets.QListWidgetItem(file_name)
        item_name.setIcon(UiIcons().video)
        item_name.setData(QtCore.Qt.UserRole, UiStrings().LiveStream)
        item_name.setToolTip(translate('MediaPlugin.MediaItem', 'Show Live Stream'))
        self.list_view.addItem(item_name)
        for track in media:
            track_str = str(track)
            track_info = QtCore.QFileInfo(track_str)
            item_name = None
            # Dont add the live stream in when reloading the UI.
            if track_str == UiStrings().LiveStream:
                continue
            elif track_str.startswith('optical:'):
                # Handle optical based item
                (file_name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(track_str)
                item_name = QtWidgets.QListWidgetItem(clip_name)
                item_name.setIcon(UiIcons().optical)
                item_name.setData(QtCore.Qt.UserRole, track)
                item_name.setToolTip('{name}@{start}-{end}'.format(name=file_name,
                                                                   start=format_milliseconds(start),
                                                                   end=format_milliseconds(end)))
            elif not os.path.exists(track):
                # File doesn't exist, mark as error.
                file_name = os.path.split(track_str)[1]
                item_name = QtWidgets.QListWidgetItem(file_name)
                item_name.setIcon(UiIcons().error)
                item_name.setData(QtCore.Qt.UserRole, track)
                item_name.setToolTip(track_str)
            elif track_info.isFile():
                # Normal media file handling.
                file_name = os.path.split(track_str)[1]
                item_name = QtWidgets.QListWidgetItem(file_name)
                search = file_name.split('.')[-1].lower()
                if search in AUDIO_EXT:
                    item_name.setIcon(UiIcons().audio)
                else:
                    item_name.setIcon(UiIcons().video)
                item_name.setData(QtCore.Qt.UserRole, track)
                item_name.setToolTip(track_str)
            if item_name:
                self.list_view.addItem(item_name)

    def get_list(self, media_type=MediaType.Audio):
        """
        Get the list of media, optional select media type.

        :param media_type: Type to get, defaults to audio.
        :return: The media list
        """
        media_file_paths = Settings().value(self.settings_section + '/media files')
        media_file_paths.sort(key=lambda file_path: get_natural_key(file_path.name))
        if media_type == MediaType.Audio:
            extension = AUDIO_EXT
        else:
            extension = VIDEO_EXT
        extension = [x[1:] for x in extension]
        media = [x for x in media_file_paths if x.suffix in extension]
        return media

    def search(self, string, show_error):
        """
        Performs a search for items containing ``string``

        :param string: String to be displayed
        :param show_error: Should the error be shown (True)
        :return: The search result.
        """
        results = []
        string = string.lower()
        for file_path in Settings().value(self.settings_section + '/media files'):
            file_name = file_path.name
            if file_name.lower().find(string) > -1:
                results.append([str(file_path), file_name])
        return results

    def on_load_optical(self):
        """
        When the load optical button is clicked, open the clip selector window.
        """
        # self.media_clip_selector_form.exec()
        if get_vlc():
            media_clip_selector_form = MediaClipSelectorForm(self, self.main_window, None)
            media_clip_selector_form.exec()
            del media_clip_selector_form
        else:
            QtWidgets.QMessageBox.critical(self, 'VLC is not available', 'VLC is not available')

    def add_optical_clip(self, optical):
        """
        Add a optical based clip to the mediamanager, called from media_clip_selector_form.

        :param optical: The clip to add.
        """
        file_paths = self.get_file_list()
        # If the clip already is in the media list it isn't added and an error message is displayed.
        if optical in file_paths:
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Mediaclip already saved'),
                                       translate('MediaPlugin.MediaItem', 'This mediaclip has already been saved'))
            return
        # Append the optical string to the media list
        file_paths.append(optical)
        self.load_list([str(optical)])
        Settings().setValue(self.settings_section + '/media files', file_paths)
