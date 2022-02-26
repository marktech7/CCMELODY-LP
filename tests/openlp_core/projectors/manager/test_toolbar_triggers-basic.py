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
Test methods called by toolbar icons with minimal flow paths and tests
"""

import openlp.core.projectors.manager

from unittest.mock import DEFAULT, patch

test_module = openlp.core.projectors.manager.__name__


def test_on_add_projector(projector_manager):
    """
    Test add new projector edit GUI is called properly
    """
    # GIVEN: Test environment
    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    with patch.multiple(projector_manager,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT):
        projector_manager.bootstrap_initialise()
        projector_manager.bootstrap_post_set_up()

    # Have to wait for projector_manager.bootstrap_post_set_up() before projector_form is initialized
    with patch.object(projector_manager, 'projector_form') as mock_form:

        # WHEN called
        projector_manager.on_add_projector()

        # THEN: projector form called
        mock_form.exec.assert_called_once()


def test_on_edit_input(projector_manager, pjlink):
    """
    Test on_edit_input calls on_select_input properly
    """
    # GIVEN: Test setup
    with patch.object(projector_manager, 'on_select_input') as mock_input:

        # WHEN: Called with pjlink instance
        projector_manager.on_edit_input(opt=pjlink)

        # THEN: appropriate call made
        mock_input.assert_called_with(opt=pjlink, edit=True)
