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
The :mod:`~openlp.core.ui.media.vlcplayer` module contains our VLC component wrapper
"""
import ctypes
import logging
import os
import sys
import threading
from datetime import datetime
from time import sleep

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import is_linux, is_macosx, is_win
from openlp.core.common.i18n import translate
from openlp.core.display.screens import ScreenList
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.media import MediaState, MediaType
from openlp.core.ui.media.mediaplayer import MediaPlayer

log = logging.getLogger(__name__)

# Audio and video extensions copied from 'include/vlc_interface.h' from vlc 2.2.0 source

_vlc = None

def get_vlc():
    """
    In order to make this module more testable, we have to wrap the VLC import inside a method. We do this so that we
    can mock out the VLC module entirely.

    :return: The "vlc" module, or None
    """
    # use the global variable if it's set
    global _vlc
    if _vlc:
        return _vlc
    # Import the VLC module if not already done
    if 'vlc' not in sys.modules:
        try:
            import vlc  # noqa module is not used directly, but is used via sys.modules['vlc']
        except (ImportError, OSError):
            return None
    # Verify that VLC is also loadable
    is_vlc_available = False
    try:
        is_vlc_available = bool(sys.modules['vlc'].get_default_instance())
    except Exception:
        pass
    if is_vlc_available:
        _vlc = sys.modules['vlc']
        return _vlc
    return None


# On linux we need to initialise X threads, but not when running tests.
# This needs to happen on module load and not in get_vlc(), otherwise it can cause crashes on some DE on some setups
# (reported on Gnome3, Unity, Cinnamon, all GTK+ based) when using native filedialogs...
if is_linux() and 'pytest' not in sys.argv[0] and get_vlc():
    try:
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
        except OSError:
            # If libx11.so.6 was not found, fallback to more generic libx11.so
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except Exception:
        log.exception('Failed to run XInitThreads(), VLC might not work properly!')

def media_item_finished_event_listener(event, controller):
    """
    Event listener which gets fired when VLC finishes playing a media item which is not part of a playlist
    The function checks if the media item is looping, and if so, restarts playing it.
    It does this synchronously to avoid race conditions with the 'tick' functionality

    :param controller: The controller handling that media item
    :return: None
    """
    print('in media_item_finished_event_listener')
    if controller.media_info.is_looping_playback:
        print('restarting media item' + controller.vlc_media_player.get_media().get_mrl())
        controller.vlc_media_player.play()
    else:
        controller.media_info.is_playing = False
        controller.vlc_media_player.stop()
        update_ui_media_finished(controller)

def media_list_finished_event_listener(event, controller):
    """
    Event listener which gets fired when VLC finishes playing a media playlist.
    The function checks if the media list is looping, and if so, restarts playing it.
    It does this synchronously to avoid race conditions with the 'tick' functionality

    :param controller: The controller handling that media item
    :return: None
    """
    print('in media_list_finished_event_listener')
    if controller.media_info.is_looping_playback:
        print('restarting media list')
        controller.vlc_media_list_player.play()
    else:
        controller.media_info.is_playing = False
        controller.vlc_media_list_player.stop()
        controller.vlc_media_player.stop()
        # stop the media player to ensure its get_time() gets reset to zero
        # threading.Thread(target=controller.vlc_media_player.stop).start()
        update_ui_media_finished(controller)

def media_changed_event_listener(event, controller):
    """
    Event listener which gets fired when VLC changes the media item it's playing
    The function initiates changes to the UI based on the duration of the new media item

    :param controller: The controller handling that media item
    :return: None
    """
    print('in media_changed_event_listener for ' + controller.vlc_media_player.get_media().get_mrl())
    print('duration: ' + str(controller.vlc_media_player.get_media().get_duration() // 1000) + ' seconds')
    playlist_length = controller.vlc_media_list.count()
    this_item_index = controller.vlc_media_list.index_of_item(controller.vlc_media_player.get_media())
    print('item number ' + str(this_item_index) + ' of ' + str(playlist_length))
    if controller.media_info.is_playlist:
        update_ui_new_playlist_item(controller, this_item_index == 0, this_item_index == playlist_length - 1, controller.vlc_media_player.get_media().get_duration())

def update_ui_media_finished(controller):
    """
    Update the UI when a media item or media list has finished
    This sets the mediabar icons and slider appropriately

    :param controller: Which Controller is running the show.
    """
    controller.mediabar.actions['playbackPlay'].setVisible(True)
    controller.mediabar.actions['playbackPause'].setVisible(False)
    controller.mediabar.actions['playbackStop'].setDisabled(True)
    if controller.media_info.is_playlist:
        controller.mediabar.actions['playbackPrevious'].setDisabled(True)
        controller.mediabar.actions['playbackNext'].setDisabled(True)
    update_ui_slider(controller, 0, controller.media_info.length)

def update_ui_new_playlist_item(controller, first, last, duration):
    """
    Update the UI when a media item of a playlist starts playing
    This sets the mediabar icons and slider appropriately

    :param controller: Which Controller is running the show.
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
        update_ui_slider(controller, 0, duration)

