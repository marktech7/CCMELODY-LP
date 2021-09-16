# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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

from PyQt5 import QtCore

from openlp.core.state import State
from openlp.core.common import is_linux, is_macosx
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.path import path_to_str
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui import DisplayControllerType, HideMode
from openlp.core.ui.media import MediaState, ItemMediaInfo, MediaType, parse_optical_path, parse_stream_path
from openlp.core.ui.media.remote import register_views
from openlp.core.ui.media.vlcplayer import VlcPlayer, get_vlc


log = logging.getLogger(__name__)

TICK_TIME = 200
HIDE_DELAY_TIME = 2500


class MediaController(RegistryBase, LogMixin, RegistryProperties):
    """
    The implementation of the Media Controller which manages how media is played.
    """
    def __init__(self, parent=None):
        """
        """
        super(MediaController, self).__init__(parent)
        self.log_info('MediaController Initialising')

    def setup(self):
        self.vlc_player = None
        self.current_media_players = {}
        # Timer for video state
        self.live_timer = QtCore.QTimer()
        self.live_timer.setInterval(TICK_TIME)
        self.live_hide_timer = QtCore.QTimer()
        self.live_hide_timer.setSingleShot(True)
        self.live_kill_timer = QtCore.QTimer()
        self.live_kill_timer.setSingleShot(True)
        self.preview_timer = QtCore.QTimer()
        self.preview_timer.setInterval(TICK_TIME)
        # Signals
        self.live_timer.timeout.connect(self._media_state_live)
        self.live_hide_timer.timeout.connect(self._on_media_hide_live)
        self.live_kill_timer.timeout.connect(self._on_media_kill_live)
        self.preview_timer.timeout.connect(self._media_state_preview)
        Registry().register_function('playbackPlay', self.media_play_msg)
        Registry().register_function('playbackPause', self.media_pause_msg)
        Registry().register_function('playbackStop', self.media_stop_msg)
        Registry().register_function('playbackLoop', self.media_loop_msg)
        Registry().register_function('playbackPrevious', self.media_previous_msg)
        Registry().register_function('playbackNext', self.media_next_msg)
        Registry().register_function('seek_slider', self.media_seek_msg)
        Registry().register_function('volume_slider', self.media_volume_msg)
        Registry().register_function('media_hide', self.media_hide)
        Registry().register_function('media_blank', self.media_blank)
        Registry().register_function('media_unblank', self.media_unblank)
        # Signals for background video
        Registry().register_function('songs_hide', self.media_hide)
        Registry().register_function('songs_blank', self.media_blank)
        Registry().register_function('songs_unblank', self.media_unblank)
        register_views()

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

    def _display_controllers(self, controller_type):
        """
        Decides which controller to use.

        :param controller_type: The controller type where a player will be placed
        """
        if controller_type == DisplayControllerType.Live:
            return self.live_controller
        return self.preview_controller

    def _media_state_live(self):
        """
        Check if there is a running Live media Player and do updating stuff (e.g. update the UI)
        """
        if DisplayControllerType.Live in self.current_media_players:
            media_player = self.current_media_players[DisplayControllerType.Live]
            media_player.resize(self.live_controller)
            self.update_ui_slider(self.live_controller)
            if not self.live_controller.media_info.is_playing:
                self.live_timer.stop()
        else:
            self.live_timer.stop()
            self.media_stop(self.live_controller)

    def _media_state_preview(self):
        """
        Check if there is a running Preview media Player and do updating stuff (e.g. update the UI)
        """
        if DisplayControllerType.Preview in self.current_media_players:
            media_player = self.current_media_players[DisplayControllerType.Preview]
            media_player.resize(self.preview_controller)
            self.update_ui_slider(self.preview_controller)
            if not self.preview_controller.media_info.is_playing:
                self.preview_timer.stop()
        else:
            self.preview_timer.stop()
            self.media_stop(self.preview_controller)

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
        self.vlc_player.setup(controller, self._define_display(controller))

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
        controller = self._display_controllers(source)
        log.debug(f'load_video is_live:{controller.is_live}')
        # stop running videos
        self.media_reset(controller)
        controller.media_info = ItemMediaInfo()
        controller.media_info.media_type = MediaType.Video
        controller.media_info.is_playlist = False
        if controller.is_live:
            controller.media_info.volume = self.settings.value('media/live volume')
        else:
            controller.media_info.volume = self.settings.value('media/preview volume')
        # background will always loop video.
        if service_item.is_capable(ItemCapabilities.HasBackgroundAudio):
            controller.media_info.file_info = service_item.background_audio
            controller.media_info.media_type = MediaType.Audio
            # is_background indicates we shouldn't override the normal display
            controller.media_info.is_background = True
            controller.media_info.is_playlist = isinstance(service_item.background_audio, list) and \
                len(service_item.background_audio) > 1
        else:
            if service_item.is_capable(ItemCapabilities.HasBackgroundStream):
                (name, mrl, options) = parse_stream_path(service_item.stream_mrl)
                controller.media_info.file_info = (mrl, options)
                controller.media_info.is_background = True
                controller.media_info.media_type = MediaType.Stream
            elif service_item.is_capable(ItemCapabilities.HasBackgroundVideo):
                controller.media_info.file_info = [service_item.video_file_name]
                service_item.media_length = self.media_length(path_to_str(service_item.video_file_name))
                controller.media_info.is_looping_playback = True
                controller.media_info.is_background = True
            else:
                controller.media_info.file_info = [service_item.get_frame_path()]
        display = self._define_display(controller)
        # if this is an optical device use special handling
        if service_item.is_capable(ItemCapabilities.IsOptical):
            self.log_debug(f'video is optical and {"live" if controller.is_live else "preview"}')
            path_string = path_to_str(service_item.get_frame_path())
            (name, title, audio_track, subtitle_track, start, end, clip_name) = parse_optical_path(path_string)
            is_valid = self.media_setup_optical(name, title, audio_track, subtitle_track, start, end, display,
                                                controller)
        elif service_item.is_capable(ItemCapabilities.CanStream):
            self.log_debug(f'video is stream and {"live" if controller.is_live else "preview"}')
            path = service_item.get_frames()[0]['path']
            controller.media_info.media_type = MediaType.Stream
            (name, mrl, options) = parse_stream_path(path)
            controller.media_info.file_info = (mrl, options)
            is_valid = self._check_file_type(controller, display)
        else:
            self.log_debug(f'video is not optical or stream, but {"live" if controller.is_live else "preview"}')
            controller.media_info.length = service_item.media_length
            controller.media_info.start_time = service_item.start_time
            controller.media_info.end_time = service_item.start_time + service_item.media_length
            is_valid = self._check_file_type(controller, display)
        if not is_valid:
            # Media could not be loaded correctly
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                       translate('MediaPlugin.MediaItem', 'Unsupported File'))
            return False
        self.log_debug('video media type: {tpe} '.format(tpe=str(controller.media_info.media_type)))
        # If both the preview and live view have a stream, make sure only the live view continues streaming
        if controller.media_info.media_type == MediaType.Stream:
            if controller.is_live:
                if self.preview_controller.media_info.media_type == MediaType.Stream:
                    self.log_warning('stream can only be displayed in one instance, killing preview stream')
                    self.preview_controller.on_media_close()
            else:
                if self.live_controller.media_info.media_type == MediaType.Stream:
                    self.log_warning('stream cannot be previewed while also streaming live')
                    return
        autoplay = False
        if service_item.requires_media() and hidden == HideMode.Theme:
            autoplay = True
        # Preview requested
        elif not controller.is_live:
            autoplay = True
        # Visible or background requested or Service Item wants to autostart
        elif not hidden or service_item.will_auto_start:
            autoplay = True
        # Unblank on load set
        elif self.settings.value('core/auto unblank'):
            autoplay = True
        # display the seek UI before starting the media, as the duration is changed for each playlist item
        self.update_ui_slider(controller, controller.media_info.start_time, controller.media_info.end_time)
        if autoplay:
            if not self.media_play(controller):
                critical_error_message_box(translate('MediaPlugin.MediaItem', 'Unsupported File'),
                                           translate('MediaPlugin.MediaItem', 'Unsupported File'))
                return False
        self.set_controls_visible(controller, True)
        self.log_debug('use {nm} controller'.
                       format(nm=self.current_media_players[controller.controller_type].display_name))
        return True

    @staticmethod
    def media_length(media_path):
        """
        Uses Media Info to obtain the media length

        :param media_path: The file path to be checked..
        """
        if MediaInfo.can_parse():
            media_data = MediaInfo.parse(media_path)
            # duration returns in milli seconds
            return media_data.tracks[0].duration
        return 0

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
        self.vlc_player.load(controller, display, filename)
        self.resize(controller, self.vlc_player)
        self.current_media_players[controller.controller_type] = self.vlc_player
        return True

    def _check_file_type(self, controller, display):
        """
        Select the correct media Player type from the prioritized Player list

        :param controller: First element is the controller which should be used
        :param display: Which display to use
        """
        if controller.media_info.media_type == MediaType.Stream:
            self.resize(controller, self.vlc_player)
            if self.vlc_player.load(controller, display, controller.media_info.file_info):
                self.current_media_players[controller.controller_type] = self.vlc_player
                return True
            return False
        if controller.media_info.is_playlist:
            self.resize(controller, self.vlc_player)
            if self.vlc_player.load(controller, display, controller.media_info.file_info):
                self.current_media_players[controller.controller_type] = self.vlc_player
                return True
        else:
            for file in controller.media_info.file_info:
                if not file.is_file and not self.vlc_player.can_folder:
                    return False
                file = str(file)
                self.resize(controller, self.vlc_player)
                if self.vlc_player.load(controller, display, file):
                    self.current_media_players[controller.controller_type] = self.vlc_player
                    return True
        return False

    def media_play_msg(self, msg):
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

    def media_play(self, controller):
        """
        Responds to the request to play a loaded video

        :param controller: The controller to be played
        """
        print('in media_play')
        self.log_debug(f'media_play is_live:{controller.is_live}')
        controller.seek_slider.blockSignals(True)
        controller.volume_slider.blockSignals(True)
        display = self._define_display(controller)
        if not self.current_media_players[controller.controller_type].play(controller, display):
            controller.seek_slider.blockSignals(False)
            controller.volume_slider.blockSignals(False)
            return False
        self.media_volume(controller, controller.media_info.volume)
        self._media_set_visibility(controller, True)
        controller.mediabar.actions['playbackPlay'].setVisible(False)
        controller.mediabar.actions['playbackPause'].setVisible(True)
        controller.mediabar.actions['playbackStop'].setDisabled(False)
        controller.mediabar.actions['playbackLoop'].setChecked(controller.media_info.is_looping_playback)
        controller.mediabar.actions['playbackStop'].setVisible(not controller.media_info.is_background or
                                                               controller.media_info.media_type is MediaType.Audio)
        controller.mediabar.actions['playbackLoop'].setVisible((not controller.media_info.is_background and
                                                               controller.media_info.media_type is not MediaType.Stream)
                                                               or controller.media_info.media_type is MediaType.Audio)
        if controller.media_info.is_playlist:
            controller.mediabar.actions['playbackPrevious'].setVisible(True)
            controller.mediabar.actions['playbackNext'].setVisible(True)
        else:
            controller.mediabar.actions['playbackPrevious'].setVisible(False)
            controller.mediabar.actions['playbackNext'].setVisible(False)
        # Start Timer for ui updates
        if controller.is_live:
            if not self.live_timer.isActive():
                self.live_timer.start()
        else:
            if not self.preview_timer.isActive():
                self.preview_timer.start()
        controller.seek_slider.blockSignals(False)
        controller.volume_slider.blockSignals(False)
        controller.media_info.is_playing = True
        if not controller.media_info.is_background:
            display = self._define_display(controller)
            if controller.is_live:
                controller.set_hide_mode(None)
                display.hide_display(HideMode.Screen)
            controller._set_theme(controller.service_item)
            display.load_verses([{"verse": "v1", "text": "", "footer": " "}])
        controller.output_has_changed()
        return True

    '''
    def tick(self, controller):
        """
        Add a tick while the media is playing but only count if not paused

        :param controller:  The Controller to be processed
        :return:            Is the video still running?
        """
        #print('in tick')
        #print(controller.vlc_media_player.get_time())
        start_again = False
        stopped = False
        if controller.media_info.is_playing and controller.media_info.length > 0:
            controller.media_info.timer += TICK_TIME
            if controller.media_info.timer >= controller.media_info.start_time + controller.media_info.length:
                if controller.media_info.is_looping_playback:
                    start_again = True
                else:
                    stopped = True
        else:
            stopped = True

        if start_again:
            controller.media_info.timer = 0
        return not stopped

    def _update_seek_ui(self, controller):
        seconds = controller.media_info.timer // 1000
        minutes = seconds // 60
        seconds %= 60
        end_seconds = controller.media_info.end_time // 1000
        end_minutes = end_seconds // 60
        end_seconds %= 60
        controller.position_label.setText(' %02d:%02d / %02d:%02d' %
                                          (minutes, seconds, end_minutes, end_seconds))
    '''

    def update_ui_media_finished(self, controller):
        """
        Update the UI when a media item or media list has finished
        This sets the mediabar icons and slider appropriately

        :param controller: The controller associated with the media event
        """
        print('in update_ui_media_finished')
        controller.mediabar.actions['playbackPlay'].setVisible(True)
        controller.mediabar.actions['playbackPause'].setVisible(False)
        controller.mediabar.actions['playbackStop'].setDisabled(True)
        if controller.media_info.is_playlist:
            controller.mediabar.actions['playbackPrevious'].setDisabled(True)
            controller.mediabar.actions['playbackNext'].setDisabled(True)
        self.update_ui_slider(controller)

    def update_ui_new_playlist_item(self, controller, first, last, duration):
        """
        Update the UI when a media item of a playlist starts playing
        This sets the mediabar icons and slider appropriately

        :param controller: The controller associated with the playlist
        :param first: if this is the first item in the playlist
        :param last: if this is the last item in the playlist
        :param duration: duration of this item in milliseconds
        """
        if first:
            print('disabling previous')
            controller.mediabar.actions['playbackPrevious'].setDisabled(True)
        else:
            controller.mediabar.actions['playbackPrevious'].setEnabled(True)
        if last:
            print('disabling last')
            controller.mediabar.actions['playbackNext'].setDisabled(True)
        else:
            controller.mediabar.actions['playbackNext'].setEnabled(True)
        if duration > 0:
            self.update_ui_slider(controller, None, duration)

    def update_ui_slider(self, controller, position=None, duration=None):
        """
        Update the UI slider with the passed-in position and duration
        If the position is None then the current vlc media player time is used
        If the duration is None then only the position label is updated
        if the duration is passed then the slider max is set also

        :param controller: The controller associated with the slider
        :param position: current position of the media in milliseconds (int or float)
        :param duration: duration of the media in milliseconds (int or float)
        """
        print('in update_ui_slider with position: ' + ('None' if position is None else str(position)) + ', duration: ' +
              ('None' if duration is None else str(duration)) + ', min: ' + str(controller.seek_slider.minimum()) +
              ', max: ' + str(controller.seek_slider.maximum()))
        if position is None:
            vlc = get_vlc()
            if controller.vlc_media_player.get_state() in [vlc.State.Playing, vlc.State.Paused]:
                position = controller.vlc_media_player.get_time()
            else:
                position = controller.media_info.start_time
        if isinstance(position, float):
            position = int(position)
        if isinstance(duration, float):
            duration = int(duration)
        controller.seek_slider.blockSignals(True)
        # set slider maximum
        if duration:
            controller.seek_slider.setMaximum(duration)
        # set slider position
        if not controller.seek_slider.isSliderDown():
            controller.seek_slider.setSliderPosition(position)
        # set label
        seconds = position // 1000
        minutes = seconds // 60
        seconds %= 60
        if duration is not None:
            total_seconds = duration // 1000
            total_minutes = total_seconds // 60
            total_seconds %= 60
            controller.position_label.setText(f" {minutes:02d}:{seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
            print(f" {minutes:02d}:{seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
        else:
            # just update the current time
            label_value = controller.position_label.text()
            if len(label_value) > 7:
                label_value = f" {minutes:02d}:{seconds:02d} " + label_value[7:]
            controller.position_label.setText(label_value)
            print(f" {minutes:02d}:{seconds:02d} ")
        controller.seek_slider.blockSignals(False)

    def media_pause_msg(self, msg):
        """
        Responds to the request to pause a loaded video

        :param msg: First element is the controller which should be used
        """
        return self.media_pause(msg[0])

    def on_media_pause(self):
        """
        Responds to the request to pause a loaded video from the web.
        """
        return self.media_pause(self.live_controller)

    def media_pause(self, controller):
        """
        Responds to the request to pause a loaded video

        :param controller: The Controller to be paused
        """
        self.log_debug(f'media_stop is_live:{controller.is_live}')
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].pause(controller)
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False
            controller.output_has_changed()
            return True
        return False

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
        return self.media_stop(msg[0])

    def on_media_stop(self):
        """
        Responds to the request to stop a loaded video from the web.
        """
        return self.media_stop(self.live_controller)

    def media_stop(self, controller):
        """
        Responds to the request to stop a loaded video

        :param controller: The controller that needs to be stopped
        """
        self.log_debug(f'media_stop is_live:{controller.is_live}')
        # if looping is on then switch it off to prevent restart when vlc State Stopped reached
        if controller.media_info.is_looping_playback:
            self.media_loop(controller)
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].stop(controller)
            if controller.is_live:
                self.live_hide_timer.start(HIDE_DELAY_TIME)
                if not controller.media_info.is_background:
                    display = self._define_display(controller)
                    if display.hide_mode == HideMode.Screen:
                        Registry().execute('live_display_hide', HideMode.Blank)
                    else:
                        controller.set_hide_mode(display.hide_mode or HideMode.Blank)
            else:
                self._media_set_visibility(controller, False)
            controller.mediabar.actions['playbackPlay'].setVisible(True)
            controller.mediabar.actions['playbackStop'].setDisabled(True)
            controller.mediabar.actions['playbackPause'].setVisible(False)
            controller.media_info.is_playing = False
            self.update_ui_slider(controller, controller.media_info.start_time, controller.media_info.end_time)
            controller.output_has_changed()
            return True
        return False

    def media_previous_msg(self, msg):
        """
        Responds to the request to go to the previous media item

        :param msg: First element is the controller which should be used
        """
        return self.media_previous(msg[0])

    def on_media_previous(self):
        """
        Responds to the request to go to the previous media item
        """
        return self.media_previous(self.live_controller)

    def media_previous(self, controller):
        self.current_media_players[controller.controller_type].previous(controller)

    def media_next_msg(self, msg):
        """
        Responds to the request to go to the next media item

        :param msg: First element is the controller which should be used
        """
        return self.media_next(msg[0])

    def on_media_next(self):
        """
        Responds to the request to go to the next media item
        """
        return self.media_next(self.live_controller)

    def media_next(self, controller):
        self.current_media_players[controller.controller_type].next(controller)

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
        self.log_debug(f'media_volume {volume}')
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
        # This may be triggered by setting the slider max/min before the current_media_players dict is set
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].seek(controller, seek_value)
            self.update_ui_slider(controller, seek_value)

    def media_reset(self, controller, delayed=False):
        """
        Responds to the request to reset a loaded video
        :param controller: The controller to use.
        :param delayed: Should the controller briefly remain visible.
        """
        self.log_debug('media_reset')
        self.set_controls_visible(controller, False)
        if controller.controller_type in self.current_media_players:
            self.current_media_players[controller.controller_type].reset(controller)
            if controller.is_live and delayed:
                self.live_kill_timer.start(HIDE_DELAY_TIME)
            else:
                if controller.is_live:
                    self.live_kill_timer.stop()
                else:
                    self._media_set_visibility(controller, False)
                del self.current_media_players[controller.controller_type]

    def media_hide_msg(self, msg):
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
        self.log_debug(f'media_hide is_live:{is_live}')
        if not is_live or self.live_kill_timer.isActive():
            return
        if self.live_controller.controller_type in self.current_media_players and \
                self.current_media_players[self.live_controller.controller_type].get_live_state() == MediaState.Playing:
            if delayed:
                self.live_hide_timer.start(HIDE_DELAY_TIME)
            else:
                self.media_pause(self.live_controller)
                self._media_set_visibility(self.live_controller, False)

    def _on_media_hide_live(self):
        self.media_pause(self.live_controller)
        self._media_set_visibility(self.live_controller, False)

    def _on_media_kill_live(self):
        self._media_set_visibility(self.live_controller, False)
        del self.current_media_players[self.live_controller.controller_type]

    def _media_set_visibility(self, controller, visible):
        """
        Set the live video Widget visibility
        """
        if controller.is_live:
            self.live_hide_timer.stop()
        visible = visible and controller.media_info.media_type is not MediaType.Audio
        self.current_media_players[controller.controller_type].set_visible(controller, visible)

    def media_blank(self, msg):
        """
        Blank the related video Widget

        :param msg: First element is the boolean for Live indication
            Second element is the hide mode
        """
        is_live = msg[1]
        hide_mode = msg[2]
        self.log_debug(f'media_blank is_live:{is_live}')
        if not is_live or self.live_controller.controller_type not in self.current_media_players:
            return
        if self.live_kill_timer.isActive():
            # If pressing blank when the video is being removed, remove it instantly
            self._media_set_visibility(self.live_controller, False)
            self.media_reset(self.live_controller)
            return
        if not self.live_controller.media_info.is_background:
            Registry().execute('live_display_hide', hide_mode)
        controller_type = self.live_controller.controller_type
        playing = self.current_media_players[controller_type].get_live_state() == MediaState.Playing
        if hide_mode == HideMode.Theme:
            if not playing:
                self.media_play(self.live_controller)
            else:
                self.live_hide_timer.stop()
        else:
            if hide_mode == HideMode.Screen:
                if playing:
                    self.media_pause(self.live_controller)
                self._media_set_visibility(self.live_controller, False)
            else:
                self.live_hide_timer.start(HIDE_DELAY_TIME)

    def media_unblank(self, msg):
        """
        Unblank the related video Widget

        :param msg: First element is not relevant in this context
            Second element is the boolean for Live indication
        """
        is_live = msg[1]
        self.log_debug(f'media_blank is_live:{is_live}')
        if not is_live or self.live_kill_timer.isActive():
            return
        Registry().execute('live_display_show')
        if self.live_controller.controller_type in self.current_media_players:
            if self.current_media_players[self.live_controller.controller_type].get_live_state() != \
                    MediaState.Playing:
                self.media_play(self.live_controller)
            else:
                self._media_set_visibility(self.live_controller, True)
                if not self.live_controller.media_info.is_background:
                    display = self._define_display(self.live_controller)
                    display.hide_display(HideMode.Screen)

    def finalise(self):
        """
        Reset all the media controllers when OpenLP shuts down
        """
        self.live_timer.stop()
        self.live_hide_timer.stop()
        self.live_kill_timer.stop()
        self.preview_timer.stop()
        self.media_reset(self._display_controllers(DisplayControllerType.Live))
        self.media_reset(self._display_controllers(DisplayControllerType.Preview))

    @staticmethod
    def _define_display(controller):
        """
        Extract the correct display for a given controller

        :param controller:  Controller to be used
        """
        if controller.is_live:
            return controller.display
        return controller.preview_display
