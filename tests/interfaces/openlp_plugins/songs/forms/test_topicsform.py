# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
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
Package to test the openlp.plugins.songs.forms.topicsform package.
"""
from unittest import TestCase

from PyQt5 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.topicsform import TopicsForm
from tests.helpers.testmixin import TestMixin


class TestTopicsForm(TestCase, TestMixin):
    """
    Test the TopicsForm class
    """

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        self.main_window = QtWidgets.QMainWindow()
        Registry().register('main_window', self.main_window)
        self.form = TopicsForm()

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.form
        del self.main_window

    def test_ui_defaults(self):
        """
        Test the TopicsForm defaults are correct
        """
        assert self.form.name_edit.text() == '', 'The first name edit should be empty'

    def test_get_name_property(self):
        """
        Test that getting the name property on the TopicsForm works correctly
        """
        # GIVEN: A topic name to set
        topic_name = 'Salvation'

        # WHEN: The name_edit's text is set
        self.form.name_edit.setText(topic_name)

        # THEN: The name property should have the correct value
        assert self.form.name == topic_name, 'The name property should be correct'

    def test_set_name_property(self):
        """
        Test that setting the name property on the TopicsForm works correctly
        """
        # GIVEN: A topic name to set
        topic_name = 'James'

        # WHEN: The name property is set
        self.form.name = topic_name

        # THEN: The name_edit should have the correct value
        assert self.form.name_edit.text() == topic_name, 'The topic name should be set correctly'
