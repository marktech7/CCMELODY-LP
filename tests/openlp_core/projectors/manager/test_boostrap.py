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
import openlp.core.projectors.manager

from unittest.mock import DEFAULT, MagicMock, patch

test_module = openlp.core.projectors.manager.__name__


def test_bootstrap_initialise(projector_manager, caplog):
    """
    Test ProjectorManager initializes with existing ProjectorDB instance
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Using existing ProjectorDB() instance')]

    with patch.multiple(projector_manager,
                        setup_ui=DEFAULT,
                        get_settings=DEFAULT) as mock_manager, \
         patch('openlp.core.projectors.manager.ProjectorDB') as mock_db:

        # WHEN: we call bootstrap_initialise
        caplog.clear()
        projector_manager.bootstrap_initialise()

        # THEN: Appropriate entries and actions
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_manager['setup_ui'].assert_called_once()
        mock_manager['get_settings'].assert_called_once()
        mock_db.assert_not_called()


def test_bootstrap_initialise_nodb(projector_manager_nodb, caplog):
    """
    Test ProjectorManager initializes with a new ProjectorDB instance
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Creating new ProjectorDB() instance')]

    with patch.multiple(projector_manager_nodb,
                        setup_ui=DEFAULT,
                        get_settings=DEFAULT) as mock_manager, \
         patch('openlp.core.projectors.manager.ProjectorDB') as mock_db:

        # WHEN: we call bootstrap_initialise
        caplog.clear()
        projector_manager_nodb.bootstrap_initialise()

        # THEN: Appropriate entries and actions
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_manager['setup_ui'].assert_called_once()
        mock_manager['get_settings'].assert_called_once()
        mock_db.assert_called_once()


def test_bootstrap_post_set_up_autostart_false(projector_manager_memdb, settings, caplog):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Loading all projectors')]

    mock_timer = MagicMock()
    mock_newProjector = MagicMock()
    mock_editProjector = MagicMock()
    mock_edit = MagicMock()
    mock_edit.newProjector = mock_newProjector
    mock_edit.editProjector = mock_editProjector

    settings.setValue('projector/connect on start', False)
    projector_manager_memdb.bootstrap_initialise()

    with patch('openlp.core.projectors.manager.ProjectorEditForm') as mocked_edit, \
         patch('openlp.core.projectors.manager.QtCore') as mock_core, \
         patch.multiple(projector_manager_memdb,
                        _load_projectors=DEFAULT,
                        projector_list_widget=DEFAULT) as mock_manager:
        mocked_edit.return_value = mock_edit
        mock_core.QTimer = mock_timer

        # WHEN: Call to initialize is run
        caplog.clear()
        projector_manager_memdb.bootstrap_post_set_up()

        # THEN: verify calls and logs
        mock_timer.singleShot.assert_not_called()
        mock_newProjector.connect.assert_called_once()
        mock_editProjector.connect.assert_called_once()
        mock_manager['_load_projectors'].assert_called_once(),
        mock_manager['projector_list_widget'].itemSelectionChanged.connect.assert_called_once()
        assert caplog.record_tuples == logs, 'Invalid log entries'


def test_bootstrap_post_set_up_autostart_true(projector_manager_memdb, settings, caplog):
    """
    Test post-initialize calls proper setups
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Delaying 1.5 seconds before loading all projectors')]

    mock_qtimer = MagicMock()
    mock_newProjector = MagicMock()
    mock_editProjector = MagicMock()
    mock_edit = MagicMock()
    mock_edit.newProjector = mock_newProjector
    mock_edit.editProjector = mock_editProjector

    settings.setValue('projector/connect on start', True)
    projector_manager_memdb.bootstrap_initialise()

    with patch('openlp.core.projectors.manager.ProjectorEditForm') as mocked_edit, \
         patch('openlp.core.projectors.manager.QtCore') as mock_core, \
         patch.multiple(projector_manager_memdb,
                        setup_ui=DEFAULT,
                        _load_projectors=DEFAULT,
                        projector_list_widget=DEFAULT) as mock_manager:
        mocked_edit.return_value = mock_edit
        mock_core.QTimer = mock_qtimer

        # WHEN: Call to initialize is run
        caplog.clear()
        projector_manager_memdb.bootstrap_post_set_up()

        # THEN: verify calls and logs
        mock_qtimer.assert_called_once()
        mock_newProjector.connect.assert_called_once()
        mock_editProjector.connect.assert_called_once()
        mock_manager['_load_projectors'].assert_not_called(),
        mock_manager['projector_list_widget'].itemSelectionChanged.connect.assert_called_once()
        assert caplog.record_tuples == logs, 'Invalid log entries'
