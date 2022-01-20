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

from openlp.core.projectors.constants import PJLINK_PORT
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


def test_bootstrap_post_set_up_autostart_projector(projector_manager_nodb, caplog):
    """
    Test post-initialize calling log and QTimer on autostart
    """
    # GIVEN: Setup mocks
    with patch('openlp.core.projectors.manager.QtCore.QTimer.singleShot') as mock_timer:
        caplog.set_level(logging.DEBUG)
        # WHEN: Initializations called
        projector_manager_nodb.bootstrap_initialise()
        projector_manager_nodb.autostart = True
        projector_manager_nodb.bootstrap_post_set_up()

        # THEN: verify log entries and timer calls
        mock_timer.assert_called_once_with(1500, projector_manager_nodb._load_projectors)
        assert caplog.record_tuples[-1] == ('openlp.core.projectors.manager', 10,
                                            'Delaying 1.5 seconds before loading all projectors'), \
            "Last log entry should be autoloading entry"


def test_udp_listen_add_duplicate_port(projector_manager_nodb, caplog):
    """
    Test adding UDP port listener to port already registered
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    projector_manager_nodb.pjlink_udp[PJLINK_PORT] = "Something to set index item"

    # WHEN: udp_listen_add is called with duplicate port number
    caplog.clear()
    projector_manager_nodb.udp_listen_add(port=PJLINK_PORT)

    # THEN: Verify log entry and registry entry not called
    assert caplog.record_tuples[0] == ('openlp.core.projectors.manager', 30,
                                       'UDP Listener for port 4352 already added - skipping')


@patch('openlp.core.projectors.manager.Registry')
def test_udp_listen_add_new(mock_registry, projector_manager_nodb, caplog):
    """
    Test adding new UDP port listener
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    log_entries = [('openlp.core.projectors.manager', 10, 'Adding UDP listener on port 4352'),
                   ('openlp.core.projectors.pjlink', 10, '(UDP:4352) PJLinkUDP() Initialized')]
    # WHEN: Adding new listener
    caplog.clear()
    projector_manager_nodb.udp_listen_add(port=PJLINK_PORT)

    # THEN: Appropriate listener and log entries
    mock_registry.execute.called_with('udp_broadcast_add', port=PJLINK_PORT)
    assert caplog.record_tuples == log_entries, 'Invalid log entries'
