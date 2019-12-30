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
from unittest import TestCase
from unittest.mock import MagicMock

from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus

from tests.helpers.testmixin import TestMixin

"""
Test the Status class.
"""


class TestState(TestCase, TestMixin):
    """
    Test the Server Class used to check if OpenLP is running.
    """
    def setUp(self):
        Registry.create()

    def tearDown(self):
        pass

    def test_add_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service
        State().add_service("test", 1, PluginStatus.Active)

        # THEN I have a saved service
        assert len(State().modules) == 1

    def test_add_service_multiple(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service twice
        State().add_service("test", 1, PluginStatus.Active)
        State().add_service("test", 1, PluginStatus.Active)

        # THEN I have a single saved service
        assert len(State().modules) == 1

    def test_add_service_multiple_depend(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service twice
        State().add_service("test", 1, 1, PluginStatus.Active)
        State().add_service("test1", 1, 1, PluginStatus.Active, "test")
        State().add_service("test1", 1, 1, PluginStatus.Active, "test")

        # THEN I have still have a single saved service and one dependency
        assert len(State().modules) == 2
        assert len(State().modules['test'].required_by) == 1

    def test_add_service_multiple_depends(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service twice
        State().add_service("test", 1, 1, PluginStatus.Active)
        State().add_service("test1", 1, 1, PluginStatus.Active, "test")
        State().add_service("test2", 1, 1, PluginStatus.Active, "test")

        # THEN I have a 3 modules and 2 dependencies
        assert len(State().modules) == 3
        assert len(State().modules['test'].required_by) == 2

    def test_active_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service which is Active
        State().add_service("test", 1, 1, PluginStatus.Active)

        # THEN I have a single saved service
        assert State().is_module_active('test') is True

    def test_inactive_service(self):
        # GIVEN a new state
        State().load_settings()

        # WHEN I add a new service which is Inactive
        State().add_service("test", 1, 1, PluginStatus.Inactive)

        # THEN I have a single saved service
        assert State().is_module_active('test') is False

    def test_basic_preconditions_fail(self):
        # GIVEN a new state
        State().load_settings()
        Registry().register('test_plugin', MagicMock())

        # WHEN I add a new services with dependencies and a failed pre condition
        State().add_service("test", 1, 1, PluginStatus.Inactive)
        State().add_service("test2", 1, 1, PluginStatus.Inactive)
        State().add_service("test1", 1, 1, PluginStatus.Inactive, 'test')
        State().update_pre_conditions('test', False)

        # THEN correct the state when I flush the preconditions
        assert State().modules['test'].pass_preconditions is False
        assert State().modules['test2'].pass_preconditions is False
        assert State().modules['test1'].pass_preconditions is False
        State().flush_preconditions()
        assert State().modules['test'].pass_preconditions is False
        assert State().modules['test2'].pass_preconditions is False
        assert State().modules['test1'].pass_preconditions is False

    def test_basic_preconditions_pass(self):
        # GIVEN a new state
        State().load_settings()
        Registry().register('test_plugin', MagicMock())

        # WHEN I add a new services with dependencies and a failed pre condition
        State().add_service("test", 1, 1, PluginStatus.Inactive)
        State().add_service("test2", 1, 1, PluginStatus.Inactive)
        State().add_service("test1", 1, 1, PluginStatus.Inactive, 'test')
        State().update_pre_conditions('test', True)

        # THEN correct the state when I flush the preconditions
        assert State().modules['test'].pass_preconditions is True
        assert State().modules['test2'].pass_preconditions is False
        assert State().modules['test1'].pass_preconditions is False
        State().flush_preconditions()
        assert State().modules['test'].pass_preconditions is True
        assert State().modules['test2'].pass_preconditions is False
        assert State().modules['test1'].pass_preconditions is True
