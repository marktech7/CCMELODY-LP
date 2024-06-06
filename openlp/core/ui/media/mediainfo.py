# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
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
The :mod:`~openlp.core.ui.media.mediainfo` module for media meta data.
"""
import logging

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from openlp.core.ui.slidecontroller import SlideController

log = logging.getLogger(__name__)

class media_info(QObject):

    def get_media_info(self, media_file: str) -> None:
        """
        Set up an media and audio player and bind it to a controller and display

        :param controller: The controller where the media is
        :param display: The display where the media is.
        :return:
        """
        # if controller.is_live:
        #     controller.media_widget = QtWidgets.QWidget(controller)
        #     controller.media_widget.setWindowFlags(
        #         QtCore.Qt.WindowType.FramelessWindowHint
        #         | QtCore.Qt.WindowType.Tool
        #         | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        #     controller.media_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_X11NetWmWindowTypeDialog)

        # else:
        #     controller.media_widget = QtWidgets.QWidget(display)
        print("GMI")
        self.media_player = QMediaPlayer(None)
        self.audio_output = QAudioOutput()
        self.video_widget = QVideoWidget()
        self.media_player.errorOccurred.connect(self.error_event)
        self.media_player.durationChanged.connect(self.duration_changed_event)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setSource(QUrl.fromLocalFile(str(media_file)))
        print("h1", self.media_player.error())
        self.media_player.play()
        print("h2", self.media_player.error())

    def duration_changed_event(self, duration: int):
        print("DD", duration)

    def error_event(self, error_text) -> None:
        print("Error ", error_text)



