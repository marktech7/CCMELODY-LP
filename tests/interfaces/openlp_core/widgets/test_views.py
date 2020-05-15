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
    Package to test the openlp.core.widgets.views.
"""
import pytest
from unittest.mock import patch

from PyQt5 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.lib.serviceitem import ServiceItem
from openlp.core.widgets.views import ListPreviewWidget
from tests.utils.osdinteraction import read_service_from_file


@pytest.fixture()
def preview_widget(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    p_widget = ListPreviewWidget(main_window, 2)
    return p_widget


def test_initial_slide_count(preview_widget):
    """
    Test the initial slide count .
    """
    # GIVEN: A new ListPreviewWidget instance.
    # WHEN: No SlideItem has been added yet.
    # THEN: The count of items should be zero.
    assert preview_widget.slide_count() == 0, 'The slide list should be empty.'


def test_initial_slide_number(preview_widget):
    """
    Test the initial current slide number.
    """
    # GIVEN: A new ListPreviewWidget instance.
    # WHEN: No SlideItem has been added yet.
    # THEN: The number of the current item should be -1.
    assert preview_widget.current_slide_number() == -1, 'The slide number should be -1.'


def test_replace_service_item(preview_widget, state_media):
    """
    Test item counts and current number with a service item.
    """
    # GIVEN: A ServiceItem with two frames.
    service_item = ServiceItem(None)
    service = read_service_from_file('serviceitem_image_3.osj')
    with patch('os.path.exists') and patch('openlp.core.lib.serviceitem.sha256_file_hash'):
        service_item.set_from_service(service[0])
    # WHEN: Added to the preview widget.
    preview_widget.replace_service_item(service_item, 1, 1)
    # THEN: The slide count and number should fit.
    assert preview_widget.slide_count() == 2, 'The slide count should be 2.'
    assert preview_widget.current_slide_number() == 1, 'The current slide number should  be 1.'


def test_change_slide(preview_widget, state_media):
    """
    Test the change_slide method.
    """
    # GIVEN: A ServiceItem with two frames content.
    service_item = ServiceItem(None)
    service = read_service_from_file('serviceitem_image_3.osj')
    with patch('os.path.exists') and patch('openlp.core.lib.serviceitem.sha256_file_hash'):
        service_item.set_from_service(service[0])
    # WHEN: Added to the preview widget and switched to the second frame.
    preview_widget.replace_service_item(service_item, 1, 0)
    preview_widget.change_slide(1)
    # THEN: The current_slide_number should reflect the change.
    assert preview_widget.current_slide_number() == 1, 'The current slide number should  be 1.'
