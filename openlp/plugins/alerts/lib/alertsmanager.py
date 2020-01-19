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
The :mod:`~openlp.plugins.alerts.lib.alertsmanager` module contains the part of the plugin which manages storing and
displaying of alerts.
"""
import json

from PyQt5 import QtCore, QtGui

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.display.screens import ScreenList


class AlertsManager(QtCore.QObject, RegistryBase, LogMixin, RegistryProperties):
    """
    AlertsManager manages the settings of Alerts.
    """
    alerts_text = QtCore.pyqtSignal(list)

    def __init__(self, parent):
        super(AlertsManager, self).__init__()
        self.timer_id = 0
        self.alert_list = []
        Registry().register_function('live_display_active', self.generate_alert)
        Registry().register_function('alerts_text', self.alert_text)
        self.alerts_text.connect(self.alert_text)

    def alert_text(self, message):
        """
        Called via a alerts_text event. Message is single element array containing text.

        :param message: The message text to be displayed
        """
        if message:
            text = message[0]
            # remove line breaks as these crash javascript code on display
            while '\n' in text:
                text = text.replace('\n', ' ')
            self.display_alert(text)

    def display_alert(self, text=''):
        """
        Called from the Alert Tab to display an alert.

        :param text: The text to display
        """
        self.log_debug('display alert called {text}'.format(text=text))
        if text:
            self.alert_list.append(text)
            if self.timer_id != 0:
                self.main_window.show_status_message(
                    translate('AlertsPlugin.AlertsManager', 'Alert message created and displayed.'))
                return
            self.main_window.show_status_message('')
            self.generate_alert()

    def generate_alert(self):
        """
        Format and request the Alert and start the timer.
        """
        if not self.alert_list or (len(ScreenList()) == 1 and
                                   not self.settings.value('core/display on monitor')):
            return
        text = self.alert_list.pop(0)

        # Get the rgb color format of the font & background hex colors from settings
        rgb_font_color = self.hex_to_rgb(QtGui.QColor(self.settings.value('alerts/font color')))
        rgb_background_color = self.hex_to_rgb(QtGui.QColor(self.settings.value('alerts/background color')))

        # Put alert settings together in dict that will be passed to Display in Javascript
        alert_settings = {
            'backgroundColor': rgb_background_color,
            'location': self.settings.value('alerts/location'),
            'fontFace': self.settings.value('alerts/font face'),
            'fontSize': self.settings.value('alerts/font size'),
            'fontColor': rgb_font_color,
            'timeout': self.settings.value('alerts/timeout'),
            'repeat': self.settings.value('alerts/repeat'),
            'scroll': self.settings.value('alerts/scroll')
        }
        self.live_controller.displays[0].alert(text, json.dumps(alert_settings))

    def timerEvent(self, event):
        """
        Time has finished so if our time then request the next Alert if there is one and reset the timer.

        :param event: the QT event that has been triggered.
        """
        if event.timerId() == self.timer_id:
            alert_tab = self.parent().settings_tab
            self.live_controller.display.alert('', alert_tab.location)
        self.killTimer(self.timer_id)
        self.timer_id = 0
        self.generate_alert()

    def hex_to_rgb(self, rgb_values):
        """
        Converts rgb color values from QColor to rgb string

        :param rgb_values:
        :return: rgb color string
        :rtype: string
        """
        return "rgb(" + str(rgb_values.red()) + ", " + str(rgb_values.green()) + ", " + str(rgb_values.blue()) + ")"
