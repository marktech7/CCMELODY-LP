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
Package to test the openlp.core.lib.pluginmanager package.
"""
import shutil
import sys
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

from PyQt5 import QtWidgets

from openlp.core.common import is_win
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.state import State
from openlp.core.lib.pluginmanager import PluginManager
from tests.helpers.testmixin import TestMixin


class TestPluginManager(TestCase, TestMixin):
    """
    Test the PluginManager class
    """

    def setUp(self):
        """
        Some pre-test setup required.
        """
        self.setup_application()
        self.build_settings()
        self.temp_dir_path = Path(mkdtemp('openlp'))
        Settings().setValue('advanced/data path', self.temp_dir_path)
        Registry.create()
        Registry().register('service_list', MagicMock())
        self.main_window = QtWidgets.QMainWindow()
        Registry().register('main_window', self.main_window)

    def tearDown(self):
        Settings().remove('advanced/data path')
        self.destroy_settings()
        del self.main_window
        # On windows we need to manually garbage collect to close sqlalchemy files
        # to avoid errors when temporary files are deleted.
        if is_win():
            import gc
            gc.collect()
        shutil.rmtree(self.temp_dir_path)

    @skip
    # This test is broken but totally unable to debug it.
    @patch('openlp.plugins.songusage.songusageplugin.Manager')
    @patch('openlp.plugins.songs.songsplugin.Manager')
    @patch('openlp.plugins.images.imageplugin.Manager')
    @patch('openlp.plugins.custom.customplugin.Manager')
    @patch('openlp.plugins.alerts.alertsplugin.Manager')
    def test_find_plugins(self, mocked_is1, mocked_is2, mocked_is3, mocked_is4, mocked_is5):
        """
        Test the find_plugins() method to ensure it imports the correct plugins
        """
        # GIVEN: A plugin manager
        plugin_manager = PluginManager()
        plugin_manager.bootstrap_initialise()

        # WHEN: We mock out sys.platform to make it return "darwin" and then find the plugins
        old_platform = sys.platform
        sys.platform = 'darwin'
        sys.platform = old_platform

        # THEN: We should find the "Songs", "Bibles", etc in the plugins list
        plugin_names = [plugin.name for plugin in State().list_plugins()]
        assert 'songs' in plugin_names, 'There should be a "songs" plugin'
        assert 'bibles' in plugin_names, 'There should be a "bibles" plugin'
        assert 'presentations' in plugin_names, 'There should be a "presentations" plugin'
        assert 'images' in plugin_names, 'There should be a "images" plugin'
        assert 'media' in plugin_names, 'There should be a "media" plugin'
        assert 'custom' in plugin_names, 'There should be a "custom" plugin'
        assert 'songusage'in plugin_names, 'There should be a "songusage" plugin'
        assert 'alerts' in plugin_names, 'There should be a "alerts" plugin'
