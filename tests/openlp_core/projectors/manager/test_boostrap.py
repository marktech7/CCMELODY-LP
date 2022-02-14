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
Test ProjectorManager.bootstrap_* methods
"""
import logging

from unittest.mock import MagicMock, patch

from openlp.core.projectors.db import ProjectorDB
from openlp.core.projectors.editform import ProjectorEditForm


def test_bootstrap_initialise(projector_manager_memdb):
    """
    Test initialize calls correct startup functions
    """
    # WHEN: we call bootstrap_initialise
    projector_manager_memdb.bootstrap_initialise()
    # THEN: ProjectorDB is setup
    assert type(projector_manager_memdb.projectordb) is ProjectorDB, \
        'Initialization should have created a ProjectorDB() instance'


def test_bootstrap_initialise_nodb(projector_manager_nodb, caplog):
    """
    Test log entry creating new projector DB
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    log_entries = 'Creating new ProjectorDB() instance'

    # WHEN: ProjectorManager created with no DB set
    caplog.clear()
    projector_manager_nodb.bootstrap_initialise()
    # THEN: Log should indicate new DB being created
    assert caplog.messages[3] == log_entries, "ProjectorManager should have indicated a new DB being created"


def test_bootstrap_post_set_up(projector_manager_memdb):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: setup mocks
    projector_manager_memdb._load_projectors = MagicMock()

    # WHEN: Call to initialize is run
    projector_manager_memdb.bootstrap_initialise()
    projector_manager_memdb.bootstrap_post_set_up()

    # THEN: verify calls to retrieve saved projectors and edit page initialized
    assert 1 == projector_manager_memdb._load_projectors.call_count, \
        'Initialization should have called load_projectors()'
    assert type(projector_manager_memdb.projector_form) == ProjectorEditForm, \
        'Initialization should have created a Projector Edit Form'
    assert projector_manager_memdb.projectordb is projector_manager_memdb.projector_form.projectordb, \
        'ProjectorEditForm should be using same ProjectorDB() instance as ProjectorManager'


def test_bootstrap_post_set_up_autostart_projector(projector_manager_memdb, caplog):
    """
    Test post-initialize calling log and QTimer on autostart
    """
    # GIVEN: Setup mocks
    caplog.set_level(logging.DEBUG)
    log_entries = 'Delaying 1.5 seconds before loading all projectors'

    with patch('openlp.core.projectors.manager.QtCore.QTimer.singleShot') as mock_timer:
        # WHEN: Initializations called
        projector_manager_memdb.bootstrap_initialise()
        projector_manager_memdb.autostart = True
        projector_manager_memdb.bootstrap_post_set_up()

        # THEN: verify log entries and timer calls
        mock_timer.assert_called_once_with(1500, projector_manager_memdb._load_projectors)
        assert caplog.messages[-1] == log_entries, "Invalid log entries"
