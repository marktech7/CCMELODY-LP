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
Package to test the openlp.core.ui.firsttimeform package.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from openlp.core.common.registry import Registry
from openlp.core.ui.firsttimeform import ThemeListWidgetItem
from openlp.core.ui.icons import UiIcons

sample_theme_data = {'file_name': 'BlueBurst.otz', 'sha256': 'sha_256_hash',
                     'thumbnail': 'BlueBurst.png', 'title': 'Blue Burst'}


@pytest.yield_fixture()
def mocked_set_icon(mock_settings):
    move_to_thread_patcher = patch('openlp.core.ui.firsttimeform.DownloadWorker.moveToThread').start()
    set_icon_patcher = patch('openlp.core.ui.firsttimeform.ThemeListWidgetItem.setIcon').start()
    q_thread_patcher = patch('openlp.core.ui.firsttimeform.QtCore.QThread').start()
    mocked_app = MagicMock()
    mocked_app.worker_threads = {}
    Registry().remove('application')
    Registry().register('application', mocked_app)
    yield set_icon_patcher
    move_to_thread_patcher.stop()
    set_icon_patcher.stop()
    q_thread_patcher.stop()


def test_failed_download(mocked_set_icon):
    """
    Test that icon get set to indicate a failure when `DownloadWorker` emits the download_failed signal
    """
    # GIVEN: An instance of `DownloadWorker`
    instance = ThemeListWidgetItem('url', sample_theme_data, MagicMock())  # noqa Overcome GC issue
    worker_threads = Registry().get('application').worker_threads
    worker = worker_threads['thumbnail_download_BlueBurst.png']['worker']

    # WHEN: `DownloadWorker` emits the `download_failed` signal
    worker.download_failed.emit()

    # THEN: Then the initial loading icon should have been replaced by the exception icon
    mocked_set_icon.assert_has_calls([call(UiIcons().picture), call(UiIcons().exception)])


@patch('openlp.core.ui.firsttimeform.build_icon')
def test_successful_download(mocked_build_icon, mocked_set_icon):
    """
    Test that the downloaded thumbnail is set as the icon when `DownloadWorker` emits the `download_succeeded`
    signal
    """
    # GIVEN: An instance of `DownloadWorker`
    instance = ThemeListWidgetItem('url', sample_theme_data, MagicMock())  # noqa Overcome GC issue
    worker_threads = Registry().get('application').worker_threads
    worker = worker_threads['thumbnail_download_BlueBurst.png']['worker']
    test_path = Path('downlaoded', 'file')

    # WHEN: `DownloadWorker` emits the `download_succeeded` signal
    worker.download_succeeded.emit(test_path)

    # THEN: An icon should have been built from the downloaded file and used to replace the loading icon
    mocked_build_icon.assert_called_once_with(test_path)
    mocked_set_icon.assert_has_calls([call(UiIcons().picture), call(mocked_build_icon())])
