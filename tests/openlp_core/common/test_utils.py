# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.core.common.utils import wait_for


def test_wait_for(registry):
    """
    Test the wait_for function
    """
    # GIVEN: Mocked app and Registry
    mock_app = MagicMock()
    Registry().register('application', mock_app)
    mock_func = MagicMock()
    mock_func.side_effect = [False, True]

    # WHEN: wait_for is run
    wait_for(mock_func)

    # THEN: the functions got called
    assert mock_func.call_count == 2
