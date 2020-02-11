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
This module contains tests for the ZionWorx song importer.
"""
from unittest.mock import patch

from openlp.core.common.registry import Registry
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.importers.zionworx import ZionWorxImport
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


<<<<<<< HEAD:tests/functional/openlp_plugins/songs/test_zionworximport.py
TEST_PATH = RESOURCE_PATH / 'songs' / 'zionworx'


class TestZionWorxImport(TestCase):
    """
    Test the functions in the :mod:`zionworximport` module.
    """
    def setUp(self):
        """
        Create the registry
        """
        Registry.create()

    def test_create_importer(self):
        """
        Test creating an instance of the ZionWorx file importer
        """
        # GIVEN: A mocked out SongImport class, and a mocked out "manager"
        with patch('openlp.plugins.songs.lib.importers.zionworx.SongImport'):
            mocked_manager = MagicMock()

            # WHEN: An importer object is created
            importer = ZionWorxImport(mocked_manager, file_paths=[])

            # THEN: The importer should be an instance of SongImport
            assert isinstance(importer, SongImport)


class TestZionWorxFileImport(SongImportTestHelper):

    def __init__(self, *args, **kwargs):
        self.importer_class_name = 'ZionWorxImport'
        self.importer_module_name = 'zionworx'
        super(TestZionWorxFileImport, self).__init__(*args, **kwargs)

    def test_song_import(self):
        """
        Test that loading an ZionWorx file works correctly on various files
        """
        self.file_import(TEST_PATH / 'zionworx.csv', self.load_external_result_data(TEST_PATH / 'zionworx.json'))
=======
@patch('openlp.core.api.http.server.HttpWorker')
@patch('openlp.core.api.http.server.run_thread')
def test_server_start(mocked_run_thread, MockHttpWorker, registry ):
    """
    Test the starting of the Waitress Server with the disable flag set off
    """
    # GIVEN: A new httpserver
    # WHEN: I start the server
    Registry().set_flag('no_web_server', False)
    HttpServer()

    # THEN: the api environment should have been created
    assert mocked_run_thread.call_count == 1, 'The qthread should have been called once'
    assert MockHttpWorker.call_count == 1, 'The http thread should have been called once'


@patch('openlp.core.api.http.server.HttpWorker')
@patch('openlp.core.api.http.server.run_thread')
def test_server_start_not_required(mocked_run_thread, MockHttpWorker, registry):
    """
    Test the starting of the Waitress Server with the disable flag set off
    """
    # GIVEN: A new httpserver
    # WHEN: I start the server
    Registry().set_flag('no_web_server', True)
    HttpServer()

    # THEN: the api environment should have been created
    assert mocked_run_thread.call_count == 0, 'The qthread should not have have been called'
    assert MockHttpWorker.call_count == 0, 'The http thread should not have been called'
>>>>>>> API Test Cleanup:tests/functional/openlp_core/api/http/test_http.py
