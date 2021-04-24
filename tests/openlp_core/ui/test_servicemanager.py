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
Package to test the openlp.core.ui.slidecontroller package.
"""
import PyQt5

from unittest import TestCase
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import ThemeLevel
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.common.enum import ServiceItemType
from openlp.core.lib.serviceitem import ItemCapabilities, ServiceItem
from openlp.core.ui.servicemanager import ServiceManager
from openlp.core.widgets.toolbar import OpenLPToolbar

from tests.helpers.testmixin import TestMixin


def test_initial_service_manager(registry):
    """
    Test the initial of service manager.
    """
    # GIVEN: A new service manager instance.
    ServiceManager(None)
    # WHEN: the default service manager is built.
    # THEN: The the controller should be registered in the registry.
    assert Registry().get('service_manager') is not None, 'The base service manager should be registered'


def test_create_basic_service(registry):
    """
    Test the create basic service array
    """
    # GIVEN: A new service manager instance.
    service_manager = ServiceManager(None)
    # WHEN: when the basic service array is created.
    service_manager._save_lite = False
    service_manager.service_theme = 'test_theme'
    service = service_manager.create_basic_service()[0]
    # THEN: The controller should be registered in the registry.
    assert service is not None, 'The base service should be created'
    assert service['openlp_core']['service-theme'] == 'test_theme', 'The test theme should be saved'
    assert service['openlp_core']['lite-service'] is False, 'The lite service should be saved'


def test_supported_suffixes(registry):
    """
    Test the create basic service array
    """
    # GIVEN: A new service manager instance.
    service_manager = ServiceManager(None)
    # WHEN: a suffix is added as an individual or a list.
    service_manager.supported_suffixes('txt')
    service_manager.supported_suffixes(['pptx', 'ppt'])
    # THEN: The suffixes should be available to test.
    assert 'txt' in service_manager.suffixes, 'The suffix txt should be in the list'
    assert 'ppt' in service_manager.suffixes, 'The suffix ppt should be in the list'
    assert 'pptx' in service_manager.suffixes, 'The suffix pptx should be in the list'


def test_build_context_menu(registry):
    """
    Test the creation of a context menu from a null service item.
    """
    # GIVEN: A new service manager instance and a default service item.
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have been called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have been called once'


def test_build_song_context_menu(registry, state):
    """
    Test the creation of a context menu from service item of type text from Songs.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    for capability in [ItemCapabilities.CanEdit, ItemCapabilities.CanPreview, ItemCapabilities.CanLoop,
                       ItemCapabilities.OnLoadUpdate, ItemCapabilities.AddIfNewItem,
                       ItemCapabilities.CanSoftBreak]:
        service_item.add_capability(capability)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_bible_context_menu(registry, state):
    """
    Test the creation of a context menu from service item of type text from Bibles.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    for capability in [ItemCapabilities.NoLineBreaks, ItemCapabilities.CanPreview,
                       ItemCapabilities.CanLoop, ItemCapabilities.CanWordSplit,
                       ItemCapabilities.CanEditTitle]:
        service_item.add_capability(capability)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_custom_context_menu(registry, state):
    """
    Test the creation of a context menu from service item of type text from Custom.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanEdit)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanSoftBreak)
    service_item.add_capability(ItemCapabilities.OnLoadUpdate)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_image_context_menu(registry):
    """
    Test the creation of a context menu from service item of type Image from Image.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanMaintain)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanAppend)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.service_item_type = ServiceItemType.Image
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    # THEN we add a 2nd display frame and regenerate the menu.
    service_item.slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_media_context_menu(registry):
    """
    Test the creation of a context menu from service item of type Command from Media.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.add_capability(ItemCapabilities.RequiresMedia)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    # THEN I change the length of the media and regenerate the menu.
    service_item.set_media_length(5)
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.time_action.setVisible.call_count == 3, 'Should have be called three times'


def test_build_presentation_pdf_context_menu(registry):
    """
    Test the creation of a context menu from service item of type Command with PDF from Presentation.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanMaintain)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanAppend)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'


def test_build_presentation_non_pdf_context_menu(registry):
    """
    Test the creation of a context menu from service item of type Command with Impress from Presentation.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'


