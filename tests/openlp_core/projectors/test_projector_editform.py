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
Interface tests to test the openlp.core.projectors.editform.ProjectorEditForm()
class and methods.
"""
import pytest
from unittest.mock import patch

from openlp.core.projectors.db import Projector, ProjectorDB
from openlp.core.projectors.editform import ProjectorEditForm
from tests.resources.projector.data import TEST1_DATA, TEST_DB


@pytest.yield_fixture()
def projector_form(settings):
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = 'sqlite:///' + TEST_DB
        projectordb = ProjectorDB()
        projector_frm = ProjectorEditForm(projectordb=projectordb)
        yield projector_frm
        projectordb.session.close()
        del projector_frm


@patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec')
def test_edit_form_add_projector(mocked_exec, projector_form):
    """
    Test projector edit form with no parameters creates a new entry.

    :return: None
    """
    # GIVEN: Mocked setup
    # WHEN: Calling edit form with no parameters
    projector_form.exec()
    item = projector_form.projector

    # THEN: Should be creating a new instance
    assert projector_form.new_projector, 'Projector edit form should be marked as a new entry'
    assert (item.ip is None and item.name is None), 'Projector edit form should have a new Projector() instance to edit'


@patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec')
def test_edit_form_edit_projector(mocked_exec, projector_form):
    """
    Test projector edit form with existing projector entry

    :return:
    """
    # GIVEN: Mocked setup
    # WHEN: Calling edit form with existing projector instance
    projector_form.exec(projector=Projector(**TEST1_DATA))
    item = projector_form.projector

    # THEN: Should be editing an existing entry
    assert projector_form.new_projector is False, 'Projector edit form should be marked as existing entry'
    assert item.ip is TEST1_DATA['ip'] and item.name is TEST1_DATA['name'], \
        'Projector edit form should have TEST1_DATA() instance to edit'