def update_ui_slider(controller, position, duration):
    """
    Update the UI slider with the passed-in position and duration
    This sets the mediabar icons and slider appropriately

    :param controller: Which Controller is running the show.
    :param position: current position of the media
    :param duration: duration of the media
    """
    controller.seek_slider.blockSignals(True)
    controller.seek_slider.setMaximum(duration)
    controller.seek_slider.setSliderPosition(position)
    total_seconds = duration // 1000
    total_minutes = total_seconds // 60
    total_seconds %= 60
    controller.position_label.setText(' %02d:%02d / %02d:%02d' % (0, 0, total_minutes, total_seconds))
    controller.seek_slider.blockSignals(False)


class VlcPlayer(MediaPlayer):
    """
    A specialised version of the MediaPlayer class, which provides a VLC display.
    """

    def __init__(self, parent):
        """
        Constructor
        """
        super(VlcPlayer, self).__init__(parent, 'vlc')
        self.original_name = 'VLC'
        self.display_name = '&VLC'
        self.parent = parent
        self.can_folder = True

    def setup(self, controller, display):
        """
        Set up the media player

        :param controller: The controller where the media is
        :param display: The display where the media is.
        :return:
        """
        vlc = get_vlc()
        if controller.is_live:
            controller.vlc_widget = QtWidgets.QFrame()
            controller.vlc_widget.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool |
                                                 QtCore.Qt.WindowStaysOnTopHint)
        else:
            controller.vlc_widget = QtWidgets.QFrame(display)
        controller.vlc_widget.setFrameStyle(QtWidgets.QFrame.NoFrame)
        # creating a basic vlc instance
        command_line_options = '--no-video-title-show '
        if self.settings.value('advanced/hide mouse') and controller.is_live:
            command_line_options += '--mouse-hide-timeout=0 '
        if self.settings.value('media/vlc arguments'):
            options = command_line_options + ' ' + self.settings.value('media/vlc arguments')
            controller.vlc_instance = vlc.Instance(options)
            # if the instance is None, it is likely that the comamndline options were invalid, so try again without
            if not controller.vlc_instance:
                controller.vlc_instance = vlc.Instance(command_line_options)
                if controller.vlc_instance:
                    critical_error_message_box(message=translate('MediaPlugin.VlcPlayer',
                                                                 'The VLC arguments are invalid.'))
                else:
                    return
        else:
            controller.vlc_instance = vlc.Instance(command_line_options)
            if not controller.vlc_instance:
                return
        log.debug(f"VLC version: {vlc.libvlc_get_version()}")
        # creating an empty vlc media player
        controller.vlc_media_player = controller.vlc_instance.media_player_new()
        # create a new media list player and attach the media player to it
        controller.vlc_media_list_player = controller.vlc_instance.media_list_player_new()
        controller.vlc_media_list_player.set_playback_mode(vlc.PlaybackMode.default)
        controller.vlc_media_list_player.set_media_player(controller.vlc_media_player)
        # create associated event managers
        controller.vlc_media_player_event_manager = controller.vlc_media_player.event_manager()
        controller.vlc_media_list_player_event_manager = controller.vlc_media_list_player.event_manager()
        controller.vlc_widget.resize(controller.size())
        controller.vlc_widget.hide()
        # The media player has to be 'connected' to the QFrame.
        # (otherwise a video would be displayed in it's own window)
        # This is platform specific!
        # You have to give the id of the QFrame (or similar object)
        # to vlc, different platforms have different functions for this.
        win_id = int(controller.vlc_widget.winId())
        if is_win():
            controller.vlc_media_player.set_hwnd(win_id)
        elif is_macosx():
            # We have to use 'set_nsobject' since Qt5 on OSX uses Cocoa
            # framework and not the old Carbon.
            controller.vlc_media_player.set_nsobject(win_id)
        else:
            # for Linux/*BSD using the X Server
            controller.vlc_media_player.set_xwindow(win_id)
        self.has_own_widget = True

    def check_available(self):
        """
        Return the availability of VLC
        """
        return get_vlc() is not None

    def load(self, controller, output_display, file):
        """
        Load a video into VLC

        :param controller: The controller where the media is
        :param output_display: The display where the media is
        :param file: file/stream to be played
        :return:
        """
        if not controller.vlc_instance:
            return False
        vlc = get_vlc()
        log.debug('load video in VLC Controller')
        path = None
        # create the media
        if controller.media_info.media_type == MediaType.CD:
            if file:
                path = os.path.normcase(file)
            if is_win():
                path = '/' + path
            controller.vlc_media = controller.vlc_instance.media_new_location('cdda://' + path)
            controller.vlc_media_player.set_media(controller.vlc_media)
            controller.vlc_media_player.play()
            # Wait for media to start playing. In this case VLC actually returns an error.
            self.media_state_wait(controller, vlc.State.Playing)
            # If subitems exists, this is a CD
            audio_cd_tracks = controller.vlc_media.subitems()
            if not audio_cd_tracks or audio_cd_tracks.count() < 1:
                return False
            controller.vlc_media = audio_cd_tracks.item_at_index(int(controller.media_info.title_track))
            if not controller.vlc_media:
                return False
            # VLC's start and stop time options work on seconds
            controller.vlc_media.add_option(f"start-time={int(controller.media_info.start_time // 1000)}")
            controller.vlc_media.add_option(f"stop-time={int(controller.media_info.end_time // 1000)}")
            controller.vlc_media_player.set_media(controller.vlc_media)
        elif controller.media_info.media_type == MediaType.DVD:
            if is_win():
                path = '/' + path
            dvd_location = 'dvd://' + path + '#' + controller.media_info.title_track
            controller.vlc_media = controller.vlc_instance.media_new_location(dvd_location)
            log.debug(f"vlc dvd load: {dvd_location}")
            controller.vlc_media.add_option(f"start-time={int(controller.media_info.start_time // 1000)}")
            controller.vlc_media.add_option(f"stop-time={int(controller.media_info.end_time // 1000)}")
            controller.vlc_media_player.set_media(controller.vlc_media)
            controller.vlc_media_player.play()
            # Wait for media to start playing. In this case VLC returns an error.
            self.media_state_wait(controller, vlc.State.Playing)
            if controller.media_info.audio_track > 0:
                res = controller.vlc_media_player.audio_set_track(controller.media_info.audio_track)
                log.debug('vlc play, audio_track set: ' + str(controller.media_info.audio_track) + ' ' + str(res))
            if controller.media_info.subtitle_track > 0:
                res = controller.vlc_media_player.video_set_spu(controller.media_info.subtitle_track)
                log.debug('vlc play, subtitle_track set: ' + str(controller.media_info.subtitle_track) + ' ' + str(res))
        elif controller.media_info.media_type == MediaType.Stream:
            controller.vlc_media = controller.vlc_instance.media_new_location(file[0])
            controller.vlc_media.add_options(file[1])
            controller.vlc_media_player.set_media(controller.vlc_media)
        else:
            # file is either a single filename or a list of filenames
            if controller.media_info.is_playlist:
                controller.vlc_media_list = controller.vlc_instance.media_list_new()
                for filename in file:
                    path = os.path.normcase(filename)
                    vlc_media_item = controller.vlc_instance.media_new_path(path)
                    vlc_media_item.parse()
                    controller.vlc_media_list.add_media(vlc_media_item)
                controller.vlc_media_list_player.set_media_list(controller.vlc_media_list)
                # detach any event managers first to make doubly we don't end up with multiple messages
                #controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerMediaChanged)
                controller.vlc_media_player_event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, media_changed_event_listener, controller)
                #controller.vlc_media_list_player_event_manager.event_detach(vlc.EventType.MediaListPlayerPlayed)
                controller.vlc_media_list_player_event_manager.event_attach(vlc.EventType.MediaListPlayerPlayed, media_list_finished_event_listener, controller)
            else:
                path = os.path.normcase(file)
                controller.vlc_media = controller.vlc_instance.media_new_path(path)
                # need to create a new blank playlist and give it to the media list player
                # otherwise old playlists hang around and can get played in subsequent items
                controller.vlc_media_list = controller.vlc_instance.media_list_new()
                controller.vlc_media_list_player.set_media_list(controller.vlc_media_list)
                #controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
                controller.vlc_media_player_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, media_item_finished_event_listener, controller)
        if not controller.media_info.is_playlist:
            # put the media in the media player (already done for playlist)
            controller.vlc_media_player.set_media(controller.vlc_media)
            # parse the metadata of the file (already done for playlist)
            controller.vlc_media.parse()
        controller.seek_slider.setMinimum(controller.media_info.start_time)
        controller.seek_slider.setMaximum(controller.media_info.end_time)
        self.volume(controller, controller.media_info.volume)
        return True

    def media_state_wait(self, controller, media_state):
        """
        Wait for the video to change its state
        Wait no longer than 60 seconds. (loading an iso file needs a long time)

        :param media_state: The state of the playing media
        :param controller: The controller where the media is
        :return:
        """
        vlc = get_vlc()
        start = datetime.now()
        if controller.media_info.is_playlist:
            while media_state != controller.vlc_media_list_player.get_state():
                sleep(0.1)
                if controller.vlc_media_list_player.get_state() == vlc.State.Error:
                    return False
                self.application.process_events()
                if (datetime.now() - start).seconds > 60:
                    return False
        else:
            while media_state != controller.vlc_media.get_state():
                sleep(0.1)
                if controller.vlc_media.get_state() == vlc.State.Error:
                    return False
                self.application.process_events()
                if (datetime.now() - start).seconds > 60:
                    return False
        return True

    def resize(self, controller):
        """
        Resize the player

        :param controller: The display where the media is stored within the controller.
        :return:
        """
        if controller.is_live:
            controller.vlc_widget.setGeometry(ScreenList().current.display_geometry)
        else:
            controller.vlc_widget.resize(controller.preview_display.size())

    def play(self, controller, output_display):
        """
        Play the current item

        :param controller: Which Controller is running the show.
        :param output_display: The display where the media is
        :return:
        """
        vlc = get_vlc()
        start_time = 0
        log.debug('vlc play, mediatype: ' + str(controller.media_info.media_type))
        if controller.is_live:
            if self.get_live_state() != MediaState.Paused and controller.media_info.timer > 0:
                start_time = controller.media_info.timer
        else:
            if self.get_preview_state() != MediaState.Paused and controller.media_info.timer > 0:
                start_time = controller.media_info.timer
        if controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_list_player.play).start()
        else:
            threading.Thread(target=controller.vlc_media_player.play).start()
        if not self.media_state_wait(controller, vlc.State.Playing):
            return False
        self.volume(controller, controller.media_info.volume)
        self.set_state(MediaState.Playing, controller)
        return True

    def pause(self, controller):
        """
        Pause the current item

        :param controller: The controller which is managing the display
        :return:
        """
        vlc = get_vlc()
        if controller.media_info.is_playlist:
            if controller.vlc_media_list_player.get_state() != vlc.State.Playing:
                return
            controller.vlc_media_list_player.pause()
        else:
            if controller.vlc_media.get_state() != vlc.State.Playing:
                return
            controller.vlc_media_player.pause()
        if self.media_state_wait(controller, vlc.State.Paused):
            self.set_state(MediaState.Paused, controller)

    def stop(self, controller):
        """
        Stop the current item

        :param controller: The controller where the media is
        :return:
        """
        vlc = get_vlc()
        if controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_list_player.stop).start()
        else:
            threading.Thread(target=controller.vlc_media_player.stop).start()
        self.set_state(MediaState.Stopped, controller)

    def previous(self, controller):
        """
        Play the previous track of a playlist

        :param display: The display to be updated.
        """
        if controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_list_player.previous).start()

    def next(self, controller):
        """
        Play the next track of a playlist

        :param display: The display to be updated.
        """
        if controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_list_player.next).start()

    def volume(self, controller, vol):
        """
        Set the volume

        :param vol: The volume to be sets
        :param controller: The controller where the media is
        :return:
        """
        controller.vlc_media_player.audio_set_volume(vol)

    def seek(self, controller, seek_value):
        """
        Go to a particular position

        :param seek_value: The position of where a seek goes to
        :param controller: The controller where the media is
        """
        if controller.vlc_media_player.is_seekable():
            controller.vlc_media_player.set_time(seek_value)

    def reset(self, controller):
        """
        Reset the player

        :param controller: The controller where the media is
        """
        print('in vlc reset')
        vlc = get_vlc()
        controller.vlc_media_player.stop()
        controller.vlc_media_list_player.stop()
        controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerMediaChanged)
        controller.vlc_media_list_player_event_manager.event_detach(vlc.EventType.MediaListPlayerPlayed)
        controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
        self.set_state(MediaState.Off, controller)

    def set_visible(self, controller, status):
        """
        Set the visibility

        :param controller: The controller where the media display is
        :param status: The visibility status
        """
        controller.vlc_widget.setVisible(status)

    def update_ui(self, controller, output_display):
        """
        Update the UI

        :param controller: Which Controller is running the show.
        :param output_display: The display where the media is
        """
        if not controller.seek_slider.isSliderDown():
            controller.seek_slider.blockSignals(True)
            controller.seek_slider.setSliderPosition(controller.vlc_media_player.get_time())
            controller.seek_slider.blockSignals(False)
