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
The :mod:`screen` module provides management functionality for a machines'
displays.
"""
import logging
from functools import cmp_to_key

from PyQt5 import QtCore, QtWidgets

from openlp.core.common import Singleton
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


log = logging.getLogger(__name__)


class Screen(object):
    """
    A Python representation of a screen
    """
    def __init__(self, number=None, geometry=None, custom_geometry=None, is_primary=False, is_display=False):
        """
        Set up the screen object

        :param int number: The Qt number of this screen
        :param QRect geometry: The geometry of this screen as a QRect object
        :param QRect custom_geometry: The custom geometry of this screen as a QRect object
        :param bool is_primary: Whether or not this screen is the primary screen
        :param bool is_display: Whether or not this screen should be used to display lyrics
        """
        self.number = int(number)
        self.geometry = geometry
        self.custom_geometry = custom_geometry
        self.is_primary = is_primary
        self.is_display = is_display

    def __str__(self):
        """
        Return a string for displaying this screen

        :return str: A nicely formatted string
        """
        name = '{screen} {number:d}'.format(screen=translate('OpenLP.ScreenList', 'Screen'), number=self.number + 1)
        if self.is_primary:
            name = '{name} ({primary})'.format(name=name, primary=translate('OpenLP.ScreenList', 'primary'))
        return name

    def __repr__(self):
        """
        Return a string representation of the object
        """
        return '<{screen}>'.format(screen=self)

    @property
    def display_geometry(self):
        """
        Returns the geometry to use when displaying. This property decides between the native and custom geometries
        """
        return self.custom_geometry or self.geometry

    @classmethod
    def from_dict(cls, screen_dict):
        """
        Create a screen object from a dictionary

        :param dict screen_dict: The dictionary from which to make the Screen object
        :return: A Screen object with the values from screen_dict
        :rtype: openlp.core.display.screens.Screen
        """
        screen_dict['geometry'] = QtCore.QRect(screen_dict['geometry']['x'], screen_dict['geometry']['y'],
                                               screen_dict['geometry']['width'], screen_dict['geometry']['height'])
        if 'custom_geometry' in screen_dict:
            screen_dict['custom_geometry'] = QtCore.QRect(screen_dict['custom_geometry']['x'],
                                                          screen_dict['custom_geometry']['y'],
                                                          screen_dict['custom_geometry']['width'],
                                                          screen_dict['custom_geometry']['height'])
        return cls(**screen_dict)

    def to_dict(self):
        """
        Convert a screen object to a dictionary

        :return: A dictionary of this screen
        :rtype: dict
        """
        screen_dict = {
            'number': self.number,
            'geometry': {
                'x': self.geometry.x(),
                'y': self.geometry.y(),
                'width': self.geometry.width(),
                'height': self.geometry.height()
            },
            'is_primary': self.is_primary,
            'is_display': self.is_display
        }
        if self.custom_geometry is not None:
            screen_dict['custom_geometry'] = {
                'x': self.custom_geometry.x(),
                'y': self.custom_geometry.y(),
                'width': self.custom_geometry.width(),
                'height': self.custom_geometry.height()
            }
        return screen_dict

    def update(self, screen_dict):
        """
        Update this instance from a dictionary

        :param dict screen_dict: The dictionary which we want to apply to the screen
        """
        self.number = int(screen_dict['number']) if 'number' in screen_dict else self.number
        self.is_display = screen_dict.get('is_display', self.is_display)
        self.is_primary = screen_dict.get('is_primary', self.is_primary)
        if 'geometry' in screen_dict:
            try:
                self.geometry = QtCore.QRect(screen_dict['geometry']['x'], screen_dict['geometry']['y'],
                                             screen_dict['geometry']['width'], screen_dict['geometry']['height'])
            except KeyError:
                # Preserve the current values as this has come from the settings update which does not have
                # the geometry information
                pass
        if 'custom_geometry' in screen_dict:
            self.custom_geometry = QtCore.QRect(screen_dict['custom_geometry']['x'],
                                                screen_dict['custom_geometry']['y'],
                                                screen_dict['custom_geometry']['width'],
                                                screen_dict['custom_geometry']['height'])


class ScreenList(metaclass=Singleton):
    """
    Wrapper to handle the parameters of the display screen.

    To get access to the screen list call ``ScreenList()``.
    """
    log.info('Screen loaded')
    screens = []

    def __iter__(self):
        """
        Convert this object into an iterable, so that we can iterate over it instead of the inner list
        """
        for screen in self.screens:
            yield screen

    def __getitem__(self, key):
        """
        Make sure this object is indexable, e.g. screen_list[1] => Screen(number=1)
        """
        for screen in self:
            if screen.number == key:
                return screen
        else:
            raise IndexError('No screen with number {number} in list'.format(number=key))

    def __len__(self):
        """
        Make sure we can call "len" on this object
        """
        return len(self.screens)

    @property
    def current(self):
        """
        Return the first "current" desktop

        NOTE: This is a HACK to ease the upgrade process
        """
        # Get the first display screen
        for screen in self.screens:
            if screen.is_display:
                return screen
        # If there's no display screen, get the first primary screen
        for screen in self.screens:
            if screen.is_primary:
                return screen
        # Otherwise just return the first screen
        if len(self.screens) > 0:
            return self.screens[0]
        else:
            return None

    @classmethod
    def create(cls, desktop):
        """
        Initialise the screen list.

        :param desktop:  A QDesktopWidget object.
        """
        screen_list = cls()
        screen_list.desktop = desktop
        screen_list.desktop.resized.connect(screen_list.on_screen_resolution_changed)
        screen_list.desktop.screenCountChanged.connect(screen_list.on_screen_count_changed)
        screen_list.desktop.primaryScreenChanged.connect(screen_list.on_primary_screen_changed)
        screen_list.update_screens()
        screen_list.load_screen_settings()
        return screen_list

    def load_screen_settings(self):
        """
        Loads the screen size and the screen number from the settings.
        """
        # Add the screen settings to the settings dict. This has to be done here due to cyclic dependency.
        # Do not do this anywhere else.
        screen_settings = {
            'core/screens': '{}'
        }
        Settings.extend_default_settings(screen_settings)
        screen_settings = Settings().value('core/screens')
        if screen_settings:
            for number, screen_dict in screen_settings.items():
                # Sometimes this loads as a string instead of an int
                number = int(number)
                if self.has_screen(number):
                    self[number].update(screen_dict)
                else:
                    self.screens.append(Screen.from_dict(screen_dict))
        else:
            self[len(self) - 1].is_display = True

    def save_screen_settings(self):
        """
        Saves the screen size and screen settings
        """
        Settings().setValue('core/screens', {screen.number: screen.to_dict() for screen in self.screens})

    def get_display_screen_list(self):
        """
        Returns a list with the screens. This should only be used to display available screens to the user::

            ['Screen 1 (primary)', 'Screen 2']
        """
        screen_list = []
        for screen in self.screens:
            screen_name = '{name} {number:d}'.format(name=translate('OpenLP.ScreenList', 'Screen'),
                                                     number=screen.number + 1)
            if screen.is_primary:
                screen_name = '{name} ({primary})'.format(name=screen_name,
                                                          primary=translate('OpenLP.ScreenList', 'primary'))
            screen_list.append(screen_name)
        return screen_list

    def get_number_for_window(self, window):
        """
        Return the screen number that the centre of the passed window is in.

        :param window: A QWidget we are finding the location of.
        """
        for screen in self.screens:
            if screen.geometry == window.geometry() or screen.display_geometry == window.geometry():
                return screen
        return None

    def set_display_screen(self, number, can_save=False):
        """
        Set screen number ``number`` to be the display screen.

        At the moment, this is forced to be only a single screen, but later when we support multiple monitors it
        will need to be updated.

        :param int number: The number of the screen
        :param bool can_save: If the screen settings should be saved, defaults to False.
        """
        for screen in self.screens:
            if screen.number == number:
                screen.is_display = True
            else:
                screen.is_display = False
        if can_save:
            self.save_screen_settings()

    def has_screen(self, number):
        """
        Confirms a screen is known.

        :param number: The screen number (int).
        """
        for screen in self.screens:
            if screen.number == number:
                return True
        return False

    def update_screens(self):
        """
        Update the list of screens
        """
        def _screen_compare(this, other):
            """
            Compare screens. Can't use a key here because of the nested property and method to be called
            """
            if this.geometry().x() < other.geometry().x():
                return -1
            elif this.geometry().x() > other.geometry().x():
                return 1
            else:
                if this.geometry().y() < other.geometry().y():
                    return -1
                elif this.geometry().y() > other.geometry().y():
                    return 1
                else:
                    return 0
        self.screens = []
        os_screens = QtWidgets.QApplication.screens()
        os_screens.sort(key=cmp_to_key(_screen_compare))
        for number, screen in enumerate(os_screens):
            self.screens.append(
                Screen(number, screen.geometry(), is_primary=self.desktop.primaryScreen() == number))

    def on_screen_resolution_changed(self, number):
        """
        Called when the resolution of a screen has changed.

        ``number``
            The number of the screen, which size has changed.
        """
        log.info('screen_resolution_changed {number:d}'.format(number=number))
        for screen in self.screens:
            if number == screen.number:
                screen.geometry = self.desktop.screenGeometry(number)
                screen.is_primary = self.desktop.primaryScreen() == number
                Registry().execute('config_screen_changed')
                break

    def on_screen_count_changed(self, changed_screen=None):
        """
        Called when a screen has been added or removed.

        ``changed_screen``
            The screen's number which has been (un)plugged.
        """
        screen_count = self.desktop.screenCount()
        log.info('screen_count_changed {count:d}'.format(count=screen_count))
        # Update the list of screens
        self.update_screens()
        # Reload setting tabs to apply possible changes.
        Registry().execute('config_screen_changed')

    def on_primary_screen_changed(self):
        """
        The primary screen has changed, let's sort it out and then notify everyone
        """
        for screen in self.screens:
            screen.is_primary = self.desktop.primaryScreen() == screen.number
        Registry().execute('config_screen_changed')
