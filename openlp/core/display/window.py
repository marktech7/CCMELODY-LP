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
"""
The :mod:`~openlp.core.display.window` module contains the display window
"""
import json
import logging
import os
import copy

from PyQt5 import QtCore, QtWebChannel, QtWidgets

from openlp.core.common.applocation import AppLocation
from openlp.core.common.enum import ServiceItemType
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.path import path_to_str
from openlp.core.common.registry import Registry
from openlp.core.common.utils import wait_for
from openlp.core.display.screens import ScreenList
from openlp.core.ui import HideMode


log = logging.getLogger(__name__)


class MediaWatcher(QtCore.QObject):
    """
    A class to watch media events in the display and emit signals for OpenLP
    """
    progress = QtCore.pyqtSignal(float)
    duration = QtCore.pyqtSignal(float)
    volume = QtCore.pyqtSignal(float)
    playback_rate = QtCore.pyqtSignal(float)
    ended = QtCore.pyqtSignal(bool)
    muted = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot(float)
    def update_progress(self, time):
        """
        Notify about the current position of the media
        """
        log.warning(time)
        self.progress.emit(time)

    @QtCore.pyqtSlot(float)
    def update_duration(self, time):
        """
        Notify about the duration of the media
        """
        log.warning(time)
        self.duration.emit(time)

    @QtCore.pyqtSlot(float)
    def update_volume(self, level):
        """
        Notify about the volume of the media
        """
        log.warning(level)
        level = level * 100
        self.volume.emit(level)

    @QtCore.pyqtSlot(float)
    def update_playback_rate(self, rate):
        """
        Notify about the playback rate of the media
        """
        log.warning(rate)
        self.playback_rate.emit(rate)

    @QtCore.pyqtSlot(bool)
    def has_ended(self, is_ended):
        """
        Notify that the media has ended playing
        """
        log.warning(is_ended)
        self.ended.emit(is_ended)

    @QtCore.pyqtSlot(bool)
    def has_muted(self, is_muted):
        """
        Notify that the media has been muted
        """
        log.warning(is_muted)
        self.muted.emit(is_muted)


class DisplayWatcher(QtCore.QObject):
    """
    This facilitates communication from the Display object in the browser back to the Python
    """
    initialised = QtCore.pyqtSignal(bool)

    @QtCore.pyqtSlot(bool)
    def setInitialised(self, is_initialised):
        """
        This method is called from the JS in the browser to set the _is_initialised attribute
        """
        log.info('Display is initialised: {init}'.format(init=is_initialised))
        self.initialised.emit(is_initialised)


