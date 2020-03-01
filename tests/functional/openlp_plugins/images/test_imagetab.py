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
This module contains tests for the lib submodule of the Images plugin.
"""
import pytest
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.plugins.images.lib.imagetab import ImageTab


@pytest.fixture()
def form(settings):
    Registry().register('settings_form', MagicMock())
    frm = ImageTab(None, 'Images', None, None)
    frm.settings_form.register_post_process = MagicMock()
    return frm


def test_save_tab_nochange(form):
    """
    Test no changes does not trigger post processing
    """
    # GIVEN: No changes on the form.
    # WHEN: the save is invoked
    form.save()
    # THEN: the post process should not be requested
    assert 0 == form.settings_form.register_post_process.call_count, \
        'Image Post processing should not have been requested'


def test_save_tab_change(form):
    """
    Test a color change is applied and triggers post processing.
    """
    # GIVEN: Apply a change to the form.
    form.on_background_color_changed('#999999')
    # WHEN: the save is invoked
    form.save()
    # THEN: the post process should be requested
    assert 1 == form.settings_form.register_post_process.call_count, \
        'Image Post processing should have been requested'
    # THEN: The color should be set
    assert form.background_color == '#999999', 'The updated color should have been saved'
