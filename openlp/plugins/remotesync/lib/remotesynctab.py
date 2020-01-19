# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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

import os.path

from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

from openlp.core.common.settings import Settings
from openlp.core.common.registry import Registry
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate
from openlp.core.lib import SettingsTab, build_icon


class RemoteSyncTab(SettingsTab):
    """
    RemoteSyncTab is the RemoteSync settings tab in the settings dialog.
    """
    def __init__(self, parent, title, visible_title, icon_path):
        super(RemoteSyncTab, self).__init__(parent, title, visible_title, icon_path)

    def setupUi(self):
        self.setObjectName('RemoteSyncTab')
        super(RemoteSyncTab, self).setupUi()
        self.server_settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.server_settings_group_box.setObjectName('server_settings_group_box')
        self.server_settings_layout = QtWidgets.QFormLayout(self.server_settings_group_box)
        self.server_settings_layout.setObjectName('server_settings_layout')
        self.address_label = QtWidgets.QLabel(self.server_settings_group_box)
        self.address_label.setObjectName('address_label')
        self.address_edit = QtWidgets.QLineEdit(self.server_settings_group_box)
        self.address_edit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.address_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
                                       self))
        self.address_edit.setObjectName('address_edit')
        self.server_settings_layout.addRow(self.address_label, self.address_edit)
        self.port_label = QtWidgets.QLabel(self.server_settings_group_box)
        self.port_label.setObjectName('port_label')
        self.port_spin_box = QtWidgets.QSpinBox(self.server_settings_group_box)
        self.port_spin_box.setMaximum(32767)
        self.port_spin_box.setObjectName('port_spin_box')
        self.server_settings_layout.addRow(self.port_label, self.port_spin_box)
        self.left_layout.addWidget(self.server_settings_group_box)
        self.auth_token_label = QtWidgets.QLabel(self.server_settings_group_box)
        self.auth_token_label.setObjectName('auth_token_label')
        self.auth_token = QtWidgets.QLineEdit(self.server_settings_group_box)
        self.auth_token.setObjectName('auth_token')
        self.server_settings_layout.addRow(self.auth_token_label, self.auth_token)
        self.left_layout.addWidget(self.server_settings_group_box)

        self.actions_group_box = QtWidgets.QGroupBox(self.left_column)
        self.actions_group_box.setObjectName('actions_group_box')
        self.actions_layout = QtWidgets.QFormLayout(self.actions_group_box)
        self.actions_layout.setObjectName('actions_layout')

        self.send_songs_btn = QtWidgets.QPushButton(self.actions_group_box)
        self.send_songs_btn.setObjectName('send_songs_btn')
        self.send_songs_btn.clicked.connect(self.on_send_songs_clicked)

        self.receive_songs_btn = QtWidgets.QPushButton(self.actions_group_box)
        self.receive_songs_btn.setObjectName('receive_songs_btn')
        self.receive_songs_btn.clicked.connect(self.on_receive_songs_clicked)
        self.actions_layout.addRow(self.send_songs_btn, self.receive_songs_btn)
        self.left_layout.addWidget(self.actions_group_box)

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

    def retranslateUi(self):
        self.server_settings_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Server Settings'))
        self.actions_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Actions'))
        self.remote_statistics_group_box.setTitle(translate('RemotePlugin.RemoteSyncTab', 'Remote Statistics'))
        self.address_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Remote server ip address:'))
        self.port_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Port number:'))
        self.auth_token_label.setText(translate('RemotePlugin.RemoteSyncTab', 'Auth Token:'))
        self.receive_songs_btn.setText(translate('RemotePlugin.RemoteSyncTab', 'Receive Songs'))
        self.send_songs_btn.setText(translate('RemotePlugin.RemoteSyncTab', 'Send Songs'))
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
