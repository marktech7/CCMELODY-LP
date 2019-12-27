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
"""
The :mod:`~openlp.core.ui.media.mediacontroller` module is the control module for all media playing.
"""
import logging

try:
    from pymediainfo import MediaInfo
    pymediainfo_available = True
except ImportError:
    pymediainfo_available = False

from subprocess import check_output
from PyQt5 import QtCore

from openlp.core.state import State
from openlp.core.api.http import register_endpoint
from openlp.core.common import is_linux, is_macosx
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui import DisplayControllerType
from openlp.core.ui.media import MediaState, ItemMediaInfo, MediaType, parse_optical_path, VIDEO_EXT, AUDIO_EXT
from openlp.core.ui.media.endpoint import media_endpoint
from openlp.core.ui.media.vlcplayer import VlcPlayer, get_vlc


log = logging.getLogger(__name__)

TICK_TIME = 200


class MediaController(RegistryBase, LogMixin, RegistryProperties):
    """
    The implementation of the Media Controller which manages how media is played.
    """

    def setup(self):
        self.vlc_player = None
        self.current_media_players = {}
        # Timer for video state
        self.live_timer = QtCore.QTimer()
        self.live_timer.setInterval(TICK_TIME)
        self.preview_timer = QtCore.QTimer()
        self.preview_timer.setInterval(TICK_TIME)
        # Signals
        self.live_timer.timeout.connect(self.media_state_live)
        self.preview_timer.timeout.connect(self.media_state_preview)
        Registry().register_function('playbackPlay', self.media_play_msg)
        Registry().register_function('playbackPause', self.media_pause_msg)
        Registry().register_function('playbackStop', self.media_stop_msg)
        Registry().register_function('playbackLoop', self.media_loop_msg)
        Registry().register_function('seek_slider', self.media_seek_msg)
        Registry().register_function('volume_slider', self.media_volume_msg)
        Registry().register_function('media_hide', self.media_hide)
        Registry().register_function('media_blank', self.media_blank)
        Registry().register_function('media_unblank', self.media_unblank)
        # Signals for background video
        Registry().register_function('songs_hide', self.media_hide)
        Registry().register_function('songs_blank', self.media_blank)
        Registry().register_function('songs_unblank', self.media_unblank)
        register_endpoint(media_endpoint)

    def bootstrap_initialise(self):
        """
        Check to see if we have any media Player's available.
        """
        self.setup()
        self.vlc_player = VlcPlayer(self)
        State().add_service('mediacontroller', 0)
        State().add_service('media_live', 0)
        has_vlc = get_vlc()
        if has_vlc and pymediainfo_available:
            State().update_pre_conditions('mediacontroller', True)
            State().update_pre_conditions('media_live', True)
        else:
            if hasattr(self.main_window, 'splash') and self.main_window.splash.isVisible():
                self.main_window.splash.hide()
            generic_message = translate('OpenLP.MediaController',
                                        'OpenLP requires the following libraries in order to show videos and other '
                                        'media, but they are not installed. Please install these libraries to enable '
                                        'media playback in OpenLP.')
            fedora_rpmfusion = translate('OpenLP.MediaController',
                                         'To install these libraries, you will need to enable the RPMFusion '
                                         'repository: https://rpmfusion.org/')
            if is_macosx():
                message = translate('OpenLP.MediaController',
                                    'macOS is missing VLC. Please download and install from the VLC web site: '
                                    'https://www.videolan.org/vlc/')
            else:
                packages = []
                if not has_vlc:
                    packages.append('python3-vlc')
                if not pymediainfo_available:
                    packages.append('python3-pymediainfo')
                message = generic_message + '\n\n' + ', '.join(packages)
                if not has_vlc and is_linux(distro='fedora'):
                    message += '\n\n' + fedora_rpmfusion
            State().missing_text('media_live', message)
        return True

    def bootstrap_post_set_up(self):
        """
        Set up the controllers.
        :return:
        """
        if State().check_preconditions('mediacontroller'):
            try:
                self.setup_display(self.live_controller, False)
            except AttributeError:
                State().update_pre_conditions('media_live', False)
                State().missing_text('media_live', translate(
                    'OpenLP.MediaController', 'No Displays have been configured, so Live Media has been disabled'))
            self.setup_display(self.preview_controller, True)

    def display_controllers(self, controller_type):
        """
        Decides which controller to use.

        :param controller_type: The controller type where a player will be placed
        """
        if controller_type == DisplayControllerType.Live:
            return self.live_controller
        return self.preview_controller

    def media_state_live(self):
        """
        Check if there is a running Live media Player and do updating stuff (e.g. update the UI)
        """
        display = self._define_display(self.display_controllers(DisplayControllerType.Live))
        if DisplayControllerType.Live in self.current_media_players:
            self.current_media_players[DisplayControllerType.Live].resize(self.live_controller)
            self.current_media_players[DisplayControllerType.Live].update_ui(self.live_controller, display)
            self.tick(self.display_controllers(DisplayControllerType.Live))
            if self.current_media_players[DisplayControllerType.Live].get_live_state() is not MediaState.Playing:
                self.live_timer.stop()
        else:
            self.live_timer.stop()
            self.media_stop(self.display_controllers(DisplayControllerType.Live))

    def media_state_preview(self):
        """
        Check if there is a running Preview media Player and do updating stuff (e.g. update the UI)
        """
        display = self._define_display(self.display_controllers(DisplayControllerType.Preview))
        if DisplayControllerType.Preview in self.current_media_players:
            self.current_media_players[DisplayControllerType.Preview].resize(self.live_controller)
            self.current_media_players[DisplayControllerType.Preview].update_ui(self.preview_controller, display)
            self.tick(self.display_controllers(DisplayControllerType.Preview))
            if self.current_media_players[DisplayControllerType.Preview].get_preview_state() is not MediaState.Playing:
                self.preview_timer.stop()
        else:
            self.preview_timer.stop()
            self.media_stop(self.display_controllers(DisplayControllerType.Preview))

    def setup_display(self, controller, preview):
        """
        After a new display is configured, all media related widgets will be created too

        :param controller:  Display on which the output is to be played
        :param preview: Whether the display is a main or preview display
        """
        controller.media_info = ItemMediaInfo()
        controller.has_audio = True
        if preview:
            controller.has_audio = False
        self.vlc_player.setup(controller, self._define_display(controller), preview)

    @staticmethod
    def set_controls_visible(controller, value):
        """
        After a new display is configured, all media related widget will be created too

        :param controller: The controller on which controls act.
        :param value: control name to be changed.
        """
        # Generic controls
        controller.mediabar.setVisible(value)

    @staticmethod
    def resize(controller, player):
        """
        After Mainwindow changes or Splitter moved all related media widgets have to be resized

        :param controller: The display on which output is playing.
        :param player:  The player which is doing the playing.
        """
        player.resize(controller)

    def load_video(self, source, service_item, hidden=False):
        """
        Loads and starts a video to run and sets the stored sound value.

        :param source: Where the call originated form
        :param service_item: The player which is doing the playing
        :param hidden: The player which is doing the playing
        """
        is_valid = True
        controller = self.display_controllers(source)
        # stop running videos
        self.media_reset(controller)
        controller.media_info = ItemMediaInfo()
        if controller.is_live:
            controller.media_info.volume = self.settings.value('media/live volume')
        else:
            controller.media_info.volume = self.settings.value('media/preview volume')
        # background will always loop video.
        if service_item.is_capable(ItemCapabilities.HasBackgroundAudio):
            controller.media_info.file_info = service_item.background_audio
        else:
            controller.media_info.file_info = [service_item.get_frame_path()]
        display = self._define_display(controller)
        if controller.is_live:
            # if this is an optical device use special handling
            if service_item.is_capable(ItemCapabilities.CanStream):
                is_valid = self._check_file_type(controller, display, True)
                controller.media_info.media_type = MediaType.Stream
            elif service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and live')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and live')
                controller.media_info.length = service_item.media_length
                is_valid = self._check_file_type(controller, display)
            controller.media_info.start_time = service_item.start_time
            controller.media_info.end_time = service_item.end_time
        elif controller.preview_display:
            if service_item.is_capable(ItemCapabilities.CanStream):
                controller.media_info.media_type = MediaType.Stream
                is_valid = self._check_file_type(controller, display, True)
            elif service_item.is_capable(ItemCapabilities.IsOptical):
                log.debug('video is optical and preview')
                path = service_item.get_frame_path()
                (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path)
                is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                    controller)
            else:
                log.debug('video is not optical and preview')
                controller.media_info.length = service_item.media_length
                is_valid = self._check_file_type(controller, display)
        if not is_valid:
            # Media could not be loaded correctly
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        log.debug('video media type: {tpe} '.format(tpe=str(controller.media_info.media_type)))
        autoplay = False
        if service_item.is_capable(ItemCapabilities.CanStream):
            autoplay = True
        # Preview requested
        if not controller.is_live:
            autoplay = True
        # Visible or background requested or Service Item wants to autostart
        elif not hidden or service_item.will_auto_start:
            autoplay = True
        # Unblank on load set
        elif self.settings.value('core/auto unblank'):
            autoplay = True
        if autoplay:
            if not self.media_play(controller):
                critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                           translate('MediaPlugin.MediaItem', 'Unsupported File'))
                return False
        self.set_controls_visible(controller, True)
        log.debug('use {nm} controller'.format(nm=self.current_media_players[controller.controller_type].display_name))
        return True

    @staticmethod
    def media_length(media_path):
        """
        Uses Media Info to obtain the media length

        :param media_path: The file path to be checked..
        """
        if MediaInfo.can_parse():
            media_data = MediaInfo.parse(media_path)
        else:
            xml = check_output(['mediainfo', '-f', '--Output=XML', '--Inform=OLDXML', media_path])
            if not xml.startswith(b'<?xml'):
                xml = check_output(['mediainfo', '-f', '--Output=XML', media_path])
            media_data = MediaInfo(xml.decode("utf-8"))
        # duration returns in milli seconds
        return media_data.tracks[0].duration

    def media_setup_optical(self, filename, title, audio_track, subtitle_track, start, end, display, controller):
        """
        Setup playback of optical media

        :param filename: Path of the optical device/drive.
        :param title: The main/title track to play.
        :param audio_track: The audio track to play.
        :param subtitle_track: The subtitle track to play.
        :param start: Start position in milliseconds.
        :param end: End position in milliseconds.
        :param display: The display to play the media.
        :param controller: The media controller.
        :return: True if setup succeeded else False.
        """
        # stop running videos
        self.media_reset(controller)
        # Setup media info
        controller.media_info = ItemMediaInfo()
        controller.media_info.file_info = QtCore.QFileInfo(filename)
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        controller.media_info.start_time = start
        controller.media_info.end_time = end
        controller.media_info.length = (end - start)
        controller.media_info.title_track = title
        controller.media_info.audio_track = audio_track
        controller.media_info.subtitle_track = subtitle_track
        # When called from mediaitem display is None
        if display is None:
            display = controller.preview_display
        self.vlc_player.load(display, filename)
        self.resize(controller, self.vlc_player)
        self.current_media_players[controller.controller_type] = self.vlc_player
        if audio_track == -1 and subtitle_track == -1:
            controller.media_info.media_type = MediaType.CD
        else:
            controller.media_info.media_type = MediaType.DVD
        return True

    def _check_file_type(self, controller, display, stream=False):
        """
        Select the correct media Player type from the prioritized Player list

        :param controller: First element is the controller which should be used
        :param display: Which display to use
        :param stream: Are we streaming or not
        """
        if stream:
            self.resize(controller, self.vlc_player)
            controller.media_info.media_type = MediaType.Stream
            if self.vlc_player.load(controller, display, None):
                self.current_media_players[controller.controller_type] = self.vlc_player
                return True
            return True
        for file in controller.media_info.file_info:
            if file.is_file:
                suffix = '*%s' % file.suffix.lower()
                file = str(file)
                if suffix in VIDEO_EXT:
                    self.resize(controller, self.vlc_player)
                    if self.vlc_player.load(controller, display, file):
                        self.current_media_players[controller.controller_type] = self.vlc_player
                        controller.media_info.media_type = MediaType.Video
                        return True
                if suffix in AUDIO_EXT:
                    if self.vlc_player.load(controller, display, file):
                        self.current_media_players[controller.controller_type] = self.vlc_player
                        controller.media_info.media_type = MediaType.Audio
                        return True
            else:
                file = str(file)
                if self.vlc_player.can_folder:
                    self.resize(controller, self.vlc_player)
                    if self.vlc_player.load(controller, display, file):
                        self.current_media_players[controller.controller_type] = self.vlc_player
                        controller.media_info.media_type = MediaType.Video
                        return True
        return False

    def media_play_msg(self, msg, status=True):
        """
        Responds to the request to play a loaded video

        :param msg: First element is the controller which should be used
        :param status:
        """
        self.media_play(msg[0], status)

    def on_media_play(self):
        """
        Responds to the request to play a loaded video from the web.
        """
        self.media_play(Registry().get('live_controller'), False)

    def media_play(self, controller, first_time=True):
        """
        Responds to the request to play a loaded video

        :param controller: The controller to be played
        :param first_time:
        """
        controller.seek_slider.blockSignals(True)
        controller.volume_slider.blockSignals(True)
        display = self._define_display(controller)
        if not self.current_media_players[controller.controller_type].play(controller, display):
            controller.seek_slider.blockSignals(False)
            controller.volume_slider.blockSignals(False)
            return False
        self.media_volume(controller, controller.media_info.volume)
        if first_time:
            self.current_media_players[controller.controller_type].set_visible(controller, True)
            controller.mediabar.actions['playbackPlay'].setVisible(False)
            controller.mediabar.actions['playbackPause'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(False)
        if controller.is_live:
            if controller.hide_menu.defaultAction().isChecked():
                controller.hide_menu.defaultAction().trigger()
            # Start Timer for ui updates
            if not self.live_timer.isActive():
                self.live_timer.start()
        else:
            # Start Timer for ui updates
            if not self.preview_timer.isActive():
                self.preview_timer.start()
        controller.seek_slider.blockSignals(False)
        controller.volume_slider.blockSignals(False)
        controller.media_info.is_playing = True
        display = self._define_display(controller)
        if controller.is_live:
            display.setVisible(False)
            # controller.preview_display.hide()
        else:
            display.setVisible(True)
        return True

    def tick(self, controller):
        """
        Add a tick while the media is playing but only count if not paused

        :param controller:  The Controller to be processed
        """
        start_again = False
        if controller.media_info.is_playing and controller.media_info.length > 0:
            if controller.media_info.timer > controller.media_info.length:
                self.media_stop(controller)
                if controller.media_info.is_looping_playback:
                    start_again = True
            controller.media_info.timer += TICK_TIME
            seconds = controller.media_info.timer // 1000
            minutes = seconds // 60
            seconds %= 60
            total_seconds = controller.media_info.length // 1000
            total_minutes = total_seconds // 60
            total_seconds %= 60
            controller.position_label.setText(' %02d:%02d / %02d:%02d' %
                                              (minutes, seconds, total_minutes, total_seconds))
        if start_again:
            self.media_play(controller, True)

    def media_pause_msg(self, msg):
        """
        Responds to the request to pause a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_pause(msg[0])

    def on_media_pause(self):
        """
        Responds to the request to pause a loaded video from the web.
        """
        self.media_pause(Registry().get('live_controller'))

    def media_pause(self, controller):
        """
        Responds to the request to pause a loaded video

        :param controller: The Controller to be paused
        """
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].pause(controller)
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(False)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False

    def media_loop_msg(self, msg):
        """
        Responds to the request to loop a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_loop(msg[0])

    @staticmethod
    def media_loop(controller):
        """
        Responds to the request to loop a loaded video

        :param controller: The controller that needs to be stopped
        """
        controller.media_info.is_looping_playback = not controller.media_info.is_looping_playback
        controller.mediabar.actions['playbackLoop'].setChecked(controller.media_info.is_looping_playback)

    def media_stop_msg(self, msg):
        """
        Responds to the request to stop a loaded video

        :param msg: First element is the controller which should be used
        """
        self.media_stop(msg[0])

    def on_media_stop(self):
        """
        Responds to the request to stop a loaded video from the web.
        """
        self.media_stop(Registry().get('live_controller'))

    def media_stop(self, controller):
        """
        Responds to the request to stop a loaded video

        :param controller: The controller that needs to be stopped
        """
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].stop(controller)
            self.current_media_players[controller.controller_type].set_visible(controller, False)
            # controller.preview_display.hide()
            controller.seek_slider.setSliderPosition(0)
            total_seconds = controller.media_info.length // 1000
            total_minutes = total_seconds // 60
            total_seconds %= 60
            controller.position_label.setText(' %02d:%02d / %02d:%02d' % (0, 0, total_minutes, total_seconds))
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(True)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False
            controller.media_info.timer = 1000
            controller.media_timer = 0

    def media_volume_msg(self, msg):
        """
        Changes the volume of a running video

        :param msg: First element is the controller which should be used
        """
        controller = msg[0]
        vol = msg[1][0]
        self.media_volume(controller, vol)

    def media_volume(self, controller, volume):
        """
        Changes the volume of a running video

        :param controller: The Controller to use
        :param volume: The volume to be set
        """
        log.debug('media_volume {vol}'.format(vol=volume))
        if controller.is_live:
            self.settings.setValue('media/live volume', volume)
        else:
            self.settings.setValue('media/preview volume', volume)
        controller.media_info.volume = volume
        self.current_media_players[controller.controller_type].volume(controller, volume)
        controller.volume_slider.setValue(volume)

    def media_seek_msg(self, msg):
        """
        Responds to the request to change the seek Slider of a loaded video via a message

        :param msg: First element is the controller which should be used
            Second element is a list with the seek value as first element
        """
        controller = msg[0]
        seek_value = msg[1][0]
        self.media_seek(controller, seek_value)

    def media_seek(self, controller, seek_value):
        """
        Responds to the request to change the seek Slider of a loaded video

        :param controller: The controller to use.
        :param seek_value: The value to set.
        """
        self.current_media_players[controller.controller_type].seek(controller, seek_value)
        controller.media_info.timer = seek_value

    def media_reset(self, controller):
        """
        Responds to the request to reset a loaded video
        :param controller: The controller to use.
        """
        self.set_controls_visible(controller, False)
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].reset(controller)
            self.current_media_players[controller.controller_type].set_visible(controller, False)
            del self.current_media_players[controller.controller_type]

    def media_hide(self, msg):
        """
        Hide the related video Widget

        :param msg: First element is the boolean for Live indication
        """
        is_live = msg[1]
        if not is_live:
            return
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() == MediaState.Playing:
            self.media_pause(self.live_controller)
            self.current_media_players[self.live_controller.controller_type].set_visible(self.live_controller, False)

    def media_blank(self, msg):
        """
        Blank the related video Widget

        :param msg: First element is the boolean for Live indication
            Second element is the hide mode
        """
        is_live = msg[1]
        hide_mode = msg[2]
        if not is_live:
            return
        Registry().execute('live_display_hide', hide_mode)
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() == MediaState.Playing:
            self.media_pause(self.live_controller)
            self.current_media_players[self.live_controller.controller_type].set_visible(self.live_controller, False)

    def media_unblank(self, msg):
        """
        Unblank the related video Widget

        :param msg: First element is not relevant in this context
            Second element is the boolean for Live indication
        """
        Registry().execute('live_display_show')
        is_live = msg[1]
        if not is_live:
            return
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() != \
                MediaState.Playing:
            if self.media_play(self.live_controller):
                self.current_media_players[self.live_controller.controller_type].set_visible(self.live_controller, True)
                # Start Timer for ui updates
                if not self.live_timer.isActive():
                    self.live_timer.start()

    def finalise(self):
        """
        Reset all the media controllers when OpenLP shuts down
        """
        self.live_timer.stop()
        self.preview_timer.stop()
        self.media_reset(self.display_controllers(DisplayControllerType.Live))
        self.media_reset(self.display_controllers(DisplayControllerType.Preview))

    @staticmethod
    def _define_display(controller):
        """
        Extract the correct display for a given controller

        :param controller:  Controller to be used
        """
        if controller.is_live:
            return controller.display
        return controller.preview_display
