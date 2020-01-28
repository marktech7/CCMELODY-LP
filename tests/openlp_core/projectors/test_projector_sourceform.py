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
:mod: `tests.interfaces.openlp_core_ui.test_projectorsourceform` module

Tests for the Projector Source Select form.
"""
import os
import time
from unittest import TestCase
from unittest.mock import patch

from PyQt5.QtWidgets import QDialog

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.projectors.constants import PJLINK_DEFAULT_CODES, PJLINK_DEFAULT_SOURCES
from openlp.core.projectors.db import Projector, ProjectorDB
from openlp.core.projectors.sourceselectform import SourceSelectSingle, source_group
from tests.helpers.testmixin import TestMixin
from tests.resources.projector.data import TEST1_DATA, TEST_DB


def build_source_dict():
    """
    Builds a source dictionary to verify source_group returns a valid dictionary of dictionary items

    :returns: dictionary of valid PJLink source codes grouped by PJLink source group
    """
    test_group = {}
    for group in PJLINK_DEFAULT_SOURCES.keys():
        test_group[group] = {}
    for key in PJLINK_DEFAULT_CODES:
        test_group[key[0]][key] = PJLINK_DEFAULT_CODES[key]
    return test_group


class ProjectorSourceFormTest(TestCase, TestMixin):
    """
    Test class for the Projector Source Select form module
    """
    @patch('openlp.core.projectors.db.init_url')
    def setUp(self, mocked_init_url):
        """
        Set up anything necessary for all tests
        """
        mocked_init_url.return_value = 'sqlite:///{}'.format(TEST_DB)
        self.setup_application()
        self.build_settings()
        Registry.create()
        Registry().register('settings', Settings())

        # Do not try to recreate if we've already been created from a previous test
        if not hasattr(self, 'projectordb'):
            self.projectordb = ProjectorDB()
        # Retrieve/create a database record
        self.projector = self.projectordb.get_projector_by_ip(TEST1_DATA['ip'])
        if not self.projector:
            self.projectordb.add_projector(projector=Projector(**TEST1_DATA))
            self.projector = self.projectordb.get_projector_by_ip(TEST1_DATA['ip'])
        self.projector.dbid = self.projector.id
        self.projector.db_item = self.projector

    def tearDown(self):
        """
        Close database session.
        Delete all C++ objects at end so we don't segfault.
        """
        self.projectordb.session.close()
        del self.projectordb
        del self.projector
        retries = 0
        while retries < 5:
            try:
                if os.path.exists(TEST_DB):
                    os.unlink(TEST_DB)
                break
            except Exception:
                time.sleep(1)
                retries += 1
        self.destroy_settings()

    def test_source_dict(self):
        """
        Test that source list dict returned from sourceselectform module is a valid dict with proper entries
        """
        # GIVEN: A list of inputs
        codes = []
        for item in PJLINK_DEFAULT_CODES.keys():
            codes.append(item)
        codes.sort()

        # WHEN: projector.sourceselectform.source_select() is called
        check = source_group(codes, PJLINK_DEFAULT_CODES)

        # THEN: return dictionary should match test dictionary
        assert check == build_source_dict(), "Source group dictionary should match test dictionary"

    @patch.object(QDialog, 'exec')
    def test_source_select_edit_button(self, mocked_qdialog):
        """
        Test source select form edit has Ok, Cancel, Reset, and Revert buttons
        """
        # GIVEN: Initial setup and mocks
        self.projector.source_available = ['11', ]
        self.projector.source = '11'

        # WHEN we create a source select widget and set edit=True
        select_form = SourceSelectSingle(parent=None, projectordb=self.projectordb)
        select_form.edit = True
        select_form.exec(projector=self.projector)

        # THEN: Verify all 4 buttons are available
        assert len(select_form.button_box.buttons()) == 4, \
            'SourceSelect dialog box should have "OK", "Cancel", "Rest", and "Revert" buttons available'

    @patch.object(QDialog, 'exec')
    def test_source_select_noedit_button(self, mocked_qdialog):
        """
        Test source select form view has OK and Cancel buttons only
        """
        # GIVEN: Initial setup and mocks
        self.projector.source_available = ['11', ]
        self.projector.source = '11'

        # WHEN we create a source select widget and set edit=False
        select_form = SourceSelectSingle(parent=None, projectordb=self.projectordb)
        select_form.edit = False
        select_form.exec(projector=self.projector)

        # THEN: Verify only 2 buttons are available
        assert len(select_form.button_box.buttons()) == 2, \
            'SourceSelect dialog box should only have "OK" and "Cancel" buttons available'
