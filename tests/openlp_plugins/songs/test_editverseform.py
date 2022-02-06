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
This module contains tests for the editverseform of the Songs plugin.
"""
import pytest
from unittest.mock import MagicMock

from openlp.plugins.songs.forms.editverseform import EditVerseForm


@pytest.fixture()
def edit_verse_form(settings):
    return EditVerseForm(None)


def test_update_suggested_verse_number_has_no_effect(edit_verse_form):
    """
    Test that update_suggested_verse_number() has no effect when editing a single verse
    """
    # GIVEN some input values
    edit_verse_form.has_single_verse = True
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=0)
    edit_verse_form.verse_text_edit.toPlainText = MagicMock(return_value='Text')
    edit_verse_form.verse_number_box.setValue(3)

    # WHEN the method is called
    edit_verse_form.update_suggested_verse_number()

    # THEN the verse number must not be changed
    assert 3 == edit_verse_form.verse_number_box.value(), 'The verse number should be 3'


def test_update_suggested_verse_number_different_type(edit_verse_form):
    """
    Test that update_suggested_verse_number() returns 0 when editing a second verse of a different type
    """
    # GIVEN some input values
    edit_verse_form.has_single_verse = False
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=2)
    edit_verse_form.verse_text_edit.toPlainText = MagicMock(return_value='Text')
    edit_verse_form.verse_number_box.setValue(3)

    # WHEN the method is called
    edit_verse_form.update_suggested_verse_number()

    # THEN the verse number must be changed to 1
    assert 1 == edit_verse_form.verse_number_box.value(), 'The verse number should be 1'


def test_on_divide_split_button_clicked(edit_verse_form):
    """
    Test that divide adds text at the correct position
    """
    # GIVEN some input values
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
    edit_verse_form.verse_text_edit.setPlainText('Text\n')

    # WHEN the method is called
    edit_verse_form.on_forced_split_button_clicked()
    # THEN the verse number must not be changed
    assert '[--}{--]\nText\n' == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse number should be [--}{--]\nText\n'


def test_on_split_button_clicked(edit_verse_form):
    """
    Test that divide adds text at the correct position
    """
    # GIVEN some input values
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
    edit_verse_form.verse_text_edit.setPlainText('Text\n')

    # WHEN the method is called
    edit_verse_form.on_overflow_split_button_clicked()
    # THEN the verse number must not be changed
    assert '[---]\nText\n' == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse number should be [---]\nText\n'
