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
The :mod:`~openlp.core.ui.media.mediacontroller` module is the control module for all media playing.
"""
import logging
from pathlib import Path
from typing import Union

try:
    from pymediainfo import MediaInfo, __version__ as pymediainfo_version

    pymediainfo_available = True
except ImportError:
    pymediainfo_available = False
    pymediainfo_version = "0.0"

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.display.window import DisplayWindow
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box, warning_message_box
from openlp.core.state import State, MessageType
from openlp.core.ui import DisplayControllerType, HideMode
from openlp.core.ui.slidecontroller import SlideController
from openlp.core.ui.media import MediaState, MediaPlayItem, MediaType, format_play_seconds, media_empty_song, \
    format_play_time, parse_stream_path, get_volume, toggle_looping_playback, saved_looping_playback, save_volume
from openlp.core.ui.media.remote import register_views
from openlp.core.ui.media.mediainfo import media_info
from openlp.core.ui.media.audioplayer import AudioPlayer
from openlp.core.ui.media.mediaplayer import MediaPlayer

log = logging.getLogger(__name__)

HIDE_DELAY_TIME = 2500


class MediaController(QtWidgets.QWidget, RegistryBase, LogMixin, RegistryProperties):
    """
    The implementation of the Media Controller which manages how media is played.
    """

    vlc_live_media_tick = QtCore.Signal()
    vlc_preview_media_tick = QtCore.Signal()
    vlc_live_media_stop = QtCore.Signal()
    vlc_preview_media_stop = QtCore.Signal()

    def __init__(self, parent=None):
        """ """
        super(MediaController, self).__init__(parent)
        self.log_info("MediaController Initialising")

    def setup(self):
        self.media_player = None
        self.audio_player = None
        # Timer for video state
        self.live_hide_timer = QtCore.QTimer()
        self.live_hide_timer.setSingleShot(True)
        self.live_kill_timer = QtCore.QTimer()
        self.live_kill_timer.setSingleShot(True)
        # Signals
        self.live_hide_timer.timeout.connect(self._on_media_hide_live)
        self.live_kill_timer.timeout.connect(self._on_media_kill_live)
        Registry().register_function("playbackPlay", self.media_play_msg)
        Registry().register_function("playbackPause", self.media_pause_msg)
        Registry().register_function("playbackStop", self.media_stop_msg)
        Registry().register_function("playbackLoop", self.media_loop_msg)
        Registry().register_function("seek_slider", self.media_seek_msg)
        Registry().register_function("volume_slider", self.media_volume_msg)
        Registry().register_function("media_hide", self.media_hide)
        Registry().register_function("media_blank", self.media_blank)
        Registry().register_function("media_unblank", self.media_unblank)
        # Signals for background video
        Registry().register_function("songs_hide", self.media_hide)
        Registry().register_function("songs_blank", self.media_blank)
        Registry().register_function("songs_unblank", self.media_unblank)
        register_views()

    def bootstrap_initialise(self):
        """
        Check to see if we have any media Player's available.
        """
        self.setup()
        State().add_service("mediacontroller", 0)
        State().add_service("media_live", 0)
        if pymediainfo_available:
            State().update_pre_conditions("mediacontroller", True)
            State().update_pre_conditions("media_live", True)
        else:
            if hasattr(self.main_window, "splash") and self.main_window.splash.isVisible():
                self.main_window.splash.hide()
            message = translate(
                "OpenLP.MediaController",
                "OpenLP requires the pymediainfo library in order to show videos and other "
                "media, but is are not installed. Please install this library to enable "
                "media playback in OpenLP.",
            )
            State().missing_text("media_live", message, MessageType.Error)

    def bootstrap_post_set_up(self):
        """
        Set up the controllers.
        :return:
        """
        if State().check_preconditions("mediacontroller"):
            try:
                self.vlc_live_media_tick.connect(self._media_state_live)
                self.vlc_preview_media_tick.connect(self._media_state_preview)
                self.vlc_live_media_stop.connect(self.live_media_stopped)
                self.vlc_preview_media_stop.connect(self.preview_media_stopped)
                self.setup_display(self.live_controller, False)
            except AttributeError:
                State().update_pre_conditions("media_live", False)
                State().missing_text(
                    "media_live",
                    translate(
                        "OpenLP.MediaController", "No Displays have been configured, " "so Live Media has been disabled"
                    ),
                )
            self.setup_display(self.preview_controller, True)

    def _display_controllers(self, controller_type: DisplayControllerType) -> SlideController:
        """
        Decides which controller to use.

        :param controller_type: The controller type where a player will be placed
        :return the correct Controller
        """
        if controller_type == DisplayControllerType.Live:
            return self.live_controller
        return self.preview_controller

    def _media_state_live(self) -> None:
        """
        In the running Live media Player and do some updating stuff (e.g. update the UI)
        """
        self.live_controller.media_player.resize()
        self.live_controller.media_player.update_ui()
        self.tick(self.live_controller)

    def _media_state_preview(self) -> None:
        """
        In the running Preview media Player and do updating stuff (e.g. update the UI)
        """
        self.preview_controller.media_player.resize()
        self.preview_controller.media_player.update_ui()
        self.tick(self.preview_controller)

    def live_media_stopped(self) -> None:
        """
        The live media has stopped
        """
        self.media_stop(self.live_controller)
        self.tick(self.live_controller)
        if (
            Registry().get("settings").value("media/live loop")
            or self.live_controller.media_play_item.is_theme_background
        ):
            self.has_started = False
            self.media_play(self.live_controller)

    def preview_media_stopped(self) -> None:
        """
        The Preview media has stopped
        """
        self.media_stop(self.preview_controller)
        self.tick(self.preview_controller)
        if (
            Registry().get("settings").value("media/preview loop")
            or self.preview_controller.media_play_item.is_theme_background
        ):
            self.has_started = False
            self.media_play(self.preview_controller)

    def setup_display(self, controller: SlideController, preview: bool) -> None:
        """
        After a new display is configured, all media related widgets will be created too
        :param controller:  Display on which the output is to be played
        # TODO
        :param preview:  Are we to preview
        """
        controller.media_play_item = MediaPlayItem()
        controller.media_player = MediaPlayer()
        controller.media_player.setup(controller, self._define_display(controller))
        controller.audio_player = AudioPlayer()
        controller.audio_player.setup(controller, self._define_display(controller))

    @staticmethod
    def set_controls_visible(controller: SlideController, value: bool) -> None:
        """
        After a new display is configured, all media related widget will be created too

        :param controller: The controller on which controls act.
        :param value: control name to be changed.
        """
        # Generic controls
        controller.mediabar.setVisible(value)

    @staticmethod
    def _resize(controller: SlideController) -> None:
        """
        After Mainwindow changes or Splitter moved all related media widgets have to be resized

        :param controller: The display on which output is playing.
        """
        controller.media_player.resize()

    def load_video(self, source, service_item, hidden: bool = False, is_theme_background: bool = False) -> bool:
        """
        Loads and starts a video to run and sets the stored sound value.

        :param source: Where the call originated form
        :param service_item: The player which is doing the playing

        :param hidden: The player which is doing the playing
        :param is_theme_background: Is the theme providing a background
        """
        controller = self._display_controllers(source)
        log.debug(f"load_video is_live:{controller.is_live}")
        # stop running videos
        self.media_reset(controller)
        print("A")
        controller.media_play_item.is_theme_background = is_theme_background
        controller.media_play_item.media_type = MediaType.Video
        controller.media_play_item.is_playing = MediaState.Loaded
        # background will always loop video.
        if service_item.is_capable(ItemCapabilities.HasBackgroundAudio):
            print("B")
            controller.media_play_item.audio_file = service_item.background_audio[0][0]
            controller.media_play_item.media_type = MediaType.Audio
            if controller.media_play_item.is_theme_background:
                print("B1")
                controller.media_play_item.media_type = MediaType.Dual
                controller.media_play_item.media_file = service_item.video_file_name           # is_background indicates we shouldn't override the normal display
                controller.media_play_item.is_background = True
        elif service_item.is_capable(ItemCapabilities.HasBackgroundStream):
            print("C")
            (stream_type, name, mrl, options) = parse_stream_path(service_item.stream_mrl)
            controller.media_play_item.external_stream = (mrl, options)
            controller.media_play_item.is_background = True
            controller.media_play_item.media_type = stream_type
        # TODO not set anywhere.
        elif service_item.is_capable(ItemCapabilities.HasBackgroundVideo):
            print("D")
            controller.media_play_item.media_file = service_item.video_file_name
            controller.media_play_item.is_background = True
        else:
            # I am a media file
            print("E")
            controller.media_play_item.media_file = service_item.get_frame_path()
            controller.media_play_item.is_background = False
        # TODO is this needed
        if service_item.is_capable(ItemCapabilities.CanStream):
            self.log_debug(f"video is stream  live={controller.is_live}")
            path = service_item.get_frames()[0]["path"]
            (stream_type, name, mrl, options) = parse_stream_path(path)
            controller.media_play_item.media_type = stream_type
            controller.media_play_item.external_stream = (mrl, options)
        else:
            self.log_debug(f"standard media, is not a stream, live={controller.is_live}")
            controller.media_play_item.length = service_item.media_length
            controller.media_play_item.start_time = service_item.start_time
            controller.media_play_item.timer = service_item.start_time
            controller.media_play_item.end_time = service_item.end_time
        is_valid = self._check_file_type_and_load(controller)
        if not is_valid:
            # Media could not be loaded correctly
            critical_error_message_box(
                translate("MediaPlugin.MediaItem", "Unsupported File"),
                translate("MediaPlugin.MediaItem", "Unable to load file - Unsupported File"),
            )
            return False
        self.log_debug("video media type: {tpe} ".format(tpe=str(controller.media_play_item.media_type)))
        # If both the preview and live view have a device stream, make sure only the live view continues streaming
        if controller.media_play_item.media_type == MediaType.DeviceStream:
            if controller.is_live:
                if self.preview_controller.media_play_item.media_type == MediaType.DeviceStream:
                    self.log_warning("stream can only be displayed in one instance, killing preview stream")
                    warning_message_box(
                        translate("MediaPlugin.MediaItem", "Unable to Preview Stream"),
                        translate("MediaPlugin.MediaItem", "Closing Preview to allow Live Stream"),
                    )
                    self.preview_controller.on_media_close()
            else:
                if self.live_controller.media_play_item.media_type == MediaType.DeviceStream:
                    self.log_warning("stream cannot be previewed while also streaming live")
                    warning_message_box(
                        translate("MediaPlugin.MediaItem", "Unable to Preview Stream "),
                        translate("MediaPlugin.MediaItem", "Unable to preview when live is currently streaming"),
                    )

                    return False
        self._media_bar(controller, "load")
        if self.decide_autoplay(service_item, controller, hidden):
            start_hidden = (
                controller.media_play_item.is_theme_background
                and controller.is_live
                and (controller.current_hide_mode == HideMode.Blank or controller.current_hide_mode == HideMode.Screen)
            )
            if not self.media_play(controller, start_hidden):
                critical_error_message_box(
                    translate("MediaPlugin.MediaItem", "Unsupported File"),
                    translate("MediaPlugin.MediaItem", "Unsupported File - unable to play"),
                )
                return False
        self._update_seek_ui(controller)
        self.set_controls_visible(controller, True)
        return True

    def decide_autoplay(self, service_item, controller, hidden: bool) -> bool:
        """
        Function to decide if we can / want to autoplay a media item

        :param service_item: The Media Service item
        :param controller: The controller on which the item is to be played
        :param hidden: is the display hidden at present?
        :return: Can we autoplay the media.
        """
        if not controller.is_live:
            return True
        is_autoplay = False
        # Visible or background requested or Service Item wants background media
        if service_item.requires_media() and hidden == HideMode.Theme:
            is_autoplay = True
        elif not hidden and (service_item.will_auto_start or
                             self.settings.value("media/media auto start") == QtCore.Qt.CheckState.Checked):
            is_autoplay = True
        # Unblank on load set
        elif self.settings.value("core/auto unblank"):
            is_autoplay = True
        if controller.media_play_item.is_theme_background:
            is_autoplay = True
        if controller.media_play_item.media_type in [MediaType.DeviceStream, MediaType.NetworkStream]:
            is_autoplay = True
        return is_autoplay

    @staticmethod
    def media_length(media_path: Union[str, Path]) -> int:
        """
        Uses Media Info to obtain the media length

        :param media_path: The file path to be checked..
        """
        media_info().get_media_info(str(media_path))
        if MediaInfo.can_parse():
            if pymediainfo_version < "4.3":
                # pymediainfo only introduced file objects in 4.3, so if this is an older version, we'll have to use
                # the old method. See https://gitlab.com/openlp/openlp/-/issues/1187
                media_data = MediaInfo.parse(str(media_path))
            else:
                # pymediainfo has an issue opening non-ascii file names, so pass it a file object instead
                # See https://gitlab.com/openlp/openlp/-/issues/1041
                with Path(media_path).open("rb") as media_file:
                    media_data = MediaInfo.parse(media_file)
                # duration returns in milli seconds
            duration = media_data.tracks[0].duration
            # It appears that sometimes we get a string. Let's try to interpret that as int, or fall back to 0
            # See https://gitlab.com/openlp/openlp/-/issues/1387
            print(duration)
            if isinstance(duration, str):
                if duration.strip().isdigit():
                    duration = int(duration.strip())
                else:
                    duration = 0
            return duration or 0
        return 0

    def _check_file_type_and_load(self, controller: SlideController) -> bool:
        """
        Select the correct media Player type from the prioritized Player list

        :param controller: First element is the controller which should be used
        :return boolean: Sucess or Failure to load the file(s)
        """
        if controller.media_play_item.media_type in [MediaType.DeviceStream, MediaType.NetworkStream]:
            self._resize(controller)
            if controller.media_player.load_stream():
                return True
            return False
        loaded_m = True
        loaded_a = True
        if controller.media_play_item.media_file:
            print("F1")
            loaded_m = controller.media_player.load()
            if loaded_m:
                self._resize(controller)
        if controller.media_play_item.audio_file:
            print("F2")
            loaded_a = controller.audio_player.load()
        if loaded_a is True and loaded_m is True:
            return True
        return False

    def media_play_msg(self, msg: list):
        """
        Responds to the request to play a loaded video

        :param msg: First element is the controller which should be used
        :param status:
        """
        return self.media_play(msg[0])

    def on_media_play(self):
        """
        Responds to the request to play a loaded video from the web.
        """
        return self.media_play(self.live_controller)

    def media_play(self, controller: SlideController, start_hidden=False):
        """
        Responds to the request to play a loaded video

        :param controller: The controller to be played
        :param start_hidden: Whether to play the video without showing the controller
        """
        self.log_debug(f"media_play is_live:{controller.is_live}")
        controller.mediabar.seek_slider.blockSignals(True)
        controller.mediabar.volume_slider.blockSignals(True)
        display = self._define_display(controller)
        if controller.audio_player and controller.media_play_item.audio_file:
            print("G1")
            controller.audio_player.play()
        if controller.media_player and controller.media_play_item.media_file:
            print("G2")
            controller.media_player.play()
        # TODO to be tested my need a different play function
        if controller.media_player and controller.media_play_item.external_stream:
            controller.media_player.play()
        self.media_volume(controller, get_volume(controller))
        if not start_hidden:
            self._media_set_visibility(controller, True)
        self._media_bar(controller, "play")
        # Start Timer for ui updates
        controller.mediabar.seek_slider.blockSignals(False)
        controller.mediabar.volume_slider.blockSignals(False)
        controller.media_play_item.is_playing = MediaState.Playing
        if not controller.media_play_item.is_background:
            display = self._define_display(controller)
            if controller.is_live:
                controller.set_hide_mode(None)
                display.hide_display(HideMode.Screen)
            controller._set_theme(controller.service_item)
            # display.load_verses(media_empty_song)
        controller.output_has_changed()
        return True

    def tick(self, controller) -> None:
        """
        Add a tick while the media is playing but only count if not paused

        :param controller:  The Controller to be processed
        :return:            Is the video still running?
        """
        controller.media_play_item.timer = controller.media_player.get_time()
        self._update_seek_ui(controller)

    def _media_bar(self, controller: SlideController, mode: str) -> None:
        """
        Set the media bar state depending on the function called.
        :param controller: The controller being updated
        :param mode: The mode the code is being called from
        :return: None
        """
        controller.mediabar.blockSignals(True)
        if controller.media_play_item.is_theme_background:
            loop_set = False
            loop_disabled = True
            controller.media_player.toggle_loop(True)
        else:
            loop_set = saved_looping_playback(controller)
            loop_disabled = False
            controller.media_player.toggle_loop(loop_set)
        controller.mediabar.seek_slider.setTickInterval(controller.media_play_item.length // 10)
        controller.mediabar.seek_slider.setMaximum(controller.media_play_item.length)
        if mode == "load":
            controller.mediabar.actions["playbackPlay"].setDisabled(False)
            controller.mediabar.actions["playbackPause"].setDisabled(True)
            controller.mediabar.actions["playbackStop"].setDisabled(True)
            controller.mediabar.actions["playbackLoop"].setChecked(loop_set)
            controller.mediabar.actions["playbackLoop"].setDisabled(loop_disabled)
        if mode == "play":
            controller.mediabar.actions["playbackPlay"].setDisabled(True)
            controller.mediabar.actions["playbackPause"].setDisabled(False)
            controller.mediabar.actions["playbackStop"].setDisabled(False)
            controller.mediabar.actions["playbackLoop"].setChecked(loop_set)
            controller.mediabar.actions["playbackLoop"].setDisabled(loop_disabled)
        if mode == "pause" or mode == "stop" or mode == "reset":
            controller.mediabar.actions["playbackPlay"].setDisabled(False)
            controller.mediabar.actions["playbackPause"].setDisabled(True)
            controller.mediabar.actions["playbackStop"].setDisabled(False)
        if mode == "stop" or mode == "reset":
            controller.mediabar.actions["playbackLoop"].setChecked(loop_set)
            controller.mediabar.actions["playbackLoop"].setDisabled(loop_disabled)
        controller.mediabar.blockSignals(False)

    @staticmethod
    def _update_seek_ui(controller: SlideController) -> None:
        """
        Update the media toolbar display after changes to sliders

        :param controller: the slidecontroller to be updated
        """
        controller.mediabar.position_label.setText(f"{format_play_time(controller.media_play_item.timer)}/"
                                                   f"{format_play_time(controller.media_play_item.length)}")

    def media_pause_msg(self, msg: list):
        """
        Responds to the request to pause a loaded video

        :param msg: First element is the controller which should be used
        :return bool
        """
        return self.media_pause(msg[0])

    def on_media_pause(self) -> True:
        """
        Responds to the request to pause a loaded video from the web.
        :return bool
        """
        return self.media_pause(self.live_controller)

    def media_pause(self, controller: SlideController) -> True:
        """
        Responds to the request to pause a loaded video

        :param controller: The Controller to be paused
        :return bool
        """
        self.log_debug(f"media_stop is_live:{controller.is_live}")
        if controller.audio_player and controller.media_play_item.audio_file:
            controller.audio_player.pause()
        if controller.media_player and controller.media_play_item.media_file:
            controller.media_player.pause()
        self._media_bar(controller, "pause")
        controller.media_play_item.is_playing = MediaState.Paused
        # Add a tick to the timer to prevent it finishing the video before it can loop back or stop
        # If the clip finishes, we hit a bug where we cannot start the video
        controller.media_play_item.timer = controller.media_player.get_time()
        controller.output_has_changed()
        return True

    def media_loop_msg(self, msg: list):
        """
        Responds to the request to loop a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_loop(msg[0])

    def media_loop(self, controller: SlideController):
        """
        Responds to the request to loop a loaded video

        :param controller: The controller that needs to be stopped
        """
        toggle_looping_playback(controller)
        controller.media_player.toggle_loop(saved_looping_playback(controller))
        controller.mediabar.actions["playbackLoop"].setChecked(saved_looping_playback(controller))

    def media_stop_msg(self, msg: list):
        """
        Responds to the request to stop a loaded video

        :param msg: First element is the controller which should be used
        """
        return self.media_stop(msg[0])

    def on_media_stop(self):
        """
        Responds to the request to stop a loaded video from the web.
        """
        return self.media_stop(self.live_controller)

    def media_stop(self, controller: SlideController) -> bool:
        """
        Responds to the request to stop a loaded video

        :param controller: The controller that needs to be stopped
        """
        self.log_debug(f"media_stop is_live:{controller.is_live}")
        if controller.audio_player and controller.media_play_item.audio_file:
            controller.audio_player.stop()
        if controller.media_player and controller.media_play_item.media_file:
            controller.media_player.stop()
        if controller.is_live:
            self.live_hide_timer.start(HIDE_DELAY_TIME)
            if not controller.media_play_item.is_background:
                display = self._define_display(controller)
                if display.hide_mode == HideMode.Screen:
                    Registry().execute("live_display_hide", HideMode.Blank)
                else:
                    controller.set_hide_mode(display.hide_mode or HideMode.Blank)
        else:
            self._media_set_visibility(controller, False)
        self._media_bar(controller, "stop")
        controller.media_play_item.is_playing = MediaState.Stopped
        controller.media_play_item.timer = controller.media_play_item.start_time
        controller.mediabar.seek_slider.setSliderPosition(controller.media_play_item.start_time)
        self._update_seek_ui(controller)
        controller.output_has_changed()
        return True

    def media_volume_msg(self, msg: list):
        """
        Changes the volume of a running video

        :param msg: First element is the controller which should be used
        """
        controller = msg[0]
        vol = msg[1][0]
        self.media_volume(controller, vol)

    def media_volume(self, controller: SlideController, volume: int):
        """
        Changes the volume of a running video

        :param controller: The Controller to use
        :param volume: The volume to be set
        """
        self.log_debug(f"media_volume {volume}")
        save_volume(controller, volume)
        if controller.media_play_item.media_type == MediaType.Dual:
            controller.media_player.volume(0)
            controller.audio_player.volume(volume)
        else:
            controller.media_player.volume(volume)
        controller.mediabar.volume_slider.setValue(volume)
        controller.mediabar.volume_label.setText(f"{format_play_seconds(volume)}")

    def media_seek_msg(self, msg: list):
        """
        Responds to the request to change the seek Slider of a loaded video via a message

        :param msg: First element is the controller which should be used
            Second element is a list with the seek value as first element
        """
        controller = msg[0]
        seek_value = msg[1][0]
        self.media_seek(controller, seek_value)

    def media_seek(self, controller: SlideController, seek_value):
        """
        Responds to the request to change the seek Slider of a loaded video

        :param controller: The controller to use.
        :param seek_value: The value to set.
        """
        if controller.media_play_item.media_type == MediaType.Dual:
            controller.audio_player.seek(seek_value)
        else:
            controller.media_player.seek(seek_value)
        controller.media_play_item.timer = seek_value
        self._update_seek_ui(controller)

    def media_reset(self, controller: SlideController, delayed: bool = False) -> None:
        """
        Responds to the request to reset a loaded video
        :param controller: The controller to use.
        :param delayed: Should the controller briefly remain visible.
        """
        self.log_debug("media_reset")
        self.set_controls_visible(controller, False)
        controller.media_player.reset()
        if controller.is_live and delayed:
            self.live_kill_timer.start(HIDE_DELAY_TIME)
        else:
            if controller.is_live:
                self.live_kill_timer.stop()
            else:
                self._media_set_visibility(controller, False)
            controller.media_play_item = MediaPlayItem()
            controller.media_play_item.is_theme_background = False
        self._media_bar(controller, "reset")

    def media_hide_msg(self, msg: list):
        """
        Hide the related video Widget

        :param msg: First element is the boolean for Live indication
        """
        is_live = msg[1]
        self.media_hide(is_live)

    def media_hide(self, is_live, delayed=False):
        """
        Pause and hide the related video Widget if is_live

        :param is_live: Live indication
        :param delayed: Should the controller briefly remain visible.
        """
        self.log_debug(f"media_hide is_live:{is_live}")
        if not is_live or self.live_kill_timer.isActive():
            return
        if self.live_controller.media_play_item.is_playing == MediaState.Playing:
            if delayed:
                self.live_hide_timer.start(HIDE_DELAY_TIME)
            else:
                self.media_pause(self.live_controller)
                self._media_set_visibility(self.live_controller, False)

    def _on_media_hide_live(self):
        """
        Local function to hide the live media
        """
        self.media_pause(self.live_controller)
        self._media_set_visibility(self.live_controller, False)

    def _on_media_kill_live(self):
        """
        Local function to kill the live media
        """
        self._media_set_visibility(self.live_controller, False)

    def _media_set_visibility(self, controller: SlideController, visible):
        """
        Set the live video Widget visibility
        """
        if controller.is_live:
            self.live_hide_timer.stop()
        visible = visible and controller.media_play_item.media_type is not MediaType.Audio
        controller.media_player.set_visible(visible)
        if controller.is_live and visible:
            display = self._define_display(controller)
            display.raise_()

    def media_blank(self, msg: list):
        """
        Blank the related video Widget

        :param msg: First element is the boolean for Live indication
            Second element is the hide mode
        """
        is_live = msg[1]
        hide_mode = msg[2]
        self.log_debug(f"media_blank is_live:{is_live}")
        if not is_live:
            return
        if self.live_kill_timer.isActive():
            # If pressing blank when the video is being removed, remove it instantly
            self._media_set_visibility(self.live_controller, False)
            self.media_reset(self.live_controller)
            return
        if not self.live_controller.media_play_item.is_background:
            Registry().execute("live_display_hide", hide_mode)
        playing = self.live_controller.media_play_item.is_playing == MediaState.Playing
        if self.live_controller.media_play_item.is_theme_background and hide_mode == HideMode.Theme:
            if not playing:
                self.media_play(self.live_controller)
            else:
                self.live_hide_timer.stop()
        else:
            if playing and not self.live_controller.media_play_item.is_theme_background:
                self.media_pause(self.live_controller)
            self._media_set_visibility(self.live_controller, False)

    def media_unblank(self, msg: list):
        """
        Unblank the related video Widget

        :param msg: First element is not relevant in this context
            Second element is the boolean for Live indication
        """
        is_live = msg[1]
        self.log_debug(f"media_blank is_live:{is_live}")
        if not is_live or self.live_kill_timer.isActive():
            return
        Registry().execute("live_display_show")
        if self.live_controller.media_play_item.is_playing != MediaState.Playing:
            self.media_play(self.live_controller)
        else:
            self._media_set_visibility(self.live_controller, True)
            if not self.live_controller.media_play_item.is_background:
                display = self._define_display(self.live_controller)
                display.hide_display(HideMode.Screen)

    def finalise(self):
        """
        Reset all the media controllers when OpenLP shuts down
        """
        self.live_hide_timer.stop()
        self.live_kill_timer.stop()
        self.media_reset(self._display_controllers(DisplayControllerType.Live))
        self.media_reset(self._display_controllers(DisplayControllerType.Preview))

    @staticmethod
    def _define_display(controller: SlideController) -> DisplayWindow:
        """
        Extract the correct display for a given controller

        :param controller:  Controller to be used
        :return correct display window
        """
        if controller.is_live:
            return controller.display
        return controller.preview_display
