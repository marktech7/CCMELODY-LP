# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
:mod: `tests.functional.openlp_core_ui.test_projectorsourceform` module

Tests for the Projector Source Select form.
"""
from openlp.core.ui.projector.sourceselectform import source_group


def test_source_group():
    """
    Test the source_group() method
    """
    # GIVEN: A list of inputs and source text
    inputs = [
        'vga1', 'vga2',
        'hdmi1', 'hdmi2'
    ]
    source_text = {
        'vga1': 'VGA 1',
        'vga2': 'VGA 2',
        'hdmi1': 'HDMI 1',
        'hdmi2': 'HDMI 2'
    }

    # WHEN: source_group() is called
    result = source_group(inputs, source_text)

    # THEN: the resultant dictionary should be correct
    expected_dict = {
        'v': {'vga1': 'VGA 1', 'vga2': 'VGA 2'},
        'h': {'hdmi1': 'HDMI 1', 'hdmi2': 'HDMI 2'}
    }
    assert result == expected_dict, result
