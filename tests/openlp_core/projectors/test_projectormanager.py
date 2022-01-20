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
Interface tests to test the themeManager class and related methods.
"""
import pytest
import logging

from unittest.mock import MagicMock, patch

from openlp.core.projectors.db import ProjectorDB
from openlp.core.projectors.editform import ProjectorEditForm
from openlp.core.projectors.manager import ProjectorManager
from tests.resources.projector.data import TEST_DB


@pytest.fixture()
def projector_manager(settings):
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = 'sqlite:///%s' % TEST_DB
        projectordb = ProjectorDB()
        proj_manager = ProjectorManager(projectordb=projectordb)
        yield proj_manager
        projectordb.session.close()
        del proj_manager


@pytest.fixture()
def projector_manager_nodb(settings):
    proj_manager = ProjectorManager(projectordb=None)
    yield proj_manager
    del proj_manager


def test_bootstrap_initialise(projector_manager):
    """
    Test initialize calls correct startup functions
    """
    # WHEN: we call bootstrap_initialise
    projector_manager.bootstrap_initialise()
    # THEN: ProjectorDB is setup
    assert type(projector_manager.projectordb) == ProjectorDB, \
        'Initialization should have created a ProjectorDB() instance'


def test_bootstrap_initialise_nodb(projector_manager_nodb, caplog):
    """
    Test log entry creating new projector DB
    """
    caplog.set_level(logging.DEBUG)

    # WHEN: ProjectorManager created with no DB set
    caplog.clear()
    projector_manager_nodb.bootstrap_initialise()
    # THEN: Log should indicate new DB being created
    assert caplog.record_tuples[3] == ('openlp.core.projectors.manager', 10, 'Creating new ProjectorDB() instance'), \
        "ProjectorManager should have indicated a new DB being created"


def test_bootstrap_post_set_up(projector_manager):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: setup mocks
    projector_manager._load_projectors = MagicMock()

    # WHEN: Call to initialize is run
    projector_manager.bootstrap_initialise()
    projector_manager.bootstrap_post_set_up()

    # THEN: verify calls to retrieve saved projectors and edit page initialized
    assert 1 == projector_manager._load_projectors.call_count, \
        'Initialization should have called load_projectors()'
    assert type(projector_manager.projector_form) == ProjectorEditForm, \
        'Initialization should have created a Projector Edit Form'
    assert projector_manager.projectordb is projector_manager.projector_form.projectordb, \
        'ProjectorEditForm should be using same ProjectorDB() instance as ProjectorManager'
