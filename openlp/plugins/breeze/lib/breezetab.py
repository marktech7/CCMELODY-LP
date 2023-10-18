# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2023 OpenLP Developers                              #
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
The :mod:`~openlp.plugins.breeze.lib.breezetab` module contains
the settings tab for the Breeze plugin
"""
from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.settingstab import SettingsTab
from openlp.plugins.breeze.lib.breeze_api import BreezeAPI


class BreezeTab(SettingsTab):
    """
    BreezeTab is the alerts settings tab in the settings dialog.
    """
    def setup_ui(self):
        self.setObjectName('BreezeTab')
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        self.tab_layout.setObjectName('tab_layout')
        self.tab_layout.setAlignment(QtCore.Qt.AlignTop)
        self.auth_group_box = QtWidgets.QGroupBox(self)
        self.tab_layout.addWidget(self.auth_group_box)
        self.auth_layout = QtWidgets.QFormLayout(self.auth_group_box)
        self.auth_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # notice
        self.notice_label = QtWidgets.QLabel(self.auth_group_box)
        self.notice_label.setWordWrap(True)
        self.auth_layout.addRow(self.notice_label)
        # instructions
        self.instructions_label = QtWidgets.QLabel(self.auth_group_box)
        self.instructions_label.setWordWrap(True)
        self.auth_layout.addRow(self.instructions_label)
        # subdomain
        self.subdomain_label = QtWidgets.QLabel(self.auth_group_box)
        self.subdomain_line_edit = QtWidgets.QLineEdit(self.auth_group_box)
        self.subdomain_line_edit.setMaxLength(64)
        self.auth_layout.addRow(self.subdomain_label, self.subdomain_line_edit)
        # username
        self.username_label = QtWidgets.QLabel(self.auth_group_box)
        self.username_line_edit = QtWidgets.QLineEdit(self.auth_group_box)
        self.username_line_edit.setMaxLength(64)
        self.auth_layout.addRow(self.username_label, self.username_line_edit)
        # secret
        self.secret_label = QtWidgets.QLabel(self.auth_group_box)
        self.secret_line_edit = QtWidgets.QLineEdit(self.auth_group_box)
        self.secret_line_edit.setMaxLength(64)
        self.auth_layout.addRow(self.secret_label, self.secret_line_edit)
        # Buttons
        self.button_layout = QtWidgets.QDialogButtonBox(self.auth_group_box)
        self.test_credentials_button = QtWidgets.QPushButton(self.auth_group_box)
        self.button_layout.addButton(self.test_credentials_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.auth_layout.addRow(self.button_layout)
        # signals
        self.test_credentials_button.clicked.connect(self.on_test_credentials_button_clicked)

    def retranslate_ui(self):
        self.auth_group_box.setTitle(translate('BreezePlugin.BreezeTab', 'Authentication Settings'))
        self.username_label.setText(translate('BreezePlugin.BreezeTab', 'Username:'))
        self.secret_label.setText(translate('BreezePlugin.BreezeTab', 'Secret:'))
        self.subdomain_label.setText(translate('BreezePlugin.BreezeTab', 'Subdomain:'))

        self.notice_label.setText(
            translate('BreezePlugin.BreezeTab', '<strong>Note:</strong> '
                      'An Internet connection and a Breeze Account are '
                      'required in order to import service plans from Breeze.')
        )
        self.instructions_label.setText(
            translate('BreezePlugin.BreezeTab',
                      """Enter your <b>Breeze</b> credentials below.
</ol>"""))

        self.test_credentials_button.setText(translate('BreezePlugin.BreezeAuthForm',
                                                       'Test Credentials'))

    def resizeEvent(self, event=None):
        """
        Don't call SettingsTab resize handler because we are not using left/right columns.
        """
        QtWidgets.QWidget.resizeEvent(self, event)

    def load(self):
        """
        Load the settings into the UI.
        """
        self.username = self.settings.value('breeze/username')
        self.secret = self.settings.value('breeze/secret')
        self.subdomain = self.settings.value('breeze/subdomain')
        self.username_line_edit.setText(self.username)
        self.secret_line_edit.setText(self.secret)
        self.subdomain_line_edit.setText(self.subdomain)

    def save(self):
        """
        Save the changes on exit of the Settings dialog.
        """
        self.settings.setValue('breeze/username', self.username_line_edit.text())
        self.settings.setValue('breeze/secret', self.secret_line_edit.text())
        self.settings.setValue('breeze/subdomain', self.subdomain_line_edit.text())

    def on_test_credentials_button_clicked(self):
        """
        Tests if the credentials are valid
        """
        username = self.username_line_edit.text()
        secret = self.secret_line_edit.text()
        subdomain = self.subdomain_line_edit.text()
        if len(username) == 0 or len(secret) == 0 or len(subdomain) == 0:
            QtWidgets.QMessageBox.warning(self, "Authentication Failed",
                                          "Please enter values for both Username, Secret, and Subdomain",
                                          QtWidgets.QMessageBox.Ok)
            return
        test_auth = BreezeAPI(username, secret, subdomain)
        organization = test_auth.test()
        if len(organization):
            QtWidgets.QMessageBox.information(self, 'Breeze Authentication Test',
                                              "Authentication successful for organization: {0}".format(organization),
                                              QtWidgets.QMessageBox.Ok)
            self.settings.setValue('breeze/token', test_auth.token())
        else:
            QtWidgets.QMessageBox.warning(self, "Authentication Failed",
                                          "Authentiation Failed",
                                          QtWidgets.QMessageBox.Ok)
