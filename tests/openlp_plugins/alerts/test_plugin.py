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
This module contains tests for the plugin class Alerts plugin.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.plugins.alerts.alertsplugin import AlertsPlugin


@pytest.fixture
@patch('openlp.plugins.alerts.alertsplugin.Manager')
def plugin_env(MockedManager, settings, state, registry):
    """An instance of the AlertsPlugin"""
    mocked_manager = MagicMock()
    MockedManager.return_value = mocked_manager
    return AlertsPlugin(), settings


def test_plugin_about():
    result = AlertsPlugin.about()

    assert result == (
        '<strong>Alerts Plugin</strong>'
        '<br />The alert plugin controls the displaying of alerts on the display screen.'
    )


def test_plugin_state(plugin_env):
    plugin = plugin_env[0]
    settings = plugin_env[1]
    plugin.alerts_active = settings.value('alerts/status')
    plugin.toggle_alerts_state()
    assert settings.value('alerts/status') != plugin.alerts_active
