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
Test methods called by toolbar icons part 1
"""

from unittest.mock import DEFAULT, patch

from openlp.core.projectors.db import Projector

from tests.resources.projector.data import FakePJLink, TEST1_DATA, TEST2_DATA, TEST3_DATA


def test_on_blank_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        mock_manager['_add_projector'].side_effect = [t_1, t_2, t_3]
        projector_manager_mtdb.bootstrap_initialise()
        # projector_list_widget created here
        projector_manager_mtdb.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        projector_manager_mtdb.add_projector(projector=t_1)
        projector_manager_mtdb.add_projector(projector=t_2)
        projector_manager_mtdb.add_projector(projector=t_3)

        # Set at least one instance as selected to verify projector_list_widget is not called
        projector_manager_mtdb.projector_list_widget.item(0).setSelected(False)
        projector_manager_mtdb.projector_list_widget.item(1).setSelected(False)
        projector_manager_mtdb.projector_list_widget.item(2).setSelected(True)

        # WHEN: Called with projector instance
        projector_manager_mtdb.on_blank_projector(opt=t_1)

        # THEN: Only t_1.set_shutter_closed() should be called
        t_1.set_shutter_closed.assert_called_once()
        t_2.set_shutter_closed.assert_not_called()
        t_3.set_shutter_closed.assert_not_called()


def test_on_blank_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        projector_manager_mtdb.bootstrap_initialise()
        # projector_list_widget created here
        projector_manager_mtdb.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        mock_manager['_add_projector'].side_effect = [t_1, t_2, t_3]
        projector_manager_mtdb.add_projector(projector=t_1)
        projector_manager_mtdb.add_projector(projector=t_2)
        projector_manager_mtdb.add_projector(projector=t_3)

        # Set at least one instance as selected to verify projector_list_widget is not called
        projector_manager_mtdb.projector_list_widget.item(0).setSelected(False)
        projector_manager_mtdb.projector_list_widget.item(1).setSelected(False)
        projector_manager_mtdb.projector_list_widget.item(2).setSelected(True)

        # WHEN: Called with projector instance
        projector_manager_mtdb.on_blank_projector(opt=None)

        # THEN: Only t_3.set_shutter_closed() should be called
        t_1.set_shutter_closed.assert_not_called()
        t_2.set_shutter_closed.assert_not_called()
        t_3.set_shutter_closed.assert_called_once()


def test_on_blank_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        projector_manager_mtdb.bootstrap_initialise()
        # projector_list_widget created here
        projector_manager_mtdb.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        mock_manager['_add_projector'].side_effect = [t_1, t_2, t_3]
        projector_manager_mtdb.add_projector(projector=t_1)
        projector_manager_mtdb.add_projector(projector=t_2)
        projector_manager_mtdb.add_projector(projector=t_3)

        # Set at least one instance as selected to verify projector_list_widget is not called
        projector_manager_mtdb.projector_list_widget.item(0).setSelected(True)
        projector_manager_mtdb.projector_list_widget.item(1).setSelected(False)
        projector_manager_mtdb.projector_list_widget.item(2).setSelected(True)

        # WHEN: Called with projector instance
        projector_manager_mtdb.on_blank_projector(opt=None)

        # THEN: t_1 and t_3 set_shutter_closed() should be called
        t_1.set_shutter_closed.assert_called_once()
        t_2.set_shutter_closed.assert_not_called()
        t_3.set_shutter_closed.assert_called_once()
