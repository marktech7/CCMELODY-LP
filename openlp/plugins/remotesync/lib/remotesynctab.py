# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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

import os.path

from enum import IntEnum
from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

from openlp.core.common.settings import Settings
from openlp.core.common.registry import Registry
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate
from openlp.core.lib import build_icon
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.widgets.edits import PathEdit
from openlp.core.widgets.enums import PathEditType
from openlp.plugins.remotesync.lib.backends.ftpsynchronizer import FtpType

class SyncType(IntEnum):
    """
    The synchronization types available
    """
    Disabled = 0
    Folder = 1
    Ftp = 2


class RemoteSyncTab(SettingsTab):
    """
    RemoteSyncTab is the RemoteSync settings tab in the settings dialog.
    """
    def setup_ui(self):
        self.setObjectName('RemoteSyncTab')
        super(RemoteSyncTab, self).setup_ui()
        # sync type setup
        self.sync_type_group_box = QtWidgets.QGroupBox(self.left_column)
        self.sync_type_group_box.setObjectName('sync_type_group_box')
        self.sync_type_group_box_layout = QtWidgets.QFormLayout(self.sync_type_group_box)
        self.sync_type_group_box_layout.setObjectName('sync_type_group_box_layout')
        self.sync_type_label = QtWidgets.QLabel(self.sync_type_group_box)
        self.sync_type_label.setObjectName('sync_type_label')
        self.sync_type_radio_group = QtWidgets.QButtonGroup(self)
        self.disabled_sync_radio = QtWidgets.QRadioButton('', self)
        self.sync_type_radio_group.addButton(self.disabled_sync_radio, SyncType.Disabled)
        self.sync_type_group_box_layout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.disabled_sync_radio)
        self.folder_sync_radio = QtWidgets.QRadioButton('', self)
        self.sync_type_radio_group.addButton(self.folder_sync_radio, SyncType.Folder)
        self.sync_type_group_box_layout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.folder_sync_radio)
        self.ftp_sync_radio = QtWidgets.QRadioButton('', self)
        self.sync_type_radio_group.addButton(self.ftp_sync_radio, SyncType.Ftp)
        self.sync_type_group_box_layout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.ftp_sync_radio)
        self.left_layout.addWidget(self.sync_type_group_box)
        # Folder sync settings
        self.folder_settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.folder_settings_group_box.setObjectName('folder_settings_group_box')
        self.folder_settings_layout = QtWidgets.QFormLayout(self.folder_settings_group_box)
        self.folder_settings_layout.setObjectName('folder_settings_layout')
        # Sync folder path
        self.folder_label = QtWidgets.QLabel(self.folder_settings_group_box)
        self.folder_label.setObjectName('folder_label')
        self.folder_path_edit = PathEdit(self.folder_settings_group_box, path_type=PathEditType.Directories,
                                         show_revert=False)
        self.folder_settings_layout.addRow(self.folder_label, self.folder_path_edit)
        self.left_layout.addWidget(self.folder_settings_group_box)
        # FTP server settings
        self.ftp_settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.ftp_settings_group_box.setObjectName('ftp_settings_group_box')
        self.ftp_settings_layout = QtWidgets.QFormLayout(self.ftp_settings_group_box)
        self.ftp_settings_layout.setObjectName('ftp_settings_layout')
        self.ftp_type_label = QtWidgets.QLabel(self.ftp_settings_group_box)
        self.ftp_type_label.setObjectName('ftp_type_label')
        # FTP type
        self.ftp_type_radio_group = QtWidgets.QButtonGroup(self)
        self.ftp_unsecure_radio = QtWidgets.QRadioButton('', self)
        self.ftp_type_radio_group.addButton(self.ftp_unsecure_radio, FtpType.Ftp)
        self.ftp_settings_layout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.ftp_unsecure_radio)
        self.ftp_secure_radio = QtWidgets.QRadioButton('', self)
        self.ftp_type_radio_group.addButton(self.ftp_secure_radio, FtpType.FtpTls)
        self.ftp_settings_layout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.ftp_secure_radio)
        self.left_layout.addWidget(self.sync_type_group_box)
        # FTP server address
        self.ftp_address_label = QtWidgets.QLabel(self.ftp_settings_group_box)
        self.ftp_address_label.setObjectName('address_label')
        self.ftp_address_edit = QtWidgets.QLineEdit(self.ftp_settings_group_box)
        self.ftp_address_edit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.ftp_address_edit.setObjectName('address_edit')
        self.ftp_settings_layout.addRow(self.ftp_address_label, self.ftp_address_edit)
        # FTP server username
        self.ftp_username_label = QtWidgets.QLabel(self.ftp_settings_group_box)
        self.ftp_username_label.setObjectName('ftp_username_label')
        self.ftp_username_edit = QtWidgets.QLineEdit(self.ftp_settings_group_box)
        self.ftp_username_edit.setObjectName('ftp_username_edit')
        self.ftp_settings_layout.addRow(self.ftp_username_label, self.ftp_username_edit)
        # FTP server password
        self.ftp_pswd_label = QtWidgets.QLabel(self.ftp_settings_group_box)
        self.ftp_pswd_label.setObjectName('ftp_pswd_label')
        self.ftp_pswd_edit = QtWidgets.QLineEdit(self.ftp_settings_group_box)
        self.ftp_pswd_edit.setObjectName('ftp_pswd_edit')
        self.ftp_settings_layout.addRow(self.ftp_pswd_label, self.ftp_pswd_edit)
        # FTP server data folder
        self.ftp_folder_label = QtWidgets.QLabel(self.ftp_settings_group_box)
        self.ftp_folder_label.setObjectName('ftp_folder_label')
        self.ftp_folder_edit = QtWidgets.QLineEdit(self.ftp_settings_group_box)
        self.ftp_folder_edit.setObjectName('ftp_folder_edit')
        self.ftp_settings_layout.addRow(self.ftp_folder_label, self.ftp_folder_edit)
        self.left_layout.addWidget(self.ftp_settings_group_box)

        """
        # Manual trigger actions
        self.actions_group_box = QtWidgets.QGroupBox(self.left_column)
        self.actions_group_box.setObjectName('actions_group_box')
        self.actions_layout = QtWidgets.QFormLayout(self.actions_group_box)
        self.actions_layout.setObjectName('actions_layout')
        # send songs
        self.send_songs_btn = QtWidgets.QPushButton(self.actions_group_box)
        self.send_songs_btn.setObjectName('send_songs_btn')
        self.send_songs_btn.clicked.connect(self.on_send_songs_clicked)
        # receive songs
        self.receive_songs_btn = QtWidgets.QPushButton(self.actions_group_box)
        self.receive_songs_btn.setObjectName('receive_songs_btn')
        self.receive_songs_btn.clicked.connect(self.on_receive_songs_clicked)
        self.actions_layout.addRow(self.send_songs_btn, self.receive_songs_btn)
        self.left_layout.addWidget(self.actions_group_box)
        """

        self.remote_statistics_group_box = QtWidgets.QGroupBox(self.left_column)
        self.remote_statistics_group_box.setObjectName('remote_statistics_group_box')
        self.remote_statistics_layout = QtWidgets.QFormLayout(self.remote_statistics_group_box)
        self.remote_statistics_layout.setObjectName('remote_statistics_layout')
        self.update_policy_label = QtWidgets.QLabel(self.remote_statistics_group_box)
        self.update_policy_label.setObjectName('update_policy_label')
        self.update_policy = QtWidgets.QLabel(self.remote_statistics_group_box)
        self.update_policy.setObjectName('update_policy')
        self.remote_statistics_layout.addRow(self.update_policy_label, self.update_policy)
        self.last_sync_label = QtWidgets.QLabel(self.remote_statistics_group_box)
        self.last_sync_label.setObjectName('last_sync_label')
        self.last_sync = QtWidgets.QLabel(self.remote_statistics_group_box)
        self.last_sync.setObjectName('last_sync')
        self.remote_statistics_layout.addRow(self.last_sync_label, self.last_sync)
        self.left_layout.addWidget(self.remote_statistics_group_box)

        self.left_layout.addStretch()
        self.right_column.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.right_layout.addStretch()

    def retranslate_ui(self):
        self.sync_type_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Synchronization Type'))
        self.disabled_sync_radio.setText(translate('RemotePlugin.RemoteSyncTab', 'Disabled'))
        self.folder_sync_radio.setText(translate('RemotePlugin.RemoteSyncTab', 'Folder'))
        self.folder_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Synchronization Folder'))
        self.ftp_sync_radio.setText(translate('RemotePlugin.RemoteSyncTab', 'FTP'))
        self.folder_settings_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Folder Settings'))
        self.ftp_settings_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'FTP Settings'))
        self.ftp_unsecure_radio.setText(translate('RemotePlugin.RemoteSyncTab', 'FTP (unencrypted)'))
        self.ftp_secure_radio.setText(translate('RemotePlugin.RemoteSyncTab', 'FTPS (encrypted)'))
        #self.ftp_type_label.setText(translate('RemotePlugin.RemoteSyncTab', 'FTP Type:'))
        self.ftp_address_label.setText(translate('RemotePlugin.RemoteSyncTab', 'FTP server address:'))
        self.ftp_username_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Username:'))
        self.ftp_pswd_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Password:'))
        self.ftp_folder_label.setText(translate('RemotePlugin.RemoteSyncTab', 'FTP data folder:'))
        #self.actions_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Actions'))
        #self.receive_songs_btn.setText(translate('RemotePlugin.RemoteSyncTab', 'Receive Songs'))
        #self.send_songs_btn.setText(translate('RemotePlugin.RemoteSyncTab', 'Send Songs'))
        self.remote_statistics_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Remote Statistics'))
        self.update_policy_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Update Policy:'))
        self.last_sync_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Last Sync:'))

    def load(self):
        """
        Load the configuration and update the server configuration if necessary
        """
        #self.port_spin_box.setValue(Settings().value(self.settings_section + '/port'))
        #self.address_edit.setText(Settings().value(self.settings_section + '/ip address'))
        #self.auth_token.setText(Settings().value(self.settings_section + '/auth token'))
        pass

    def save(self):
        """
        Save the configuration and update the server configuration if necessary
        """
        #Settings().setValue(self.settings_section + '/port', self.port_spin_box.value())
        #Settings().setValue(self.settings_section + '/ip address', self.address_edit.text())
        #Settings().setValue(self.settings_section + '/auth token', self.auth_token.text())
        self.generate_icon()

    def on_send_songs_clicked(self):
        Registry().execute('synchronize_to_remote')
        #self.remote_synchronizer.send_all_songs()

    def on_receive_songs_clicked(self):
        Registry().execute('synchronize_from_remote')
        #self.remote_synchronizer.receive_songs()

    def generate_icon(self):
        """
        Generate icon for main window
        """
        self.remote_sync_icon.hide()
        icon = QtGui.QImage(':/remote/network_server.png')
        icon = icon.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.remote_sync_icon.setPixmap(QtGui.QPixmap.fromImage(icon))
        self.remote_sync_icon.show()