@patch('PyQt5.QtCore.QTimer.singleShot')
def test_single_click_preview_true(mocked_singleShot, registry):
    """
    Test that when "Preview items when clicked in Service Manager" enabled the preview timer starts
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = True
    Registry().register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called
    service_manager.on_single_click_preview()
    # THEN: timer should have been started
    mocked_singleShot.assert_called_with(PyQt5.QtWidgets.QApplication.instance().doubleClickInterval(),
                                         service_manager.on_single_click_preview_timeout)


@patch('PyQt5.QtCore.QTimer.singleShot')
def test_single_click_preview_false(mocked_singleShot, registry):
    """
    Test that when "Preview items when clicked in Service Manager" disabled the preview timer doesn't start
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = False
    Registry().register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called
    service_manager.on_single_click_preview()
    # THEN: timer should not be started
    assert mocked_singleShot.call_count == 0, 'Should not be called'


@patch('PyQt5.QtCore.QTimer.singleShot')
@patch('openlp.core.ui.servicemanager.ServiceManager.make_live')
def test_single_click_preview_double(mocked_make_live, mocked_singleShot, registry):
    """
    Test that when a double click has registered the preview timer doesn't start
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = True
    Registry().register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called following a double click
    service_manager.on_double_click_live()
    service_manager.on_single_click_preview()
    # THEN: timer should not be started
    mocked_make_live.assert_called_with()
    assert mocked_singleShot.call_count == 0, 'Should not be called'


@patch('openlp.core.ui.servicemanager.ServiceManager.make_preview')
def test_single_click_timeout_single(mocked_make_preview, registry):
    """
    Test that when a single click has been registered, the item is sent to preview
    """
    # GIVEN: A service manager.
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called
    service_manager.on_single_click_preview_timeout()
    # THEN: make_preview() should have been called
    assert mocked_make_preview.call_count == 1, 'ServiceManager.make_preview() should have been called once'


@patch('openlp.core.ui.servicemanager.ServiceManager.make_preview')
@patch('openlp.core.ui.servicemanager.ServiceManager.make_live')
def test_single_click_timeout_double(mocked_make_live, mocked_make_preview, registry):
    """
    Test that when a double click has been registered, the item does not goes to preview
    """
    # GIVEN: A service manager.
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called after a double click
    service_manager.on_double_click_live()
    service_manager.on_single_click_preview_timeout()
    # THEN: make_preview() should not have been called
    assert mocked_make_preview.call_count == 0, 'ServiceManager.make_preview() should not be called'


@patch('openlp.core.ui.servicemanager.zipfile')
@patch('openlp.core.ui.servicemanager.ServiceManager.save_file_as')
@patch('openlp.core.ui.servicemanager.os')
def test_save_file_raises_permission_error(mocked_os, mocked_save_file_as, mocked_zipfile, registry):
    """
    Test that when a PermissionError is raised when trying to save a file, it is handled correctly
    """
    # GIVEN: A service manager, a service to save
    mocked_main_window = MagicMock()
    Registry().register('main_window', mocked_main_window)
    Registry().register('application', MagicMock())
    service_manager = ServiceManager(None)
    service_manager._service_path = MagicMock()
    service_manager._save_lite = False
    service_manager.service_items = []
    service_manager.service_theme = 'Default'
    service_manager.service_manager_list = MagicMock()
    mocked_save_file_as.return_value = True
    mocked_zipfile.ZipFile.return_value = MagicMock()
    mocked_os.link.side_effect = PermissionError

    # WHEN: The service is saved and a PermissionError is raised
    result = service_manager.save_file()

    # THEN: The "save_as" method is called to save the service
    assert result is True
    mocked_save_file_as.assert_called_with()


@patch('openlp.core.ui.servicemanager.zipfile')
@patch('openlp.core.ui.servicemanager.ServiceManager.save_file_as')
@patch('openlp.core.ui.servicemanager.os')
@patch('openlp.core.ui.servicemanager.len')
def test_save_file_large_file(mocked_len, mocked_os, mocked_save_file_as, mocked_zipfile, registry):
    """
    Test that when a file size size larger than a 32bit signed int is attempted to save, the progress bar
    should be provided a value that fits in a 32bit int (because it's passed to C++ as a 32bit unsigned int)
    """
    # GIVEN: A service manager, a service to save, and len() returns a huge value (file size)
    def check_for_i32_overflow(val):
        if val > 2147483647:
            raise OverflowError
    mocked_main_window = MagicMock()
    mocked_main_window.display_progress_bar.side_effect = check_for_i32_overflow
    Registry().register('main_window', mocked_main_window)
    Registry().register('application', MagicMock())
    mocked_settings = MagicMock()
    Registry().register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    service_manager._service_path = MagicMock()
    service_manager._save_lite = False
    service_manager.service_items = []
    service_manager.service_theme = 'Default'
    service_manager.service_manager_list = MagicMock()
    mocked_save_file_as.return_value = True
    mocked_zipfile.ZipFile.return_value = MagicMock()
    mocked_len.return_value = 10000000000000

    # WHEN: The service is saved and no error is raised
    result = service_manager.save_file()

    # THEN: The "save_as" method is called to save the service
    assert result is True
    mocked_save_file_as.assert_called_with()


@patch('openlp.core.ui.servicemanager.ServiceManager.regenerate_service_items')
def test_theme_change_global(mocked_regenerate_service_items, registry):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Global
    """
    # GIVEN: A service manager, settings set to Global theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = ThemeLevel.Global
    Registry().register('settings', mocked_settings)

    # WHEN: theme_change is called
    service_manager.theme_change()

    # THEN: The the theme toolbar should not be visible
    assert service_manager.toolbar.actions['theme_combo_box'].isVisible() is False, \
        'The visibility should be False'


@patch('openlp.core.ui.servicemanager.ServiceManager.regenerate_service_items')
def test_theme_change_service(mocked_regenerate_service_items, registry):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Theme
    """
    # GIVEN: A service manager, settings set to Service theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = ThemeLevel.Service
    Registry().register('settings', mocked_settings)

    # WHEN: theme_change is called
    service_manager.theme_change()

    # THEN: The the theme toolbar should be visible
    assert service_manager.toolbar.actions['theme_combo_box'].isVisible() is True, \
        'The visibility should be True'


@patch('openlp.core.ui.servicemanager.ServiceManager.regenerate_service_items')
def test_theme_change_song(mocked_regenerate_service_items, registry):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Song
    """
    # GIVEN: A service manager, settings set to Song theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = ThemeLevel.Song
    Registry().register('settings', mocked_settings)

    # WHEN: theme_change is called
    service_manager.theme_change()

    # THEN: The the theme toolbar should be visible
    assert service_manager.toolbar.actions['theme_combo_box'].isVisible() is True, \
        'The visibility should be True'


class TestServiceManager(TestCase, TestMixin):
    """
    Test the service manager
    """

    def _create_mock_action(self, name, **kwargs):
        """
        Create a fake action with some "real" attributes
        """
        action = QtWidgets.QAction(self.service_manager)
        action.setObjectName(name)
        if kwargs.get('triggers'):
            action.triggered.connect(kwargs.pop('triggers'))
        self.service_manager.toolbar.actions[name] = action
        return action

    def setUp(self):
        """
        Create the UI
        """
        Registry.create()
        self.setup_application()
        Registry().register('application', MagicMock())
        Registry().register('main_window', MagicMock())
        Registry().register('settings', Settings())
        self.service_manager = ServiceManager()
        self.add_toolbar_action_patcher = patch('openlp.core.ui.servicemanager.OpenLPToolbar.add_toolbar_action')
        self.mocked_add_toolbar_action = self.add_toolbar_action_patcher.start()
        self.mocked_add_toolbar_action.side_effect = self._create_mock_action

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        self.add_toolbar_action_patcher.stop()
        del self.service_manager

    def test_basic_service_manager(self):
        """
        Test the Service Manager UI Functionality
        """
        # GIVEN: A New Service Manager instance
        # WHEN I have set up the display
        self.service_manager.setup_ui(self.service_manager)

        # THEN the count of items should be zero
        assert self.service_manager.service_manager_list.topLevelItemCount() == 0, \
            'The service manager list should be empty '

    @patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt')
    @patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal')
    @patch('openlp.core.ui.servicemanager.QtWidgets.QMenu.exec')
    def test_default_context_menu(self, mocked_exec, mocked_mapToGlobal, mocked_item_at_method):
        """
        Test the context_menu() method with a default service item
        """
        # GIVEN: A service item added
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        mocked_item.data.return_value = 1
        self.service_manager.setup_ui(self.service_manager)
        # A service item without capabilities.
        service_item = ServiceItem()
        self.service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        self.service_manager.edit_action.setVisible = MagicMock()
        self.service_manager.create_custom_action.setVisible = MagicMock()
        self.service_manager.maintain_action.setVisible = MagicMock()
        self.service_manager.notes_action.setVisible = MagicMock()
        self.service_manager.time_action.setVisible = MagicMock()
        self.service_manager.auto_start_action.setVisible = MagicMock()

        # WHEN: Show the context menu.
        self.service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        self.service_manager.time_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'

    def test_edit_context_menu(self):
        """
        Test the context_menu() method with a edit service item
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanEdit)
            service_item.edit_id = 1
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_maintain_context_menu(self):
        """
        Test the context_menu() method with a maintain
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanMaintain)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_loopy_context_menu(self):
        """
        Test the context_menu() method with a loop
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanLoop)
            service_item.slides.append("One")
            service_item.slides.append("Two")
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_start_time_context_menu(self):
        """
        Test the context_menu() method with a start time
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.HasVariableStartTime)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_auto_start_context_menu(self):
        """
        Test the context_menu() method with can auto start
        """
        # GIVEN: A service item added
        self.service_manager.setup_ui(self.service_manager)
        with patch('PyQt5.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
                patch('PyQt5.QtWidgets.QWidget.mapToGlobal'), \
                patch('PyQt5.QtWidgets.QMenu.exec'):
            mocked_item = MagicMock()
            mocked_item.parent.return_value = None
            mocked_item_at_method.return_value = mocked_item
            # We want 1 to be returned for the position
            mocked_item.data.return_value = 1
            # A service item without capabilities.
            service_item = ServiceItem()
            service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
            self.service_manager.service_items = [{'service_item': service_item}]
            q_point = None
            # Mocked actions.
            self.service_manager.edit_action.setVisible = MagicMock()
            self.service_manager.create_custom_action.setVisible = MagicMock()
            self.service_manager.maintain_action.setVisible = MagicMock()
            self.service_manager.notes_action.setVisible = MagicMock()
            self.service_manager.time_action.setVisible = MagicMock()
            self.service_manager.auto_start_action.setVisible = MagicMock()
            self.service_manager.rename_action.setVisible = MagicMock()

            # WHEN: Show the context menu.
            self.service_manager.context_menu(q_point)

            # THEN: The following actions should be not visible.
            self.service_manager.edit_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.maintain_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
            self.service_manager.time_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'
            self.service_manager.auto_start_action.setVisible.assert_called_with(True), \
                'The action should be set visible.'
            self.service_manager.rename_action.setVisible.assert_called_once_with(False), \
                'The action should be set invisible.'

    def test_click_on_new_service(self):
        """
        Test the on_new_service event handler is called by the UI
        """
        # GIVEN: An initial form
        mocked_event = MagicMock()
        self.service_manager.on_new_service_clicked = mocked_event
        self.service_manager.setup_ui(self.service_manager)

        # WHEN displaying the UI and pressing cancel
        new_service = self.service_manager.toolbar.actions['newService']
        new_service.trigger()

        assert mocked_event.call_count == 1, 'The on_new_service_clicked method should have been called once'

    def test_expand_selection_on_right_arrow(self):
        """
        Test that a right arrow key press event calls the on_expand_selection function
        """
        # GIVEN a mocked expand function
        self.service_manager.on_expand_selection = MagicMock()

        # WHEN the right arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_expand_selection function should have been called.
        self.service_manager.on_expand_selection.assert_called_once_with()

    def test_collapse_selection_on_left_arrow(self):
        """
        Test that a left arrow key press event calls the on_collapse_selection function
        """
        # GIVEN a mocked collapse function
        self.service_manager.on_collapse_selection = MagicMock()

        # WHEN the left arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Left, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_collapse_selection function should have been called.
        self.service_manager.on_collapse_selection.assert_called_once_with()

    def test_move_selection_down_on_down_arrow(self):
        """
        Test that a down arrow key press event calls the on_move_selection_down function
        """
        # GIVEN a mocked move down function
        self.service_manager.on_move_selection_down = MagicMock()

        # WHEN the down arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Down, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_move_selection_down function should have been called.
        self.service_manager.on_move_selection_down.assert_called_once_with()

    def test_move_selection_up_on_up_arrow(self):
        """
        Test that an up arrow key press event calls the on_move_selection_up function
        """
        # GIVEN a mocked move up function
        self.service_manager.on_move_selection_up = MagicMock()

        # WHEN the up arrow key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Up, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_move_selection_up function should have been called.
        self.service_manager.on_move_selection_up.assert_called_once_with()

    def test_delete_selection_on_delete_key(self):
        """
        Test that a delete key press event calls the on_delete_from_service function
        """
        # GIVEN a mocked on_delete_from_service function
        self.service_manager.on_delete_from_service = MagicMock()

        # WHEN the delete key event is called
        self.service_manager.setup_ui(self.service_manager)
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier)
        self.service_manager.service_manager_list.keyPressEvent(event)

        # THEN the on_delete_from_service function should have been called.
        self.service_manager.on_delete_from_service.assert_called_once_with()

    def _setup_service_manager_list(self):
        self.service_manager.expanded = MagicMock()
        self.service_manager.collapsed = MagicMock()
        verse_1 = QtWidgets.QTreeWidgetItem(0)
        verse_2 = QtWidgets.QTreeWidgetItem(0)
        song_item = QtWidgets.QTreeWidgetItem(0)
        song_item.addChild(verse_1)
        song_item.addChild(verse_2)
        self.service_manager.setup_ui(self.service_manager)
        self.service_manager.service_manager_list.addTopLevelItem(song_item)
        return verse_1, verse_2, song_item

    def test_on_expand_selection(self):
        """
        Test that the on_expand_selection function successfully expands an item and moves to its first child
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(song_item)
        # Reset expanded function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.expanded = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_expand_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        above_selected_index = self.service_manager.service_manager_list.indexAbove(selected_index)
        assert self.service_manager.service_manager_list.isExpanded(above_selected_index) is True, \
            'Item should have been expanded'
        self.service_manager.expanded.assert_called_once_with(song_item)

    def test_on_collapse_selection_with_parent_selected(self):
        """
        Test that the on_collapse_selection function successfully collapses an item
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(song_item)
        self.service_manager.service_manager_list.expandItem(song_item)

        # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.collapsed = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_collapse_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        assert self.service_manager.service_manager_list.isExpanded(selected_index) is False, \
            'Item should have been collapsed'
        assert self.service_manager.service_manager_list.currentItem() == song_item, \
            'Top item should have been selected'
        self.service_manager.collapsed.assert_called_once_with(song_item)

    def test_on_collapse_selection_with_child_selected(self):
        """
        Test that the on_collapse_selection function successfully collapses child's parent item
        and moves selection to its parent.
        """
        # GIVEN a mocked servicemanager list
        verse_1, verse_2, song_item = self._setup_service_manager_list()
        self.service_manager.service_manager_list.setCurrentItem(verse_2)
        self.service_manager.service_manager_list.expandItem(song_item)
        # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
        self.service_manager.collapsed = MagicMock()

        # WHEN on_expand_selection is called
        self.service_manager.on_collapse_selection()

        # THEN selection should be expanded
        selected_index = self.service_manager.service_manager_list.currentIndex()
        assert self.service_manager.service_manager_list.isExpanded(selected_index) is False, \
            'Item should have been collapsed'
        assert self.service_manager.service_manager_list.currentItem() == song_item, \
            'Top item should have been selected'
        self.service_manager.collapsed.assert_called_once_with(song_item)

    def test_replace_service_item(self):
        """
        Tests that the replace_service_item function replaces items as expected
        """
        # GIVEN a service item list and a new item which name and edit_id match a service item
        self.service_manager.repaint_service_list = MagicMock()
        Registry().register('live_controller', MagicMock())
        item1 = MagicMock()
        item1.edit_id = 'abcd'
        item1.name = 'itemA'
        item2 = MagicMock()
        item2.edit_id = 'abcd'
        item2.name = 'itemB'
        item3 = MagicMock()
        item3.edit_id = 'cfgh'
        item3.name = 'itemA'
        self.service_manager.service_items = [
            {'service_item': item1},
            {'service_item': item2},
            {'service_item': item3}
        ]
        new_item = MagicMock()
        new_item.edit_id = 'abcd'
        new_item.name = 'itemA'

        # WHEN replace_service_item is called
        self.service_manager.replace_service_item(new_item)

        # THEN new_item should replace item1, and only replaces that one item
        assert self.service_manager.service_items[0]['service_item'] == new_item
        new_item.merge.assert_called_once_with(item1)
