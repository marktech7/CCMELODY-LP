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
Test misc. functions with few test paths

_load_projectors()
add_projector_from_wizard()
get_projector_list()

NOTE: Mock udp_listen_add and udp_listen_delete to keep Registry from
      spouting multiple failed exec calls
"""

import openlp.core.projectors.db
import openlp.core.projectors.manager

from unittest.mock import DEFAULT, patch

from openlp.core.projectors.db import Projector

from tests.resources.projector.data import TEST1_DATA, TEST2_DATA, TEST3_DATA


@patch.multiple(openlp.core.projectors.manager.ProjectorManager,
                udp_listen_add=DEFAULT,
                udp_listen_delete=DEFAULT)
def test_private_load_projectors(projector_manager, **kwargs):
    """
    Test that _load_projectors() retrieves all entries from projector database
    """
    # GIVEN: Test environment
    t_db = projector_manager.projectordb  # Shortcut helper
    t_list = t_db.get_projector_all()

    # Mock _load_projectors before bootstrap so we can test it
    with patch.object(projector_manager, '_load_projectors'):
        projector_manager.bootstrap_initialise()
        projector_manager.bootstrap_post_set_up()

    # WHEN: Called
    projector_manager._load_projectors()

    assert len(projector_manager.projector_list) == len(t_list), \
        'Invalid number of entries between check and list'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk = []
    for dbitem in projector_manager.projector_list:
        t_chk.append(dbitem.db_item)

    assert t_chk == t_list, 'projector_list DB items do not match test items'


@patch.multiple(openlp.core.projectors.manager.ProjectorManager,
                udp_listen_add=DEFAULT,
                udp_listen_delete=DEFAULT,
                add_projector=DEFAULT)
@patch.object(openlp.core.projectors.db.ProjectorDB, 'get_projector_by_ip')
def test_add_projector_from_wizard(mock_ip, projector_manager_mtdb, **kwargs):
    """
    Test when add projector from GUI, appropriate method is called correctly
    """
    # GIVEN: Test environment
    t_item = Projector(**TEST1_DATA)
    mock_ip.return_value = t_item
    mock_add = kwargs['add_projector']

    # WHEN: Called
    projector_manager_mtdb.add_projector_from_wizard(ip=t_item.ip)

    # THEN: appropriate calls made
    mock_add.assert_called_with(t_item)


@patch.multiple(openlp.core.projectors.manager.ProjectorManager,
                udp_listen_add=DEFAULT,
                udp_listen_delete=DEFAULT)
def test_get_projector_list(projector_manager, caplog, **kwargs):
    """
    Test get_projector_list() returns valid entries
    """
    # GIVEN: Test environment
    t_list = projector_manager.projectordb.get_projector_all()

    projector_manager.bootstrap_initialise()
    projector_manager.bootstrap_post_set_up()

    # WHEN: Called
    t_chk = projector_manager.get_projector_list()

    # THEN: DB items for both t_list and projector_list are the same
    assert len(t_chk) == len(t_list), 'projector_list length mismatch with test items length'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk_list = [item.db_item for item in t_chk]
    assert t_list == t_chk_list, 'projector_list DB items do not match test items'
