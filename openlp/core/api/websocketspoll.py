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
from time import sleep

from PyQt5 import QtCore
from openlp.core.common.registry import Registry
from openlp.core.common.mixins import RegistryProperties


class WebSocketPoller(QtCore.QObject, RegistryProperties):
    """
    Accessed by web sockets to get status type information from the application
    """

    changed = QtCore.pyqtSignal()

    def __init__(self):
        """
        Constructor for the web sockets poll builder class.
        """
        super(WebSocketPoller, self).__init__()
        self._previous = None
        self._sent_previous = False

    def get_state(self):
        poller_manager = Registry().get('poller_manager')

        if poller_manager is not None:
            extra_items = poller_manager.sub_items
        else:
            extra_items = {}

        return {'results': {
            **extra_items,
            'counter': self.live_controller.slide_count if self.live_controller.slide_count else 0,
            'service': self.service_manager.service_id,
            'slide': self.live_controller.selected_row or 0,
            'item': self.live_controller.service_item.unique_identifier if self.live_controller.service_item else '',
            'twelve': self.settings.value('api/twelve hour'),
            'blank': self.live_controller.blank_screen.isChecked(),
            'theme': self.live_controller.theme_screen.isChecked(),
            'display': self.live_controller.desktop_screen.isChecked(),
            'version': 3,
            'isSecure': self.settings.value('api/authentication enabled'),
            'chordNotation': self.settings.value('songs/chord notation')
        }}

    def hook_signals(self, **args):
        self.live_controller.slidecontroller_changed.connect(self.on_signal_received)
        self.service_manager.servicemanager_changed.connect(self.on_signal_received)
        # Registry().register_function('api_configuration_changed', self.on_signal_received)

    @QtCore.pyqtSlot(list)
    @QtCore.pyqtSlot(str)
    @QtCore.pyqtSlot()
    def on_signal_received(self):
        self._previous = self.get_state()
        self._sent_previous = False
        self.changed.emit()

    def get_state_if_changed(self):
        """
        Poll OpenLP to determine current state if it has changed.

        This must only be used by web sockets or else we could miss a state change.

        :return: The current application state or None if unchanged since last call
        """
        if not self._sent_previous:
            if self._previous is None:
                self._previous = self.get_state()
                self._sent_previous = False

            self._sent_previous = True
            return self._previous
        else:
            return None
