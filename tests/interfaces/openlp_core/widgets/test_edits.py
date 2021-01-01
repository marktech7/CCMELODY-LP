# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
Module to test the EditCustomForm.
"""
import pytest
from unittest.mock import MagicMock, call

from PyQt5 import QtCore, QtGui, QtTest, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.widgets.edits import HistoryComboBox, SearchEdit


class SearchTypes(object):
    """
    Types of search
    """
    First = 0
    Second = 1


SECOND_PLACEHOLDER_TEXT = "Second Placeholder Text"
SEARCH_TYPES = [(SearchTypes.First, QtGui.QIcon(), "First", "First Placeholder Text"),
                (SearchTypes.Second, QtGui.QIcon(), "Second", SECOND_PLACEHOLDER_TEXT)]


@pytest.fixture()
def search_edit(mock_settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    Registry().remove('settings')
    Registry().register('settings', MagicMock(**{'value.return_value': SearchTypes.First}))

    s_edit = SearchEdit(main_window, 'settings_section')
    # To complete set up we have to set the search types.
    s_edit.set_search_types(SEARCH_TYPES)
    return s_edit


@pytest.fixture()
def combo(mock_settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    s_combo = HistoryComboBox(main_window)
    return s_combo


def test_set_search_types(search_edit):
    """
    Test setting the search types of the search edit.
    """
    # GIVEN: The search edit with the search types set. NOTE: The set_search_types(types) is called in the setUp()
    # method!

    # WHEN:

    # THEN: The first search type should be the first one in the list. The selected type should be saved in the
    #       settings
    assert search_edit.current_search_type() == SearchTypes.First, \
        "The first search type should be selected."
    Registry().get('settings').setValue.assert_called_once_with('settings_section/last used search type', 0)


def test_set_current_search_type(search_edit):
    """
    Test if changing the search type works.
    """
    # GIVEN:
    # WHEN: Change the search type
    result = search_edit.set_current_search_type(SearchTypes.Second)

    # THEN:
    assert result is True, "The call should return success (True)."
    assert search_edit.current_search_type() == SearchTypes.Second, \
        "The search type should be SearchTypes.Second"
    assert search_edit.placeholderText() == SECOND_PLACEHOLDER_TEXT, \
        "The correct placeholder text should be 'Second Placeholder Text'."
    Registry().get('settings').setValue.assert_has_calls(
        [call('settings_section/last used search type', 0), call('settings_section/last used search type', 1)])


def test_clear_button_visibility(search_edit):
    """
    Test if the clear button is hidden/shown correctly.
    """
    # GIVEN: Everything is left to its defaults (hidden).
    assert search_edit.clear_button.isHidden(), "Pre condition not met. Button should be hidden."

    # WHEN: Type something in the search edit.
    QtTest.QTest.keyPress(search_edit, QtCore.Qt.Key_A)
    QtTest.QTest.keyRelease(search_edit, QtCore.Qt.Key_A)

    # THEN: The clear button should not be hidden any more.
    assert not search_edit.clear_button.isHidden(), "The clear button should be visible."


def test_press_clear_button(search_edit):
    """
    Check if the search edit behaves correctly when pressing the clear button.
    """
    # GIVEN: A search edit with text.
    QtTest.QTest.keyPress(search_edit, QtCore.Qt.Key_A)
    QtTest.QTest.keyRelease(search_edit, QtCore.Qt.Key_A)

    # WHEN: Press the clear button.
    QtTest.QTest.mouseClick(search_edit.clear_button, QtCore.Qt.LeftButton)

    # THEN: The search edit text should be cleared and the button be hidden.
    assert not search_edit.text(), "The search edit should not have any text."
    assert search_edit.clear_button.isHidden(), "The clear button should be hidden."


def test_history_combo_get_items(combo):
    """
    Test the getItems() method
    """
    # GIVEN: The combo.

    # WHEN: Add two items.
    combo.addItem('test1')
    combo.addItem('test2')

    # THEN: The list of items should contain both strings.
    assert combo.getItems() == ['test1', 'test2']
