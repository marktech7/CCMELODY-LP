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


class FakeProjector(object):
    """
    Helper test class
    """
    def __init__(self, port=4352, name="Faker"):
        self.link = self
        self.port = port
        self.name = name


class FakePJLinkUDP(object):
    """
    Helper test class
    """
    def __init__(self, *args, **kwargs):
        pass

    def check_settings(self, *args, **kwargs):
        pass


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
    log_entries = 'Creating new ProjectorDB() instance'
    # WHEN: ProjectorManager created with no DB set
    caplog.clear()
    projector_manager_nodb.bootstrap_initialise()
    # THEN: Log should indicate new DB being created
    assert caplog.messages[3] == log_entries, "ProjectorManager should have indicated a new DB being created"


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
        log_entries = 'Delaying 1.5 seconds before loading all projectors'
        # WHEN: Initializations called
        projector_manager_nodb.bootstrap_initialise()
        projector_manager_nodb.autostart = True
        projector_manager_nodb.bootstrap_post_set_up()

        # THEN: verify log entries and timer calls
        mock_timer.assert_called_once_with(1500, projector_manager_nodb._load_projectors)
        assert caplog.messages[-1] == log_entries, "Invalid log entries"


def test_udp_listen_add_duplicate(projector_manager_nodb, caplog):
    """
    Test adding UDP port listener to port already registered
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    log_entries = ['UDP Listener for port 10 already added - skipping']
    port_list = {10: 'port1', 20: 'port2'}
    projector_manager_nodb.pjlink_udp = port_list

    # WHEN: udp_listen_add is called with duplicate port number
    caplog.clear()
    projector_manager_nodb.udp_listen_add(port=10)

    # THEN: Verify log entry and registry entry not called
    assert projector_manager_nodb.pjlink_udp == port_list, "Invalid ports in list"
    assert caplog.messages == log_entries, "Invalid log entries"


@patch('openlp.core.projectors.manager.PJLinkUDP')
@patch('openlp.core.projectors.manager.Registry')
def test_udp_listen_add_new(mock_registry, mock_udp, projector_manager_nodb, caplog):
    """
    Test adding new UDP port listener
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    mock_udp.return_value = FakePJLinkUDP()
    log_entries = ['Adding UDP listener on port 20']
    projector_manager_nodb.pjlink_udp = {10: 'port1'}
    # WHEN: Adding new listener
    caplog.clear()
    projector_manager_nodb.udp_listen_add(port=20)
    # THEN: Appropriate listener and log entries
    assert 20 in projector_manager_nodb.pjlink_udp, "Port not added"
    assert 2 == len(projector_manager_nodb.pjlink_udp), "Invalid ports in list"
    assert type(projector_manager_nodb.pjlink_udp[20]) == FakePJLinkUDP, \
        'PJLinkUDP instance should have been added'
    assert mocked_registry.execute.has_call('udp_broadcast_add', port=20)
    assert caplog.messages == log_entries, 'Invalid log entries'


def test_udp_listen_delete_missing(projector_manager_nodb, caplog):
    """
    Test deleting UDP port listener not in list
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    projector_manager_nodb.pjlink_udp = {10: 'port1'}
    log_entries = ['Checking for UDP port 20 listener deletion',
                   'UDP listener for port 20 not there - skipping delete']
    # WHEN: Deleting port listener from dictinary
    projector_manager_nodb.udp_listen_delete(port=20)
    # THEN: Log missing port and exit method
    assert projector_manager_nodb.pjlink_udp == {10: 'port1'}, "Invalid ports in list"
    assert caplog.messages == log_entries, "Invalid log entries"


@patch('openlp.core.projectors.manager.Registry')
def test_udp_listen_delete_single(mock_registry, projector_manager_nodb, caplog):
    """
    Test deleting UDP listener
    """
    # GIVEN: Initial setup
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    caplog.set_level(logging.DEBUG)
    log_entries = ['Checking for UDP port 10 listener deletion',
                   'UDP listener for port 10 deleted']
    port_list = {20: 'port2'}
    projector_manager_nodb.pjlink_udp = {10: 'port1', **port_list}
    projector_manager_nodb.projector_list = [FakeProjector(port=20)]
    # WHEN: deleting a listener
    caplog.clear()
    projector_manager_nodb.udp_listen_delete(port=10)
    # THEN: pjlink_udp and logs should have appropriate entries
    assert caplog.messages == log_entries, 'Invalid log entries'
    assert projector_manager_nodb.pjlink_udp == port_list, 'Invalid ports in list'
    assert mocked_registry.execute.has_call('udp_broadcast_delete', port=10)


def test_udp_listen_delete_skip(projector_manager_nodb, caplog):
    """
    Test not deleting UDP listener
    """
    # GIVEN: Initial setup
    caplog.set_level(logging.DEBUG)
    log_entries = ['Checking for UDP port 10 listener deletion',
                   'UDP listener for port 10 needed for other projectors - skipping delete']
    port_list = {10: 'port1', 20: 'port2'}
    projector_manager_nodb.pjlink_udp = port_list
    projector_manager_nodb.projector_list = [FakeProjector(port=10),
                                             FakeProjector(port=20)]
    # WHEN: deleting a listener
    caplog.clear()
    projector_manager_nodb.udp_listen_delete(port=10)
    print(projector_manager_nodb.pjlink_udp)
    print(caplog.record_tuples)
    # THEN: pjlink_udp and logs should have appropriate entries
    assert caplog.messages == log_entries, 'Invalid log entries'
    assert projector_manager_nodb.pjlink_udp == port_list, 'Invalid ports in list'
