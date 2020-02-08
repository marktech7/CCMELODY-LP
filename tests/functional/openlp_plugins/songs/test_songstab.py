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
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.lib.songstab import SongsTab
from tests.helpers.testmixin import TestMixin

__default_settings__ = {
    'songs/footer template': """${title}""",
    'songs/chord notation': 'english'
}


class TestSongTab(TestCase, TestMixin):
    """
    This is a test case to test various methods in the ImageTab.
    """

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        Registry().register('settings_form', MagicMock())
        self.setup_application()
        self.build_settings()
        Registry().register('settings', self.setting)
        self.setting.extend_default_settings(__default_settings__)
        self.parent = QtWidgets.QMainWindow()
        self.form = SongsTab(self.parent, 'Songs', None, None)
        self.form.settings_form.register_post_process = MagicMock()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.parent
        del self.form
        self.destroy_settings()

    def test_german_notation_on_load(self):
        """
        Test the corrent notation is selected on load
        """
        # GIVEN: German notation in the settings
        self.setting.setValue('songs/chord notation', 'german')
        # WHEN: Load is invoked
        self.form.load()
        # THEN: The german radio button should be checked
        assert self.form.german_notation_radio_button.isChecked() is True

    def test_neolatin_notation_on_load(self):
        """
        Test the corrent notation is selected on load
        """
        # GIVEN: neo-latin notation in the settings
        self.setting.setValue('songs/chord notation', 'neo-latin')
        # WHEN: Load is invoked
        self.form.load()
        # THEN: The neo-latin radio button should be checked
        assert self.form.neolatin_notation_radio_button.isChecked() is True

    def test_invalid_notation_on_load(self):
        """
        Test the invalid notation in settings reverts to english
        """
        # GIVEN: gibberish notation in the settings
        self.setting.setValue('songs/chord notation', 'gibberish')
        # WHEN: Load is invoked
        self.form.load()
        # THEN: The english radio button should be checked
        assert self.form.english_notation_radio_button.isChecked() is True

    def test_save_check_box_settings(self):
        """
        Test check box options are correctly saved
        """
        # GIVEN: A arrangement of enabled/disabled check boxes
        self.form.on_search_as_type_check_box_changed(QtCore.Qt.Unchecked)
        self.form.on_tool_bar_active_check_box_changed(QtCore.Qt.Checked)
        self.form.on_update_on_edit_check_box_changed(QtCore.Qt.Unchecked)
        self.form.on_add_from_service_check_box_changed(QtCore.Qt.Checked)
        self.form.on_songbook_slide_check_box_changed(QtCore.Qt.Unchecked)
        self.form.on_mainview_chords_check_box_changed(QtCore.Qt.Checked)
        self.form.on_disable_chords_import_check_box_changed(QtCore.Qt.Unchecked)
        # WHEN: Save is invoked
        self.form.save()
        # THEN: The correct values should be stored in the settings
        # song_search is currently unused
        assert self.setting.value('songs/display songbar') is True
        assert self.setting.value('songs/update service on edit') is False
        assert self.setting.value('songs/add song from service') is True
        assert self.setting.value('songs/add songbook slide') is False
        assert self.setting.value('songs/mainview chords') is True
        assert self.setting.value('songs/disable chords import') is False

    def test_english_notation_button(self):
        """
        Test notation button clicked handler
        """
        # GIVEN: A normal song form
        # WHEN: english notation clicked
        self.form.on_english_notation_button_clicked()
        # THEN: Chord notation should be correct
        assert self.form.chord_notation == 'english'

    def test_german_notation_button(self):
        """
        Test notation button clicked handler
        """
        # GIVEN: A normal song form
        # WHEN: german notation clicked
        self.form.on_german_notation_button_clicked()
        # THEN: Chord notation should be correct
        assert self.form.chord_notation == 'german'

    def test_neolatin_notation_button(self):
        """
        Test notation button clicked handler
        """
        # GIVEN: A normal song form
        # WHEN: neolatin notation clicked
        self.form.on_neolatin_notation_button_clicked()
        # THEN: Chord notation should be correct
        assert self.form.chord_notation == 'neo-latin'

    @patch('openlp.core.common.settings.Settings.setValue')
    def test_footer_nochange(self, mocked_settings_set_val):
        """
        Test the footer is not saved when not changed
        """
        # GIVEN: A normal song form
        # WHEN: save is invoked
        self.form.save()
        # THEN: footer should not have been saved (one less call than the change test below)
        assert mocked_settings_set_val.call_count == 8

    @patch('openlp.core.common.settings.Settings.setValue')
    def test_footer_change(self, mocked_settings_set_val):
        """
        Test the footer is saved when changed
        """
        # GIVEN: Footer has changed
        self.form.footer_edit_box.setPlainText('A new footer')
        # WHEN: save is invoked
        self.form.save()
        # THEN: footer should have been saved (one more call to setValue than the nochange test)
        assert mocked_settings_set_val.call_count == 9
        assert self.form.footer_edit_box.toPlainText() == 'A new footer'

    def test_footer_reset(self):
        """
        Test the footer is reset when reset clicked
        """
        # GIVEN: A default footer and different content in the edit box
        self.setting.setValue('songs/footer template', 'hello')
        self.form.footer_edit_box.setPlainText('A different footer')
        # WHEN: reset is invoked
        self.form.on_footer_reset_button_clicked()
        # THEN: footer edit box should have been reset to the settings value
        assert self.form.footer_edit_box.toPlainText() == self.setting.get_default_value('songs/footer template')

    def test_save_tab_nochange(self):
        """
        Test no changes does not trigger post processing
        """
        # GIVEN: No changes on the form.
        self.initial_color = '#999999'
        # WHEN: the save is invoked
        self.form.save()
        # THEN: the post process should not be requested
        assert 0 == self.form.settings_form.register_post_process.call_count, \
            'Songs Post processing should not have been requested'

    def test_save_tab_change(self):
        """
        Test save after visiting the page triggers post processing.
        """
        # GIVEN: Form has been visited.
        self.form.tab_visited = True
        # WHEN: the save is invoked
        self.form.save()
        # THEN: the post process should be requested
        assert 1 == self.form.settings_form.register_post_process.call_count, \
            'Songs Post processing should have been requested'
