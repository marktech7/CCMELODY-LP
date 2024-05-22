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
The :mod:`~openlp.core.ui.media.mediaplayer` module for media playing.
"""
import logging

from PySide6 import QtCore, QtWidgets

from openlp.core.common.mixins import LogMixin
from openlp.core.common.registry import Registry
from openlp.core.display.window import DisplayWindow
from openlp.core.ui.slidecontroller import SlideController
from openlp.core.ui.media.mediabase import MediaBase

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from PySide6.QtCore import QUrl

log = logging.getLogger(__name__)


class MediaPlayer(MediaBase, LogMixin):
    """
    A specialised version of the MediaPlayer class, which provides an media player for media when the main media class
    is also in use.
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(MediaPlayer, self).__init__(parent, "qt6")
        self.parent = parent

    def setup(self, controller: SlideController, display: DisplayWindow) -> None:
        """
        Set up an audio player andbind it to a controller and display

        :param controller: The controller where the media is
        :param display: The display where the media is.
        :return:
        """
        if controller.is_live:
            controller.media_widget = QtWidgets.QWidget(controller)
            controller.media_widget.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint
                | QtCore.Qt.WindowType.Tool
                | QtCore.Qt.WindowType.WindowStaysOnTopHint)
            controller.media_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_X11NetWmWindowTypeDialog)

        else:
            controller.media_widget = QtWidgets.QWidget(display)
        self.media_player = QMediaPlayer(None)
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        layout = QtWidgets.QVBoxLayout(controller.media_widget)
        layout.addWidget(self.video_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.controller = controller
        self.display = display
        self.media_player.positionChanged.connect(self.pos_callback)

    def pos_callback(self, position) -> None:
        """
        A Tick event triggered by VLC
        :param event: The VLC Event triggered
        :param controller: The controller upon which the event occurs
        :return: None
        """
        self.controller.media_play_item.timer = position
        if self.controller.is_live:
            Registry().get("media_controller").vlc_live_media_tick.emit()
        else:
            Registry().get("media_controller").vlc_preview_media_tick.emit()

    def toggle_loop(self, loop_required: bool) -> None:
        """
        Switch the loop toggle setting

        :param loop_required: Do I need to loop
        """
        if loop_required:
            self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
        else:
            self.media_player.setLoops(QMediaPlayer.Loops.Once)

    def check_available(self):
        """
        Return the availability of VLC
        """
        return True

    def load(self) -> bool:
        """
        Load a media file into the player

        :return:  Success or Failure
        """
        self.log_debug("load external media stream in Media Player")
        if self.controller.media_play_item.media_file:
            self.media_player.setSource(QUrl.fromLocalFile(str(self.controller.media_play_item.media_file)))
            return True
        return False

    def load_stream(self) -> bool:
        """
        Load a media stream into the player
        :return:  Success or Failure
        """
        self.log_debug("load stream  in Media Player")
        # TODO sort out when we have the input sorted
        # aa = QMediaDevices.videoInputs()
        # for a in aa:
        #     print(a)
        #     print(a.id())
        #     print(a.description())
        #     print(a.description() == "Chicony USB2.0 Camera: Chicony")
        #     print("Chicony USB2.0 Camera: Chicony" in a.description())

        # mediaCaptureSession = QMediaCaptureSession()
        # mediaCaptureSession.setCamera(camera)
        # mediaCaptureSession.setVideoOutput(video_widget)

        if self.controller.media_play_item.external_stream:
            self.media_player.setSource(QUrl.fromLocalFile(str(self.controller.media_play_item.media_file)))
            return True
        return False

    def play(self) -> None:
        """
        Play the current loaded audio item
        :return:
        """
        self.media_player.play()

    def pause(self) -> None:
        """
        Pause the current item

        :param controller: The controller which is managing the display
        :return:
        """
        self.media_player.pause()

    def stop(self) -> None:
        """
        Stop the current item

        :param controller: The controller where the media is
        :return:
        """
        self.media_player.stop()

    def duration(self) -> int:
        """
        """
        return self.media_player.duration()
