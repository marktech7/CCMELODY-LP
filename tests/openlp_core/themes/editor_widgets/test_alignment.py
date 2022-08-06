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
Package to test the openlp.core.themes.editor_widgets.alignment package.
"""
import pytest

from openlp.core.lib.theme import HorizontalType, VerticalType
from openlp.core.themes.editor_widgets.alignment import AlignmentWidget


def test_init_(settings):
    """
    Test the initialisation of AlignmentWidget
    """
    # GIVEN: The AlignmentWidget class
    # WHEN: Initialising AlignmentWidget
    # THEN: We should have an instance of the widget with no errors
    AlignmentWidget()


def test_get_horizontal_align(settings):
    """
    Test the horizontal_align getter
    """
    # GIVEN: An AlignmentWidget instance with the combobox set to index 1
    page = AlignmentWidget()
    page.horizontal_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = page.horizontal_align

    # THEN: The result should be correct
    assert result == HorizontalType.Right


def test_set_horizontal_align_int(settings):
    """
    Test the horizontal_align setter with an int
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    page.horizontal_align = HorizontalType.Center

    # THEN: The combobox should be correct
    assert page.horizontal_combo_box.currentIndex() == 2


def test_set_horizontal_align_str(settings):
    """
    Test the horizontal_align setter with a str
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    page.horizontal_align = HorizontalType.to_string(HorizontalType.Justify)

    # THEN: The combobox should be correct
    assert page.horizontal_combo_box.currentIndex() == 3


def test_set_horizontal_align_exception(settings):
    """
    Test the horizontal_align setter with something other than a str or int
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='horizontal_align must either be a string or an int'):
        page.horizontal_align = []


def test_get_vertical_align(settings):
    """
    Test the vertical_align getter
    """
    # GIVEN: An AlignmentWidget instance with the combobox set to index 1
    page = AlignmentWidget()
    page.vertical_combo_box.setCurrentIndex(1)

    # WHEN: The property is accessed
    result = page.vertical_align

    # THEN: The result should be correct
    assert result == VerticalType.Middle


def test_set_vertical_align_int(settings):
    """
    Test the vertical_align setter with an int
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    page.vertical_align = VerticalType.Bottom

    # THEN: The combobox should be correct
    assert page.vertical_combo_box.currentIndex() == 2


def test_set_vertical_align_str(settings):
    """
    Test the vertical_align setter with a str
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    page.vertical_align = VerticalType.to_string(VerticalType.Top)

    # THEN: The combobox should be correct
    assert page.vertical_combo_box.currentIndex() == 0


def test_set_vertical_align_exception(settings):
    """
    Test the vertical_align setter with something other than a str or int
    """
    # GIVEN: An AlignmentWidget instance
    page = AlignmentWidget()

    # WHEN: The property is set
    # THEN: An exception is raised
    with pytest.raises(TypeError, match='vertical_align must either be a string or an int'):
        page.vertical_align = []
