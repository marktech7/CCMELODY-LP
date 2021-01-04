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
from openlp.core.common.mixins import RegistryProperties


class WebSocketPoller(RegistryProperties):
    """
    Accessed by web sockets to get status type information from the application
    """
    def __init__(self):
        """
        Constructor for the web sockets poll builder class.
        """
        super(WebSocketPoller, self).__init__()
        self._previous = {}

    def get_state(self):
        return {'results': {
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

    def get_state_if_changed(self):
        """
        Poll OpenLP to determine current state if it has changed.

        This must only be used by web sockets or else we could miss a state change.

        :return: The current application state or None if unchanged since last call
        """
        current = self.get_state()
        if self._previous != current:
            self._previous = current
            return current
        else:
            return None
