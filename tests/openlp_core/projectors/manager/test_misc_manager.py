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
"""
from unittest.mock import DEFAULT, patch

from openlp.core.projectors.db import Projector

from tests.resources.projector.data import TEST1_DATA, TEST2_DATA, TEST3_DATA


def test_private_load_projectors(projector_manager_mtdb):
    """
    Test that _load_projectors() retrieves all entries from projector database
    """
    # GIVEN: Test environment
    t_db = projector_manager_mtdb.projectordb  # Shortcut helper
    for itm in (TEST1_DATA, TEST2_DATA, TEST3_DATA):
        t_db.add_projector(Projector(**itm))
    t_db.session.commit()

    t_list = t_db.get_projector_all()

    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    # Although we're testing _load_projectors, need to mock
    # it first to get past bootstrap_post_set_up() before test
    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        _load_projectors=DEFAULT) as mock_manager:
        # Satisfy Flake8 linting
        mock_manager['udp_listen_add'].return_value = None
        projector_manager_mtdb.bootstrap_initialise()
        projector_manager_mtdb.bootstrap_post_set_up()

    # WHEN: Called
    projector_manager_mtdb._load_projectors()

    assert len(projector_manager_mtdb.projector_list) == len(t_list), \
        'Invalid number of entries between check and list'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk = []
    for dbitem in projector_manager_mtdb.projector_list:
        t_chk.append(dbitem.db_item)

    assert t_chk == t_list, 'projector_list DB items do not match test items'


def test_on_edit_input(projector_manager):
    """
    Test calling edit projector input GUI from input selection icon makes appropriate calls
    """
    # GIVEN: Test environment
    with patch.object(projector_manager, 'on_select_input') as mock_edit:

        # WHEN: Called
        projector_manager.on_edit_input()

        # THEN: select input called with edit option
        mock_edit.assert_called_with(opt=None, edit=True)


def test_on_add_projector(projector_manager):
    """
    Test add new projector edit GUI is called properly
    """
    # GIVEN: Test environment
    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    with patch.multiple(projector_manager,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT) as mock_manager:
        # Satisfy Flake8 linting
        mock_manager['udp_listen_add'].return_value = None
        projector_manager.bootstrap_initialise()
        projector_manager.bootstrap_post_set_up()

    with patch.object(projector_manager, 'projector_form') as mock_form:

        # WHEN called
        projector_manager.on_add_projector()

        # THEN: projector form called
        mock_form.exec.assert_called_once()


def test_add_projector_from_wizard(projector_manager):
    """
    Test when add projector from GUI, appropriate method is called correctly
    """
    # GIVEN: Test environment
    with patch.multiple(projector_manager,
                        projectordb=DEFAULT,
                        add_projector=DEFAULT) as mock_manager:
        t_item = Projector(**TEST1_DATA)

        mock_manager['projectordb'].get_projector_by_ip.return_value = t_item

        # WHEN: Called
        projector_manager.add_projector_from_wizard(ip=t_item.ip)

        # THEN: appropriate calls made
        mock_manager['add_projector'].assert_called_with(t_item)


def test_get_projector_list(projector_manager_mtdb):
    """
    Test get_projector_list() returns valid entries
    """
    # GIVEN: Test environment
    t_db = projector_manager_mtdb.projectordb  # Shortcut helper
    for itm in (TEST1_DATA, TEST2_DATA, TEST3_DATA):
        t_db.add_projector(Projector(**itm))
    t_list = t_db.get_projector_all()

    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT) as mock_manager:
        # Satisfy Flake8 linting
        mock_manager['udp_listen_add'].return_value = None
        projector_manager_mtdb.bootstrap_initialise()
        projector_manager_mtdb.bootstrap_post_set_up()

    # WHEN: Called
    t_chk = projector_manager_mtdb.get_projector_list()

    # THEN: DB items for both t_list and projector_list are the same
    assert len(t_chk) == len(t_list), 'projector_list length mismatch with test items length'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk_list = []
    for dbitem in t_chk:
        t_chk_list.append(dbitem.db_item)
    assert t_list == t_chk_list, 'projector_list DB items do not match test items'
