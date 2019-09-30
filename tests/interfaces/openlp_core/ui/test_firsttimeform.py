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
Package to test the openlp.core.ui.firsttimeform package.
"""
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from openlp.core.common.registry import Registry
from openlp.core.ui.firsttimeform import ThemeListWidgetItem
from openlp.core.ui.icons import UiIcons
from tests.helpers.testmixin import TestMixin


class TestThemeListWidgetItem(TestCase, TestMixin):
    def setUp(self):
        self.sample_theme_data = {'file_name': 'BlueBurst.otz', 'sha256': 'sha_256_hash',
                                  'thumbnail': 'BlueBurst.png', 'title': 'Blue Burst'}
        Registry.create()
        self.registry = Registry()
        mocked_app = MagicMock()
        mocked_app.worker_threads = {}
        Registry().register('application', mocked_app)
        self.setup_application()

        move_to_thread_patcher = patch('openlp.core.ui.firsttimeform.DownloadWorker.moveToThread')
        self.addCleanup(move_to_thread_patcher.stop)
        move_to_thread_patcher.start()
        set_icon_patcher = patch('openlp.core.ui.firsttimeform.ThemeListWidgetItem.setIcon')
        self.addCleanup(set_icon_patcher.stop)
        self.mocked_set_icon = set_icon_patcher.start()
        q_thread_patcher = patch('openlp.core.ui.firsttimeform.QtCore.QThread')
        self.addCleanup(q_thread_patcher.stop)
        q_thread_patcher.start()

    def test_failed_download(self):
        """
        Test that icon get set to indicate a failure when `DownloadWorker` emits the download_failed signal
        """
        # GIVEN: An instance of `DownloadWorker`
        instance = ThemeListWidgetItem('url', self.sample_theme_data, MagicMock())  # noqa Overcome GC issue
        worker_threads = Registry().get('application').worker_threads
        worker = worker_threads['thumbnail_download_BlueBurst.png']['worker']

        # WHEN: `DownloadWorker` emits the `download_failed` signal
        worker.download_failed.emit()

        # THEN: Then the initial loading icon should have been replaced by the exception icon
        self.mocked_set_icon.assert_has_calls([call(UiIcons().picture), call(UiIcons().exception)])

    @patch('openlp.core.ui.firsttimeform.build_icon')
    def test_successful_download(self, mocked_build_icon):
        """
        Test that the downloaded thumbnail is set as the icon when `DownloadWorker` emits the `download_succeeded`
        signal
        """
        # GIVEN: An instance of `DownloadWorker`
        instance = ThemeListWidgetItem('url', self.sample_theme_data, MagicMock())  # noqa Overcome GC issue
        worker_threads = Registry().get('application').worker_threads
        worker = worker_threads['thumbnail_download_BlueBurst.png']['worker']
        test_path = Path('downlaoded', 'file')

        # WHEN: `DownloadWorker` emits the `download_succeeded` signal
        worker.download_succeeded.emit(test_path)

        # THEN: An icon should have been built from the downloaded file and used to replace the loading icon
        mocked_build_icon.assert_called_once_with(test_path)
        self.mocked_set_icon.assert_has_calls([call(UiIcons().picture), call(mocked_build_icon())])
