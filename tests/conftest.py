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
All the tests
"""
import os
from tempfile import mkstemp

import pytest
from PyQt5 import QtCore, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


@pytest.yield_fixture
def qapp():
    """An instance of QApplication"""
    app = QtWidgets.QApplication([])
    yield app
    del app


@pytest.yield_fixture
def settings(qapp):
    """A Settings() instance"""
    fd, ini_file = mkstemp('.ini')
    Settings.set_filename(ini_file)
    Registry.create()
    Settings().setDefaultFormat(QtCore.QSettings.IniFormat)
    # Needed on windows to make sure a Settings object is available during the tests
    sets = Settings()
    sets.setValue('themes/global theme', 'my_theme')
    Registry().register('settings', set)
    yield sets
    del sets
    os.close(fd)
    os.unlink(Settings().fileName())


@pytest.fixture
def registry():
    """An instance of the Registry"""
    Registry.create()
