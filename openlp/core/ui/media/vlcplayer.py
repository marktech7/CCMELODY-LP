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

'''
Openlp makes use of the events which are triggered by VLC under certain circumstances. A summary is below.
Most of these result in the UI being updated.

Event:           MediaStateChanged
Associated with: vlc Media class
Triggered:       whenever there is a change of state associated with the vlc media
Openlp function: media_state_changed_event_listener.
                 Used to detect a state of Stopped so that media items can be restarted if looping is set on

Event:           MediaPlayerEndReached
Associated with: vlc MediaPlayer
Triggered:       whenever vlc has finished playing a media item - either an individual item, or an item which
                 is part of a playlist.
Openlp function: media_item_finished_event_listener
                 If playing a playlist then this event is ignored.
                 If not playing a playlist and looping is set on, then the item is restarted. However, you can't
                 immediately called play() in this state of Ended - you have to go to Stopped first.

Event:           MediaPlayerMediaChanged
Associated with: vlc MediaPlayer
Triggered:       whenever the new item within a playlist starts
Openlp function: media_changed_event_listener
                 Used to update the UI based on the new item

Event:           MediaListPlayerPlayed
Associated with: vlc MediaListPlayer
Triggered:       whenever the end of a playlist is reached.
                 Used to restart the playlist if looping is set on

Note that in some event listeners and states you can't call vlc functions such as play() directly but must use a thread.
See https://stackoverflow.com/a/68491297
'''

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
        self.setup_vlc_player(controller)
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

    def setup_vlc_player(self, controller):
        vlc = get_vlc()
        # creating an empty vlc media player
        controller.vlc_media_player = controller.vlc_instance.media_player_new()
        # create a new media list player and attach the media player to it
        controller.vlc_media_list_player = controller.vlc_instance.media_list_player_new()
        controller.vlc_media_list_player.set_playback_mode(vlc.PlaybackMode.default)
        controller.vlc_media_list_player.set_media_player(controller.vlc_media_player)
        # event managers
        controller.vlc_media_player_event_manager = controller.vlc_media_player.event_manager()
        controller.vlc_media_list_player_event_manager = controller.vlc_media_list_player.event_manager()

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
        print('in vlc load with file: ' + str(file))
        if not controller.vlc_instance:
            return False
        vlc = get_vlc()
        self.file = file
        log.debug('load video in VLC Controller')
        path = None
        # need to create a new blank playlist and give it to the media list player
        # otherwise old playlists hang around and can get played in subsequent items
        controller.vlc_media_list = controller.vlc_instance.media_list_new()
        controller.vlc_media_list_player.set_media_list(controller.vlc_media_list)
        # create the media
        if controller.media_info.media_type == MediaType.CD:
            path = os.path.normcase(file)
            if is_win():
                path = '/' + path
            controller.vlc_media = controller.vlc_instance.media_new_location('cdda://' + path)
            controller.vlc_media_player.set_media(controller.vlc_media)
            controller.vlc_media_player.play()
            # Wait for media to start playing. In this case VLC actually returns an error.
            self.media_state_wait(controller, [vlc.State.Playing, vlc.State.Stopped])
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
            path = os.path.normcase(file)
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
            self.media_state_wait(controller, [vlc.State.Playing])
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
            else:
                path = os.path.normcase(file)
                controller.vlc_media = controller.vlc_instance.media_new_path(path)
        if not controller.media_info.is_playlist:
            # put the media in the media player (already done for playlist)
            controller.vlc_media_player.set_media(controller.vlc_media)
            # parse the metadata of the file (already done for playlist)
            controller.vlc_media.parse()
        if controller.media_info.is_playlist:
            controller.vlc_media_event_manager = controller.vlc_media_list.event_manager()

            controller.vlc_media_list_player_event_manager.event_attach(vlc.EventType.MediaListPlayerPlayed,
                                                                        self.media_list_finished_event_listener,
                                                                        controller)
            # detach any event managers first to make doubly we don't end up with multiple messages
            # controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerMediaChanged)
            # controller.vlc_media_list_player_event_manager.event_detach(vlc.EventType.MediaListPlayerPlayed)
        else:
            # controller.vlc_media_player_event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
            controller.vlc_media_event_manager = controller.vlc_media.event_manager()
            controller.vlc_media_event_manager.event_attach(vlc.EventType.MediaStateChanged,
                                                            self.media_state_changed_event_listener, controller)

        controller.vlc_media_player_event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged,
                                                               self.media_changed_event_listener, controller)
        controller.vlc_media_player_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,
                                                               self.media_item_finished_event_listener, controller)

        controller.seek_slider.setMinimum(controller.media_info.start_time)
        controller.seek_slider.setMaximum(controller.media_info.end_time)
        self.volume(controller, controller.media_info.volume)
        return True

    def media_state_wait(self, controller, media_states):
        """
        Wait for the video to change its state
        Wait no longer than 60 seconds. (loading an iso file needs a long time)

        :param media_states: The anticipated state or states of the playing media
        :param controller: The controller where the media is
        :return:
        """

        vlc = get_vlc()
        start = datetime.now()
        if controller.media_info.is_playlist:
            while controller.vlc_media_list_player.get_state() not in media_states:
                print('in media_state_wait playlist, state: ' + str(controller.vlc_media_list_player.get_state()))
                sleep(0.1)
                if controller.vlc_media_list_player.get_state() == vlc.State.Error:
                    return False
                if controller.vlc_media_list_player.get_state() == vlc.State.Ended:
                    threading.Thread(target=controller.vlc_media_player.stop).start()
                self.application.process_events()
                if (datetime.now() - start).seconds > 60:
                    return False
        else:
            while controller.vlc_media_list_player.get_state() not in media_states:
                print('in media_state_wait single item, state: ' + str(controller.vlc_media_list_player.get_state()))
                sleep(0.1)
                if controller.vlc_media.get_state() == vlc.State.Error:
                    return False
                if controller.vlc_media_list_player.get_state() == vlc.State.Ended:
                    threading.Thread(target=controller.vlc_media_player.stop).start()
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
        print('in vlc play, controller.media_info.timer = ' + str(controller.media_info.timer))
        vlc = get_vlc()
        print('vlc state: ' + str(controller.vlc_media_list_player.get_state()))
        log.debug('vlc play, mediatype: ' + str(controller.media_info.media_type))
        if controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_list_player.play).start()
        else:
            threading.Thread(target=controller.vlc_media_player.play).start()
        if not self.media_state_wait(controller, [vlc.State.Playing]):
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
        if self.media_state_wait(controller, [vlc.State.Paused]):
            self.set_state(MediaState.Paused, controller)

    def stop(self, controller):
        """
        Stop the current item

        :param controller: The controller where the media is
        :return:
        """
        print('in media stop')
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

    def media_item_finished_event_listener(self, event, controller):
        """
        Event listener which gets fired when VLC finishes playing a media item (a single item, or one within a playlist)
        To enable the vlc player to be reused it calls stop(), but this needs to be done via a thread.
        If the media is looping then it will be restarted (in media_state_changed_event_listener)  when the state
        becomes Stopped
        Otherwise the UI is updated to take account of the media item being finished.

        :param event: the VLC event
        :param controller: The controller handling that media item
        :return: None
        """
        print('in media_item_finished_event_listener')
        if not controller.media_info.is_playlist:
            threading.Thread(target=controller.vlc_media_player.stop).start()
            if not controller.media_info.is_looping_playback:
                controller.media_info.is_playing = False
                self.media_controller.update_ui_media_finished(controller)

    def media_list_finished_event_listener(self, event, controller):
        """
        Event listener which gets fired when VLC finishes playing a media playlist.
        The function checks if the media list is looping, and if so, restarts playing it.

        :param event: the VLC event
        :param controller: The controller handling that media item
        :return: None
        """
        print('in media_list_finished_event_listener')
        if controller.media_info.is_looping_playback:
            print('restarting media list')
            threading.Thread(target=controller.vlc_media_list_player.play).start()
        else:
            controller.media_info.is_playing = False
            # stop the media player to ensure its get_time() gets reset to zero
            threading.Thread(target=controller.vlc_media_list_player.stop).start()
            threading.Thread(target=controller.vlc_media_player.stop).start()
            self.media_controller.update_ui_media_finished(controller)

    def media_changed_event_listener(self, event, controller):
        """
        Event listener which gets fired when VLC changes the media item it's playing
        The function initiates changes to the UI

        :param event: the VLC event
        :param controller: The controller handling that media item
        :return: None
        """
        print('in media_changed_event_listener for ' + controller.vlc_media_player.get_media().get_mrl())
        if controller.media_info.is_playlist:
            playlist_length = controller.vlc_media_list.count()
            this_item_index = controller.vlc_media_list.index_of_item(controller.vlc_media_player.get_media())
            print('item number ' + str(this_item_index) + ' of ' + str(playlist_length))
            self.media_controller.update_ui_new_playlist_item(controller, this_item_index == 0,
                                                              this_item_index == playlist_length - 1,
                                                              controller.vlc_media_player.get_media().get_duration())

    def media_state_changed_event_listener(self, event, controller):
        vlc = get_vlc()
        print('in media_state_changed_event_listener with state ' + str(controller.vlc_media_player.get_state()))
        if controller.vlc_media_player.get_state() == vlc.State.Stopped and controller.media_info.is_looping_playback:
            threading.Thread(target=controller.vlc_media_player.play).start()