class DisplayWindow(QtWidgets.QWidget, RegistryProperties):
    """
    This is a window to show the output
    """
    def __init__(self, parent=None, screen=None, can_show_startup_screen=True):
        """
        Create the display window
        """
        super(DisplayWindow, self).__init__(parent)
        # Gather all flags for the display window
        flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint
        if self.settings.value('advanced/x11 bypass wm'):
            flags |= QtCore.Qt.X11BypassWindowManagerHint
        # Need to import this inline to get around a QtWebEngine issue
        from openlp.core.display.webengine import WebEngineView
        self._is_initialised = False
        self._can_show_startup_screen = can_show_startup_screen
        self._fbo = None
        self.setWindowTitle(translate('OpenLP.DisplayWindow', 'Display Window'))
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.webview = WebEngineView(self)
        self.webview.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.webview.page().setBackgroundColor(QtCore.Qt.transparent)
        self.layout.addWidget(self.webview)
        self.webview.loadFinished.connect(self.after_loaded)
        display_base_path = AppLocation.get_directory(AppLocation.AppDir) / 'core' / 'display' / 'html'
        self.display_path = display_base_path / 'display.html'
        self.checkerboard_path = display_base_path / 'checkerboard.png'
        self.openlp_splash_screen_path = display_base_path / 'openlp-splash-screen.png'
        self.set_url(QtCore.QUrl.fromLocalFile(path_to_str(self.display_path)))
        self.channel = QtWebChannel.QWebChannel(self)
        self.media_watcher = MediaWatcher(self)
        self.channel.registerObject('mediaWatcher', self.media_watcher)
        self.display_watcher = DisplayWatcher(self)
        self.channel.registerObject('displayWatcher', self.display_watcher)
        self.webview.page().setWebChannel(self.channel)
        self.display_watcher.initialised.connect(self.on_initialised)
        self.is_display = False
        self.scale = 1
        self.hide_mode = None
        self.__script_done = True
        self.__script_result = None
        if screen and screen.is_display:
            Registry().register_function('live_display_hide', self.hide_display)
            Registry().register_function('live_display_show', self.show_display)
            self.update_from_screen(screen)
            self.is_display = True
            # Only make visible on single monitor setup if setting enabled.
            if len(ScreenList()) > 1 or self.settings.value('core/display on monitor'):
                self.show()

    @property
    def is_initialised(self):
        return self._is_initialised

    def on_initialised(self, is_initialised):
        """
        Update the initialised status
        """
        self._is_initialised = is_initialised

    def update_from_screen(self, screen):
        """
        Update the number and the geometry from the screen.

        :param Screen screen: A `~openlp.core.display.screens.Screen` instance
        """
        self.setGeometry(screen.display_geometry)
        self.screen_number = screen.number

    def set_single_image(self, bg_color, image_path):
        """
        :param str bg_color: Background color
        :param Path image_path: Path to the image
        """
        image_uri = image_path.as_uri()
        self.run_javascript('Display.setFullscreenImage("{bg_color}", "{image}");'.format(bg_color=bg_color,
                                                                                          image=image_uri))

    def set_single_image_data(self, bg_color, image_data):
        self.run_javascript('Display.setFullscreenImageFromData("{bg_color}", '
                            '"{image_data}");'.format(bg_color=bg_color, image_data=image_data))

    def set_startup_screen(self):
        bg_color = self.settings.value('core/logo background color')
        image = self.settings.value('core/logo file')
        if path_to_str(image).startswith(':'):
            image = self.openlp_splash_screen_path
        image_uri = image.as_uri()
        self.run_javascript('Display.setStartupSplashScreen("{bg_color}", "{image}");'.format(bg_color=bg_color,
                                                                                              image=image_uri))

    def set_url(self, url):
        """
        Set the URL of the webview

        :param QtCore.QUrl | str url: The URL to set
        """
        if not isinstance(url, QtCore.QUrl):
            url = QtCore.QUrl(url)
        self.webview.setUrl(url)

    def set_html(self, html):
        """
        Set the html
        """
        self.webview.setHtml(html)

    def after_loaded(self):
        """
        Add stuff after page initialisation
        """
        js_is_display = str(self.is_display).lower()
        self.run_javascript('Display.init({do_transitions});'.format(do_transitions=js_is_display))
        wait_for(lambda: self._is_initialised)
        if self.scale != 1:
            self.set_scale(self.scale)
        if self._can_show_startup_screen:
            self.set_startup_screen()

    def run_javascript(self, script, is_sync=False):
        """
        Run some Javascript in the WebView

        :param script: The script to run, a string
        :param is_sync: Run the script synchronously. Defaults to False
        """
        log.debug(script)
        # Wait for previous scripts to finish
        wait_for(lambda: self.__script_done)
        if is_sync:
            self.__script_done = False
            self.__script_result = None

            def handle_result(result):
                """
                Handle the result from the asynchronous call
                """
                self.__script_done = True
                self.__script_result = result

            self.webview.page().runJavaScript(script, handle_result)
            # Wait for script to finish
            if not wait_for(lambda: self.__script_done):
                self.__script_done = True
            return self.__script_result
        else:
            self.webview.page().runJavaScript(script)

    def go_to_slide(self, verse):
        """
        Go to a particular slide.

        :param str verse: The verse to go to, e.g. "V1" for songs, or just "0" for other types
        """
        self.run_javascript('Display.goToSlide("{verse}");'.format(verse=verse))

    def load_verses(self, verses, is_sync=False):
        """
        Set verses in the display
        """
        json_verses = json.dumps(verses)
        print(json_verses)
        self.run_javascript('Display.setTextSlides({verses});'.format(verses=json_verses), is_sync=is_sync)

    def load_images(self, images):
        """
        Set images in the display
        """
        imagesr = copy.deepcopy(images)
        for image in imagesr:
            image['path'] = image['path'].as_uri()
        json_images = json.dumps(imagesr)
        self.run_javascript('Display.setImageSlides({images});'.format(images=json_images))

    def load_video(self, video):
        """
        Load video in the display
        """
        video = copy.deepcopy(video)
        video['path'] = video['path'].as_uri()
        json_video = json.dumps(video)
        self.run_javascript('Display.setVideo({video});'.format(video=json_video))

    def play_video(self):
        """
        Play the currently loaded video
        """
        self.run_javascript('Display.playVideo();')

    def pause_video(self):
        """
        Pause the currently playing video
        """
        self.run_javascript('Display.pauseVideo();')

    def stop_video(self):
        """
        Stop the currently playing video
        """
        self.run_javascript('Display.stopVideo();')

    def set_video_playback_rate(self, rate):
        """
        Set the playback rate of the current video.

        The rate can be any valid float, with 0.0 being stopped, 1.0 being normal speed,
        over 1.0 is faster, under 1.0 is slower, and negative is backwards.

        :param rate: A float indicating the playback rate.
        """
        self.run_javascript('Display.setPlaybackRate({rate});'.format(rate=rate))

    def set_video_volume(self, level):
        """
        Set the volume of the current video.

        The volume should be an int from 0 to 100, where 0 is no sound and 100 is maximum volume. Any
        values outside this range will raise a ``ValueError``.

        :param level: A number between 0 and 100
        """
        if level < 0 or level > 100:
            raise ValueError('Volume should be from 0 to 100, was "{}"'.format(level))
        self.run_javascript('Display.setVideoVolume({level});'.format(level=level))

    def toggle_video_mute(self):
        """
        Toggle the mute of the current video
        """
        self.run_javascript('Display.toggleVideoMute();')

    def save_screenshot(self, fname=None):
        """
        Save a screenshot, either returning it or saving it to file
        """
        pixmap = self.grab()
        if fname:
            ext = os.path.splitext(fname)[-1][1:]
            pixmap.save(fname, ext)
        else:
            return pixmap

    def set_theme(self, theme, is_sync=False, service_item_type=False):
        """
        Set the theme of the display
        """
        print(service_item_type)
        print(theme.background_type)
        print(self.is_display)
        # If review Display for media so we need to display black box.
        if not self.is_display and service_item_type == ServiceItemType.Command:
            theme_copy = copy.deepcopy(theme)
            theme_copy.background_type = 'solid'
            theme_copy.background_start_color = '#090909'
            theme_copy.background_end_color = '#090909'
            theme_copy.background_main_color = '#090909'
            theme_copy.background_footer_color = '#090909'
            exported_theme = theme_copy.export_theme(is_js=True)
        # If background is transparent and this is not a display, inject checkerboard background image instead
        elif theme.background_type == 'transparent' and not self.is_display:
            theme_copy = copy.deepcopy(theme)
            theme_copy.background_type = 'image'
            theme_copy.background_filename = self.checkerboard_path
            exported_theme = theme_copy.export_theme(is_js=True)
        else:
            exported_theme = theme.export_theme(is_js=True)
        self.run_javascript('Display.setTheme({theme});'.format(theme=exported_theme), is_sync=is_sync)

    def get_video_types(self):
        """
        Get the types of videos playable by the embedded media player
        """
        return self.run_javascript('Display.getVideoTypes();', is_sync=True)

    def show_display(self):
        """
        Show the display
        """
        if self.is_display:
            # Only make visible on single monitor setup if setting enabled.
            if len(ScreenList()) == 1 and not self.settings.value('core/display on monitor'):
                return
        self.run_javascript('Display.show();')
        # Check if setting for hiding logo on startup is enabled.
        # If it is, display should remain hidden, otherwise logo is shown. (from def setup)
        if self.isHidden() and not self.settings.value('core/logo hide on startup'):
            self.setVisible(True)
        self.hide_mode = None
        # Trigger actions when display is active again.
        if self.is_display:
            Registry().execute('live_display_active')

    def blank_to_theme(self):
        """
        Blank to theme
        """
        self.run_javascript('Display.blankToTheme();')

    def hide_display(self, mode=HideMode.Screen):
        """
        Hide the display by making all layers transparent Store the images so they can be replaced when required

        :param mode: How the screen is to be hidden
        """
        log.debug('hide_display mode = {mode:d}'.format(mode=mode))
        if self.is_display:
            # Only make visible on single monitor setup if setting enabled.
            if len(ScreenList()) == 1 and not self.settings.value('core/display on monitor'):
                return
        if mode == HideMode.Screen:
            self.setVisible(False)
        elif mode == HideMode.Blank:
            self.run_javascript('Display.blankToBlack();')
        else:
            self.run_javascript('Display.blankToTheme();')
        if mode != HideMode.Screen:
            if self.isHidden():
                self.setVisible(True)
                self.webview.setVisible(True)
        self.hide_mode = mode

    def set_scale(self, scale):
        """
        Set the HTML scale
        """
        self.scale = scale
        # Only scale if initialised (scale run again once initialised)
        if self._is_initialised:
            self.run_javascript('Display.setScale({scale});'.format(scale=scale * 100))

    def alert(self, text, settings):
        """
        Set an alert
        """
        self.run_javascript('Display.alert("{text}", {settings});'.format(text=text, settings=settings))
