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
This module contains tests for the lib submodule of the Images plugin.
"""
import os
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase, skip
from unittest.mock import patch

from openlp.core.common.applocation import AppLocation
from openlp.core.common.settings import Settings
from openlp.core.lib.db import Manager
from openlp.plugins.images.lib import upgrade
from openlp.plugins.images.lib.db import ImageFilenames, init_schema
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import TEST_RESOURCES_PATH


__default_settings__ = {
    'images/db type': 'sqlite',
    'images/background color': '#000000',
}


class TestImageDBUpgrade(TestCase, TestMixin):
    """
    Test that the image database is upgraded correctly
    """
    def setUp(self):
        self.build_settings()
        Settings().extend_default_settings(__default_settings__)
        self.tmp_folder = mkdtemp()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.destroy_settings()
        # Ignore errors since windows can have problems with locked files
        shutil.rmtree(self.tmp_folder, ignore_errors=True)

    @skip
    # Broken due to Path issues.
    def test_image_filenames_table(self):
        """
        Test that the ImageFilenames table is correctly upgraded to the latest version
        """
        # GIVEN: An unversioned image database
        temp_db_name = os.path.join(self.tmp_folder, 'image-v0.sqlite')
        shutil.copyfile(os.path.join(TEST_RESOURCES_PATH, 'images', 'image-v0.sqlite'), temp_db_name)

        with patch.object(AppLocation, 'get_data_path', return_value=Path('/', 'test', 'dir')):
            # WHEN: Initalising the database manager
            manager = Manager('images', init_schema, db_file_path=Path(temp_db_name), upgrade_mod=upgrade)

            # THEN: The database should have been upgraded and image_filenames.file_path should return Path objects
            upgraded_results = manager.get_all_objects(ImageFilenames)

            expected_result_data = {1: Path('/', 'test', 'image1.jpg'),
                                    2: Path('/', 'test', 'dir', 'image2.jpg'),
                                    3: Path('/', 'test', 'dir', 'subdir', 'image3.jpg')}

            assert len(upgraded_results) == 3
            for result in upgraded_results:
                assert expected_result_data[result.id] == result.file_path
