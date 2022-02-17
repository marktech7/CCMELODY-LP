# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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
This module contains tests for the lib submodule of the Remotes plugin.
"""
import hashlib
from unittest.mock import MagicMock, patch
import pytest
import re

from PyQt5 import QtWidgets

from openlp.core.api.tab import ApiTab
from openlp.core.common import get_network_interfaces
from openlp.core.common.registry import Registry

ZERO_URL = '0.0.0.0'


@pytest.fixture
def api_tab(settings):
    Registry().set_flag('website_version', '00-00-0000')
    Registry().set_flag('no_web_server', False)
    parent = QtWidgets.QMainWindow()
    form = ApiTab(parent)
    yield form
    del parent
    del form


def test_get_ip_address_default(api_tab):
    """
    Test the get_ip_address function with ZERO_URL
    """
    # GIVEN: list of local IP addresses for this machine
    ip_addresses = []
    interfaces = get_network_interfaces()
    for _, interface in interfaces.items():
        ip_addresses.append(interface['ip'])

    # WHEN: the default ip address is given
    ip_address = api_tab.get_ip_address(ZERO_URL)

    # THEN: the default ip address will be returned
    assert re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_address), \
        'The return value should be a valid ip address'
    assert ip_address in ip_addresses, 'The return address should be in the list of local IP addresses'


def test_get_ip_address_with_ip(api_tab):
    """
    Test the get_ip_address function with given ip address
    """
    # GIVEN: An ip address
    given_ip = '192.168.1.1'

    # WHEN: the default ip address is given
    ip_address = api_tab.get_ip_address(given_ip)

    # THEN: the default ip address will be returned
    assert ip_address == given_ip, 'The return value should be %s' % given_ip


def test_set_urls(api_tab):
    """
    Test the set_url function to generate correct url links
    """
    # GIVEN: An ip address
    api_tab.address_edit.setText('192.168.1.1')
    # WHEN: the urls are generated
    api_tab.set_urls()
    # THEN: the following links are returned
    assert api_tab.remote_url.text() == "<a href=\"http://192.168.1.1:4316/\">http://192.168.1.1:4316/</a>", \
        'The return value should be a fully formed link'
    assert api_tab.stage_url.text() == \
        "<a href=\"http://192.168.1.1:4316/stage\">http://192.168.1.1:4316/stage</a>", \
        'The return value should be a fully formed stage link'
    assert api_tab.live_url.text() == \
        "<a href=\"http://192.168.1.1:4316/main\">http://192.168.1.1:4316/main</a>", \
        'The return value should be a fully formed main link'
    assert api_tab.chords_url.text() == \
        "<a href=\"http://192.168.1.1:4316/chords\">http://192.168.1.1:4316/chords</a>", \
        'The return value should be a fully formed chords link'
    assert hashlib.sha256(api_tab.app_qr_code_label.text().encode()).hexdigest() \
           == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Incorrect QR Code generated'


def test_address_revert_button_clicked(api_tab, settings):
    """
    Test the IP revert function works
    """
    # GIVEN: The ip address text set to a non default value
    api_tab.address_edit.setText('not the default')
    # WHEN: address_revert_button_clicked is called
    api_tab.address_revert_button_clicked()
    # THEN: The text should have been changed to the default value
    assert api_tab.address_edit.text() == settings.get_default_value('api/ip address')


def test_save(api_tab, settings):
    """
    Test the save function works
    """
    # GIVEN: Some example remote data
    api_tab.address_edit.setText(settings.value('api/ip address'))
    api_tab.twelve_hour = True
    api_tab.thumbnails = True
    api_tab.user_login_group_box.setChecked(True)
    api_tab.user_id.setText('user id thing')
    api_tab.password.setText('user password thing')
    # WHEN: save is called
    api_tab.save()
    # THEN: The text should have been changed to provided values
    assert settings.value('api/twelve hour') is True
    assert settings.value('api/thumbnails') is True
    assert settings.value('api/authentication enabled') is True
    assert settings.value('api/user id') == 'user id thing'
    assert settings.value('api/password') == 'user password thing'


@patch('openlp.core.api.tab.QtWidgets.QMessageBox')
def test_different_ip_save_shows_restart_message(mock_qmessagebox, api_tab, settings):
    """
    Test if the "change will only take effect on restart" is presented after IP change.
    """
    # GIVEN: The ip address text set to a non default value and a mocked QMessageBox
    mock_qmessagebox.information = MagicMock()
    api_tab.address_edit.setText('not the default')
    api_tab._settings_form = MagicMock()
    # WHEN: save is called
    api_tab.save()
    # THEN: The messagebox should be shown
    mock_qmessagebox.information.assert_called_once()
