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
from unittest.mock import MagicMock, call, patch

import pytest
from PyQt5 import QtCore, QtTest, QtGui, QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.editverseform import EditVerseForm


@pytest.fixture()
def edit_verse_form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = EditVerseForm()
    yield frm
    del frm
    del main_window


def test_ui_defaults(edit_verse_form):
    """
    Test the EditVerseForm defaults are correct
    """
    # GIVEN: An EditVerseForm instance
    # WHEN: The form is shown
    # THEN: The default value is correct
    assert edit_verse_form.verse_text_edit.toPlainText() == '', 'The verse edit box is empty.'


def test_type_verse_text(edit_verse_form):
    """
    Test that typing into the verse text edit box returns the correct text
    """
    # GIVEN: An instance of the EditVerseForm and some text to type
    text = 'Amazing Grace, how sweet the sound!'

    # WHEN: Some verse text is typed into the text edit
    QtTest.QTest.keyClicks(edit_verse_form.verse_text_edit, text)

    # THEN: The verse text edit should have the verse text in it
    assert text == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have the typed out verse'


def test_insert_verse(edit_verse_form):
    """
    Test the insert_verse() method
    """
    # GIVEN: An EditVerseForm instance, with stuff mocked out
    with patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        mocked_verse_text_edit.textCursor.return_value.columnNumber.return_value = 1
        # WHEN: insert_verse() is called
        edit_verse_form.insert_verse('V')
        # THEN: The verse is inserted
        assert mocked_verse_text_edit.insertPlainText.call_args_list == [call('\n'), call('---[Verse:1]---\n')]
        mocked_verse_text_edit.setFocus()


def test_insert_verse_insert_click(edit_verse_form):
    """
    Test that clicking the insert button inserts the correct verse marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The Insert button is clicked
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:1]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a verse marker'


def test_insert_verse_up_click(edit_verse_form):
    """
    Test that clicking the up button on the spin box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The spin button and then the Insert button are clicked
    QtTest.QTest.keyClick(edit_verse_form.verse_number_box, QtCore.Qt.Key_Up)
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:2]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Verse 2" marker'


def test_insert_chorus(edit_verse_form):
    """
    Test that clicking the verse type combo box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The verse type combo box and then the Insert button are clicked
    QtTest.QTest.keyClick(edit_verse_form.verse_type_combo_box, QtCore.Qt.Key_Down)
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Chorus:1 in it
    assert '---[Chorus:1]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Chorus 1" marker'


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


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
def test_on_transpose_up_button_clicked(mocked_show_key_warning, edit_verse_form):
    """
    Test that transpose button will transpose the chords and warn about missing song key
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    # WHEN the method is called
    edit_verse_form.on_transpose_up_button_clicked()
    mocked_show_key_warning.assert_called_once_with(edit_verse_form)
    # THEN chords should be transposed up
    assert 'Am[Ab]azing gr[Ab/C]ace, how sw[C#]eet the s[Ab]ound' == edit_verse_form.verse_text_edit.toPlainText()


def test_on_transpose_down_button_clicked(edit_verse_form):
    """
    Test that transpose button will transpose the chords and warn about missing song key
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    # WHEN the method is called
    edit_verse_form.on_transpose_down_button_clicked()
    # THEN chords should be transposed up
    assert '[=F#]Am[F#]azing gr[F#/A#]ace, how sw[B]eet the s[F#]ound' == edit_verse_form.verse_text_edit.toPlainText()


def test_set_verse_single(settings, edit_verse_form):
    """
    Test the set_verse() method of the EditVerseForm for single verses
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out, and chords enabled
    settings.setValue('songs/enable chords', True)

    with patch.object(edit_verse_form, 'verse_type_combo_box') as mocked_verse_type_combo, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box, \
            patch.object(edit_verse_form, 'insert_button') as mocked_insert_button, \
            patch.object(edit_verse_form, 'transpose_widget') as mocked_transpose_widget, \
            patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        # WHEN: set_verse() is called
        edit_verse_form.set_verse('Amazing grace, how sweet the sound', single=True)

        # THEN: The right things should have been done
        mocked_verse_type_combo.setCurrentIndex.assert_called_once_with(0)
        mocked_verse_number_box.setValue.assert_called_once_with(1)
        mocked_insert_button.setVisible.assert_called_once_with(False)
        mocked_transpose_widget.setVisible.assert_called_once_with(False)
        mocked_verse_text_edit.setPlainText.assert_called_once_with('Amazing grace, how sweet the sound')
        mocked_verse_text_edit.setFocus.assert_called_once_with()
        mocked_verse_text_edit.moveCursor.assert_called_once_with(QtGui.QTextCursor.End)


def test_set_verse_multiple(settings, edit_verse_form):
    """
    Test the set_verse() method of the EditVerseForm for multiple verses
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out, and chords enabled
    settings.setValue('songs/enable chords', True)

    with patch.object(edit_verse_form, 'verse_type_combo_box') as mocked_verse_type_combo, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box, \
            patch.object(edit_verse_form, 'insert_button') as mocked_insert_button, \
            patch.object(edit_verse_form, 'transpose_widget') as mocked_transpose_widget, \
            patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        # WHEN: set_verse() is called
        edit_verse_form.set_verse(None)

        # THEN: The right things should have been done
        mocked_verse_type_combo.setCurrentIndex.assert_called_once_with(0)
        mocked_verse_number_box.setValue.assert_called_once_with(1)
        mocked_insert_button.setVisible.assert_called_once_with(True)
        mocked_transpose_widget.setVisible.assert_called_once_with(True)
        mocked_verse_text_edit.setPlainText.assert_called_once_with('---[Verse:1]---\n')
        mocked_verse_text_edit.setFocus.assert_called_once_with()
        mocked_verse_text_edit.moveCursor.assert_called_once_with(QtGui.QTextCursor.End)
