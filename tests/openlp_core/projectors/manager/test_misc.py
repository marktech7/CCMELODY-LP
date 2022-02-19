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

from tests.resources.projector.data import TEST1_DATA


def test_on_edit_input(projector_manager_memdb):
    """
    Test calling edit from input selection
    """
    # GIVEN: Test environment
    with patch.object(projector_manager_memdb, 'on_select_input') as mock_edit:

        # WHEN: Called
        projector_manager_memdb.on_edit_input()

        # THEN: select input called with edit option
        mock_edit.assert_called_with(opt=None, edit=True)


def test_on_add_projector(projector_manager_memdb):
    # GIVEN: Test environment
    projector_manager_memdb.bootstrap_initialise()
    projector_manager_memdb.bootstrap_post_set_up()

    with patch.object(projector_manager_memdb, 'projector_form') as mock_form:

        # WHEN called
        projector_manager_memdb.on_add_projector()

        # THEN: projector form called
        mock_form.exec.assert_called_once()


def test_add_projector_from_wizard(projector_manager_memdb):
    projector_manager = projector_manager_memdb

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
