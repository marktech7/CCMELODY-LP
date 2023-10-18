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
The :mod:`~openlp.plugins.breeze.forms.selectserviceplandialog` module contains the user interface code for the dialog
"""
from PyQt5 import QtWidgets

from openlp.core.common.i18n import translate


class Ui_SelectPlanDialog(object):
    """
    The actual Qt components that make up the dialog.
    """
    def setup_ui(self, breeze_dialog):
        breeze_dialog.setObjectName('breeze_dialog')
        breeze_dialog.resize(400, 280)
        self.breeze_layout = QtWidgets.QFormLayout(breeze_dialog)
        self.breeze_layout.setContentsMargins(50, 50, 50, 50)
        self.breeze_layout.setSpacing(8)
        self.breeze_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        # Plan Selection GUI Elements
        self.plan_selection_label = QtWidgets.QLabel(breeze_dialog)
        self.plan_selection_combo_box = QtWidgets.QComboBox(breeze_dialog)
        self.breeze_layout.addRow(self.plan_selection_label, self.plan_selection_combo_box)
        # Theme List for Songs and Custom Slides
        self.song_theme_selection_label = QtWidgets.QLabel(breeze_dialog)
        self.song_theme_selection_combo_box = QtWidgets.QComboBox(breeze_dialog)
        self.breeze_layout.addRow(self.song_theme_selection_label, self.song_theme_selection_combo_box)
        self.slide_theme_selection_label = QtWidgets.QLabel(breeze_dialog)
        self.slide_theme_selection_combo_box = QtWidgets.QComboBox(breeze_dialog)
        self.breeze_layout.addRow(self.slide_theme_selection_label, self.slide_theme_selection_combo_box)
        # Import Button
        self.button_layout = QtWidgets.QDialogButtonBox(breeze_dialog)
        self.import_as_new_button = QtWidgets.QPushButton(breeze_dialog)
        self.button_layout.addButton(self.import_as_new_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.update_existing_button = QtWidgets.QPushButton(breeze_dialog)
        self.button_layout.addButton(self.update_existing_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.edit_auth_button = QtWidgets.QPushButton(breeze_dialog)
        self.button_layout.addButton(self.edit_auth_button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.breeze_layout.addRow(self.button_layout)
        self.retranslate_ui(breeze_dialog)

    def retranslate_ui(self, breeze_dialog):
        """
        Translate the GUI.
        """
        breeze_dialog.setWindowTitle(translate('BreezePlugin.BreezeForm',
                                                       'Breeze Service Plan Importer'))
        self.plan_selection_label.setText(translate('BreezePlugin.BreezeForm', 'Select Service Plan'))
        self.import_as_new_button.setText(translate('BreezePlugin.BreezeForm', 'Import New'))
        self.import_as_new_button.setToolTip(translate('BreezePlugin.BreezeForm',
                                                       'Import As New Service'))
        self.update_existing_button.setText(translate('BreezePlugin.BreezeForm', 'Refresh Service'))
        self.update_existing_button.setToolTip(translate('BreezePlugin.BreezeForm',
                                                         'Refresh Existing Service from Breeze. '
                                                         'This will update song lyrics or item orders that '
                                                         'have changed'))
        self.edit_auth_button.setText(translate('BreezePlugin.BreezeForm', 'Edit Authentication'))
        self.edit_auth_button.setToolTip(translate('BreezePlugin.BreezeForm', 'Edit the username '
                                                   'and Password to login to Breeze'))
        self.song_theme_selection_label.setText(translate('BreezePlugin.BreezeForm', 'Song Theme'))
        self.slide_theme_selection_label.setText(translate('BreezePlugin.BreezeForm', 'Slide Theme'))
