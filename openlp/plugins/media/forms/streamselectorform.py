# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
import re
import ctypes
from datetime import datetime
from pathlib import Path
from time import sleep

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import is_linux, is_macosx, is_win
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media.vlcplayer import get_vlc
from openlp.plugins.media.forms.streamselectordialog import Ui_StreamSelector


log = logging.getLogger(__name__)


class StreamSelectorForm(QtWidgets.QDialog, Ui_StreamSelector):
    """
    Class to manage the clip selection
    """
    log.info('{name} StreamSelectorForm loaded'.format(name=__name__))

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(StreamSelectorForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint |
                                                 QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setup_ui(self)
        self.insert_devices()

    def exec(self):
        """
        Start dialog
        """
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Saves the current stream as a clip to the mediamanager
        """
        log.debug('in StreamSelectorForm.accept')
        self.media_item.add_stream(None)

    def insert_devices(self):
        """
        Read device list and insert into comboboxes
        """
        vlc = get_vlc()
        vlc_instance = vlc.Instance('')
        # Create an instance of a pointer-pointer to a vlc.MediaDiscovererDescription
        services_pp = ctypes.POINTER(ctypes.POINTER(vlc.MediaDiscovererDescription))()
        # Create a pointer of the instance above
        services_ppp = ctypes.pointer(services_pp)
        # Due to a bug(?) in vlc.py we need to cast to a wrong type to make vlc.py accept the input
        services_fake_pp = ctypes.cast(services_ppp, ctypes.POINTER(ctypes.POINTER(vlc.MediaDiscovererDescription)))
        service_count = vlc_instance.media_discoverer_list_get(vlc.MediaDiscovererCategory.devices, services_fake_pp)
        list_services = []
        for i in range(service_count):
            print('item : %d' % i)
            list_services.append(services_pp[i].contents)
            print(services_pp[i].contents.cat)
            print(ctypes.c_char_p(services_pp[i].contents.name).value)
            print(ctypes.c_char_p(services_pp[i].contents.longname).value)

        # Find audio/video devices
        audio_discoverer = None
        video_discoverer = None
        for service in list_services:
            longname = service.longname.decode().lower()
            if 'audio' in longname:
                audio_discoverer = vlc_instance.media_discoverer_new(service.longname)
                audio_discoverer.start()
            elif 'video' in longname:
                video_discoverer = vlc_instance.media_discoverer_new(service.longname)
                video_discoverer.start()
        if audio_discoverer or video_discoverer:
            # allow time for devices to be discovered
            sleep(3)
            if audio_discoverer:
                audio_discoverer.stop()
                media_list = audio_discoverer.media_list()
                for i in range(media_list.count()):
                    media = media_list.item_at_index(i)
                    #print(media.get_type())
                    print(media.get_mrl())
                    self.audio_devices_combo_box.addItem(media.get_mrl())
            if video_discoverer:
                video_discoverer.stop()
                media_list = video_discoverer.media_list()
                for i in range(media_list.count()):
                    media = media_list.item_at_index(i)
                    #print(media.get_type())
                    print(media.get_mrl())
                    self.video_devices_combo_box.addItem(media.get_mrl())
        else:
            print('No VLC discoverer for audio or video found!')
        # clean up
        vlc.libvlc_media_discoverer_list_release(ctypes.cast(services_pp,
                                                             ctypes.POINTER(vlc.MediaDiscovererDescription)),
                                                 service_count)
