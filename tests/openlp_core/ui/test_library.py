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
from unittest.mock import MagicMock

from PyQt5 import QtCore, QtWidgets

from openlp.core.ui.library import FolderLibraryItem


def test_folderlibrary_create_item_from_id(registry, settings):
    """Test the create_item_from_id method"""
    # GIVEN: An instance of the FolderLibraryItem
    mocked_item = MagicMock()
    mocked_manager = MagicMock()
    mocked_manager.get_object_filtered.return_value = mocked_item
    MockFolder = MagicMock()
    MockItem = MagicMock()
    library_item = FolderLibraryItem(None, MagicMock(manager=mocked_manager), MockFolder, MockItem)

    # WHEN: create_item_from_id is called
    result = library_item.create_item_from_id('path/to/video.mp4')

    # THEN: The result should be a QTreeWidgetItem with a mocked object as data
    assert isinstance(result, QtWidgets.QTreeWidgetItem)
    assert result.data(0, QtCore.Qt.UserRole) is mocked_item
