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
Tests for commands that do not need much testing
"""

import logging
import openlp.core.projectors.pjlinkcommands

from openlp.core.projectors.pjlinkcommands import process_srch

test_module = openlp.core.projectors.pjlinkcommands.__name__


def test_srch_no_projector(caplog):
    """
    Test SRCH command with no projector instance
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(f'{test_module}', logging.WARNING, 'SRCH packet detected - ignoring')]

    # WHEN: Called
    t_chk = process_srch()

    # THEN: Appropriate return code and log entries
    assert t_chk is None, 'Invalid return code'
    assert caplog.record_tuples == logs, 'Invalid log entries'


def test_srch_with_projector(pjlink, caplog):
    """
    Test SRCH command with projector
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) SRCH packet detected - ignoring')]

    # WHEN: Called
    t_chk = process_srch(projector=pjlink)

    # THEN: Appropriate return code and log entries
    assert t_chk is None, 'Invalid return code'
    assert caplog.record_tuples == logs, 'Invalid log entries'
