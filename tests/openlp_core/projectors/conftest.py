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
Fixtures for projector tests
"""
import os
import pytest

from unittest.mock import patch

from openlp.core.projectors.db import Projector, ProjectorDB
from openlp.core.projectors.editform import ProjectorEditForm
from openlp.core.projectors.manager import ProjectorManager
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST_DB, TEST1_DATA, TEST2_DATA, TEST3_DATA

'''
NOTE: Since Registry is a singleton, sleight of hand allows us to verify
      calls to Registry.methods()

@patch(path.to.imported.Registry)
def test_function(mock_registry):
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    ...
    assert mocked_registry.method.has_call(...)
'''


@pytest.fixture()
def projectordb(temp_folder, settings):
    """
    Provides a projector database with 3 test records
    """
    tmpdb_url = f'sqlite:///{os.path.join(temp_folder, TEST_DB)}'
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = tmpdb_url
        proj = ProjectorDB()
    proj.add_projector(Projector(**TEST1_DATA))
    proj.add_projector(Projector(**TEST2_DATA))
    proj.add_projector(Projector(**TEST3_DATA))
    yield proj
    proj.session.close()
    del proj


@pytest.fixture()
def projectordb_mtdb(temp_folder, settings):
    """
    Provides an empty projector database
    """
    tmpdb_url = f'sqlite:///{os.path.join(temp_folder, TEST_DB)}'
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = tmpdb_url
        proj = ProjectorDB()
    yield proj
    proj.session.close()
    del proj


@pytest.fixture()
def projector_manager(projectordb, settings):
    """
    Provides ProjectorManager with a populated ProjectorDB
    """
    proj_manager = ProjectorManager(projectordb=projectordb)
    yield proj_manager
    projectordb.session.close()
    del proj_manager


@pytest.fixture()
def projector_manager_nodb(settings):
    """
    Provides ProjectorManager with no previously defined ProjectorDB
    """
    proj_manager = ProjectorManager(projectordb=None)
    yield proj_manager
    del proj_manager


@pytest.fixture()
def projector_manager_mtdb(projectordb_mtdb, settings):
    """
    Provides a ProjectorManager with an empty ProjectorDB
    """
    t_manager = ProjectorManager(projectordb=projectordb_mtdb)
    yield t_manager
    del t_manager


@pytest.fixture()
def projector_editform(projectordb):
    """
    Provides ProjectorEditForm with mocked QMessageBox, QDialog and populated ProjectorDB
    """
    with patch('openlp.core.projectors.editform.QtWidgets.QMessageBox') as mock_msg_box, \
         patch('openlp.core.projectors.editform.QtWidgets.QDialog') as mock_dialog_box, \
         patch.object(ProjectorEditForm, 'updateProjectors') as mock_update, \
         patch.object(ProjectorEditForm, 'close') as mock_close:

        _form = ProjectorEditForm(projectordb=projectordb)
        _form.mock_msg_box = mock_msg_box
        _form.mock_dialog_box = mock_dialog_box
        _form.mock_updateProjectors = mock_update
        _form.mock_close = mock_close
        yield _form
    del _form


@pytest.fixture()
def projector_editform_mtdb(projectordb_mtdb):
    """
    Provides ProjectorEditForm with mocked QMessageBox, QDialog and empty ProjectorDB
    """
    with patch('openlp.core.projectors.editform.QtWidgets.QMessageBox') as mock_msg_box, \
         patch('openlp.core.projectors.editform.QtWidgets.QDialog') as mock_dialog_box, \
         patch.object(ProjectorEditForm, 'updateProjectors') as mock_update, \
         patch.object(ProjectorEditForm, 'close') as mock_close:

        _form = ProjectorEditForm(projectordb=projectordb)
        _form.mock_msg_box = mock_msg_box
        _form.mock_dialog_box = mock_dialog_box
        _form.mock_updateProjectors = mock_update
        _form.mock_close = mock_close
        yield _form
    del _form


@pytest.fixture()
def pjlink():
    """
    Provides a PJLink instance with TEST1_DATA
    """
    pj_link = PJLink(Projector(**TEST1_DATA), no_poll=True)
    yield pj_link
    del pj_link
