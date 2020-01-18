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
All the tests
"""
import os
import sys
from tempfile import mkstemp
from unittest.mock import MagicMock

import pytest
from PyQt5 import QtCore, QtWidgets  # noqa
sys.modules['PyQt5.QtWebEngineWidgets'] = MagicMock()

from openlp.core.app import OpenLP
from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


@pytest.yield_fixture
def qapp():
    """An instance of QApplication"""
    app = OpenLP()
    yield app
    del app


@pytest.yield_fixture
def mocked_qapp():
    """A mocked instance of QApplication"""
    app = MagicMock()
    yield app
    del app


@pytest.fixture
def registry():
    """An instance of the Registry"""
    Registry.create()


@pytest.yield_fixture
def settings(qapp, registry):
    """A Settings() instance"""
    fd, ini_file = mkstemp('.ini')
    Settings.set_filename(ini_file)
    Settings().setDefaultFormat(QtCore.QSettings.IniFormat)
    # Needed on windows to make sure a Settings object is available during the tests
    sets = Settings()
    sets.setValue('themes/global theme', 'my_theme')
    Registry().register('settings', sets)
    yield sets
    del sets
    os.close(fd)
    os.unlink(Settings().fileName())


@pytest.yield_fixture
def mock_settings(registry):
    """A Mock Settings() instance"""
    # Create and register a mock settings object to work with
    mock_settings = MagicMock()
    Registry().register('settings', mock_settings)
    yield mock_settings
    Registry().remove('settings')
    del mock_settings


@pytest.fixture(scope='function')
def state():
    State().load_settings()
