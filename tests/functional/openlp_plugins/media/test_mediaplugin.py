# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
Test the media plugin
"""
from unittest import TestCase
from unittest.mock import patch

from openlp.core.common.registry import Registry
from openlp.plugins.media.mediaplugin import MediaPlugin
from tests.helpers.testmixin import TestMixin


class MediaPluginTest(TestCase, TestMixin):
    """
    Test the media plugin
    """
    def setUp(self):
        Registry.create()

    @patch('openlp.plugins.media.mediaplugin.Plugin.initialise')
    def test_initialise(self, mocked_initialise):
        """
        Test that the initialise() method overwrites the built-in one, but still calls it
        """
        # GIVEN: A media plugin instance
        media_plugin = MediaPlugin()

        # WHEN: initialise() is called
        media_plugin.initialise()

        # THEN: The the base initialise() method should be called
        mocked_initialise.assert_called_with()

    def test_about_text(self):
        # GIVEN: The MediaPlugin
        # WHEN: Retrieving the about text
        # THEN: about() should return a string object
        assert isinstance(MediaPlugin.about(), str)
        # THEN: about() should return a non-empty string
        assert len(MediaPlugin.about()) != 0
