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
This module contains tests for the upgrade submodule of the Bibles plugin.
"""
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from sqlalchemy import create_engine

from openlp.core.common.settings import ProxyMode
from openlp.core.lib.db import upgrade_db
from openlp.plugins.bibles.lib import upgrade
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import RESOURCE_PATH


class TestUpgrade(TestCase, TestMixin):
    """
    Test the `upgrade_2` function in the :mod:`upgrade` module when the db does not contains proxy metadata
    """

    def setUp(self):
        """
        Setup for tests
        """
        self.tmp_path = Path(mkdtemp())
        db_path = RESOURCE_PATH / 'bibles' / 'web-bible-2.4.6-v1.sqlite'
        db_tmp_path = self.tmp_path / 'web-bible-2.4.6-v1.sqlite'
        shutil.copyfile(db_path, db_tmp_path)
        self.db_url = 'sqlite:///' + str(db_tmp_path)

        patched_settings = patch('openlp.plugins.bibles.lib.upgrade.Settings')
        self.mocked_settings = patched_settings.start()
        self.addCleanup(patched_settings.stop)
        self.mocked_settings_instance = MagicMock()
        self.mocked_settings.return_value = self.mocked_settings_instance

        patched_message_box = patch('openlp.plugins.bibles.lib.upgrade.QtWidgets.QMessageBox')
        self.mocked_message_box = patched_message_box.start()
        self.addCleanup(patched_message_box.stop)

    def tearDown(self):
        """
        Clean up after tests
        """
        # Ignore errors since windows can have problems with locked files
        shutil.rmtree(self.tmp_path, ignore_errors=True)

    def test_upgrade_2_none_selected(self):
        """
        Test that upgrade 2 completes properly when the user chooses not to use a proxy ('No')
        """
        # GIVEN: An version 1 web bible with proxy settings

        # WHEN: Calling upgrade_db and the user has 'clicked' the 'No' button
        upgrade_db(self.db_url, upgrade)

        # THEN: The proxy meta data should have been removed, and the version should have been changed to version 2
        self.mocked_message_box.assert_not_called()
        engine = create_engine(self.db_url)
        conn = engine.connect()
        assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'


class TestProxyMetaUpgrade(TestCase, TestMixin):
    """
    Test the `upgrade_2` function in the :mod:`upgrade` module when the db contains proxy metadata
    """

    def setUp(self):
        """
        Setup for tests
        """
        self.tmp_path = Path(mkdtemp())
        db_path = RESOURCE_PATH / 'bibles' / 'web-bible-2.4.6-proxy-meta-v1.sqlite'
        db_tmp_path = self.tmp_path / 'web-bible-2.4.6-proxy-meta-v1.sqlite'
        shutil.copyfile(db_path, db_tmp_path)
        self.db_url = 'sqlite:///' + str(db_tmp_path)

        patched_settings = patch('openlp.plugins.bibles.lib.upgrade.Settings')
        self.mocked_settings = patched_settings.start()
        self.addCleanup(patched_settings.stop)
        self.mocked_settings_instance = MagicMock()
        self.mocked_settings.return_value = self.mocked_settings_instance

        patched_message_box = patch('openlp.plugins.bibles.lib.upgrade.QtWidgets.QMessageBox')
        mocked_message_box = patched_message_box.start()
        self.addCleanup(patched_message_box.stop)
        self.mocked_no_button = MagicMock()
        self.mocked_http_button = MagicMock()
        self.mocked_both_button = MagicMock()
        self.mocked_https_button = MagicMock()
        self.mocked_message_box_instance = MagicMock(
            **{'addButton.side_effect': [self.mocked_no_button, self.mocked_http_button,
                                         self.mocked_both_button, self.mocked_https_button]})
        mocked_message_box.return_value = self.mocked_message_box_instance

    def tearDown(self):
        """
        Clean up after tests
        """
        # Ignore errors since windows can have problems with locked files
        shutil.rmtree(self.tmp_path, ignore_errors=True)

    def test_upgrade_2_none_selected(self):
        """
        Test that upgrade 2 completes properly when the user chooses not to use a proxy ('No')
        """
        # GIVEN: An version 1 web bible with proxy settings

        # WHEN: Calling upgrade_db and the user has 'clicked' the 'No' button
        self.mocked_message_box_instance.clickedButton.return_value = self.mocked_no_button
        upgrade_db(self.db_url, upgrade)

        # THEN: The proxy meta data should have been removed, and the version should have been changed to version 2
        engine = create_engine(self.db_url)
        conn = engine.connect()
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
        assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'
        self.mocked_settings_instance.setValue.assert_not_called()

    def test_upgrade_2_http_selected(self):
        """
        Test that upgrade 2 completes properly when the user chooses to use a HTTP proxy
        """
        # GIVEN: An version 1 web bible with proxy settings

        # WHEN: Calling upgrade_db and the user has 'clicked' the 'HTTP' button
        self.mocked_message_box_instance.clickedButton.return_value = self.mocked_http_button
        upgrade_db(self.db_url, upgrade)

        # THEN: The proxy meta data should have been removed, the version should have been changed to version 2, and the
        #       proxy server saved to the settings
        engine = create_engine(self.db_url)
        conn = engine.connect()
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
        assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

        assert self.mocked_settings_instance.setValue.call_args_list == [
            call('advanced/proxy http', 'proxy_server'), call('advanced/proxy username', 'proxy_username'),
            call('advanced/proxy password', 'proxy_password'), call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]

    def test_upgrade_2_https_selected(self):
        """
        Tcest that upgrade 2 completes properly when the user chooses to use a HTTPS proxy
        """
        # GIVEN: An version 1 web bible with proxy settings

        # WHEN: Calling upgrade_db and the user has 'clicked' the 'HTTPS' button
        self.mocked_message_box_instance.clickedButton.return_value = self.mocked_https_button
        upgrade_db(self.db_url, upgrade)

        # THEN: The proxy settings should have been removed, the version should have been changed to version 2, and the
        #       proxy server saved to the settings
        engine = create_engine(self.db_url)
        conn = engine.connect()
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
        assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

        assert self.mocked_settings_instance.setValue.call_args_list == [
            call('advanced/proxy https', 'proxy_server'), call('advanced/proxy username', 'proxy_username'),
            call('advanced/proxy password', 'proxy_password'), call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]

    def test_upgrade_2_both_selected(self):
        """
        Tcest that upgrade 2 completes properly when the user chooses to use a both HTTP and HTTPS proxies
        """

        # GIVEN: An version 1 web bible with proxy settings

        # WHEN: Calling upgrade_db
        self.mocked_message_box_instance.clickedButton.return_value = self.mocked_both_button
        upgrade_db(self.db_url, upgrade)

        # THEN: The proxy settings should have been removed, the version should have been changed to version 2, and the
        #       proxy server saved to the settings
        engine = create_engine(self.db_url)
        conn = engine.connect()
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
        assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
        assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

        assert self.mocked_settings_instance.setValue.call_args_list == [
            call('advanced/proxy http', 'proxy_server'), call('advanced/proxy https', 'proxy_server'),
            call('advanced/proxy username', 'proxy_username'), call('advanced/proxy password', 'proxy_password'),
            call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]
