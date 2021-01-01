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
Package to test the openlp.plugins.songs.forms.editverseform package.
"""
import pytest

from PyQt5 import QtCore, QtTest, QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.editverseform import EditVerseForm


@pytest.fixture()
def form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = EditVerseForm()
    yield frm
    del frm
    del main_window


def test_ui_defaults(form):
    """
    Test the EditVerseForm defaults are correct
    """
    # GIVEN: An EditVerseForm instance
    # WHEN: The form is shown
    # THEN: The default value is correct
    assert form.verse_text_edit.toPlainText() == '', 'The verse edit box is empty.'


def test_type_verse_text(form):
    """
    Test that typing into the verse text edit box returns the correct text
    """
    # GIVEN: An instance of the EditVerseForm and some text to type
    text = 'Amazing Grace, how sweet the sound!'

    # WHEN: Some verse text is typed into the text edit
    QtTest.QTest.keyClicks(form.verse_text_edit, text)

    # THEN: The verse text edit should have the verse text in it
    assert text == form.verse_text_edit.toPlainText(), \
        'The verse text edit should have the typed out verse'


def test_insert_verse(form):
    """
    Test that clicking the insert button inserts the correct verse marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The Insert button is clicked
    QtTest.QTest.mouseClick(form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:1]---' in form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a verse marker'


def test_insert_verse_2(form):
    """
    Test that clicking the up button on the spin box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The spin button and then the Insert button are clicked
    QtTest.QTest.keyClick(form.verse_number_box, QtCore.Qt.Key_Up)
    QtTest.QTest.mouseClick(form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:2]---' in form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Verse 2" marker'


def test_insert_chorus(form):
    """
    Test that clicking the verse type combo box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The verse type combo box and then the Insert button are clicked
    QtTest.QTest.keyClick(form.verse_type_combo_box, QtCore.Qt.Key_Down)
    QtTest.QTest.mouseClick(form.insert_button, QtCore.Qt.LeftButton)

    # THEN: The verse text edit should have a Chorus:1 in it
    assert '---[Chorus:1]---' in form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Chorus 1" marker'
