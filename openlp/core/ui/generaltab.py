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
The general tab of the configuration dialog.
"""
import logging
from pathlib import Path

from PyQt5 import QtGui, QtWidgets

from openlp.core.common import get_images_filter
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.widgets.buttons import ColorButton
from openlp.core.widgets.edits import PathEdit


log = logging.getLogger(__name__)


class GeneralTab(SettingsTab):
    """
    GeneralTab is the general settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Initialise the general settings tab
        """
        self.logo_background_color = '#ffffff'
        self.screens = ScreenList()
        self.icon_path = ':/icon/openlp-logo.svg'
        general_translated = translate('OpenLP.GeneralTab', 'General')
        super(GeneralTab, self).__init__(parent, 'Core', general_translated)

    def setup_ui(self):
        """
        Create the user interface for the general settings tab
        """
        self.setObjectName('GeneralTab')
        super(GeneralTab, self).setup_ui()
        self.tab_layout.setStretch(1, 1)
        # CCLI Details
        self.ccli_group_box = QtWidgets.QGroupBox(self.left_column)
        self.ccli_group_box.setObjectName('ccli_group_box')
        self.ccli_layout = QtWidgets.QFormLayout(self.ccli_group_box)
        self.ccli_layout.setObjectName('ccli_layout')
        self.number_label = QtWidgets.QLabel(self.ccli_group_box)
        self.number_label.setObjectName('number_label')
        self.number_edit = QtWidgets.QLineEdit(self.ccli_group_box)
        self.number_edit.setValidator(QtGui.QIntValidator())
        self.number_edit.setObjectName('number_edit')
        self.ccli_layout.addRow(self.number_label, self.number_edit)
        self.username_label = QtWidgets.QLabel(self.ccli_group_box)
        self.username_label.setObjectName('username_label')
        self.username_edit = QtWidgets.QLineEdit(self.ccli_group_box)
        self.username_edit.setObjectName('username_edit')
        self.ccli_layout.addRow(self.username_label, self.username_edit)
        self.password_label = QtWidgets.QLabel(self.ccli_group_box)
        self.password_label.setObjectName('password_label')
        self.password_edit = QtWidgets.QLineEdit(self.ccli_group_box)
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setObjectName('password_edit')
        self.ccli_layout.addRow(self.password_label, self.password_edit)
        self.left_layout.addWidget(self.ccli_group_box)
        self.left_layout.addStretch()
        # Application Startup
        self.startup_group_box = QtWidgets.QGroupBox(self.right_column)
        self.startup_group_box.setObjectName('startup_group_box')
        self.startup_layout = QtWidgets.QVBoxLayout(self.startup_group_box)
        self.startup_layout.setObjectName('startup_layout')
        self.warning_check_box = QtWidgets.QCheckBox(self.startup_group_box)
        self.warning_check_box.setObjectName('warning_check_box')
        self.startup_layout.addWidget(self.warning_check_box)
        self.auto_open_check_box = QtWidgets.QCheckBox(self.startup_group_box)
        self.auto_open_check_box.setObjectName('auto_open_check_box')
        self.startup_layout.addWidget(self.auto_open_check_box)
        self.show_splash_check_box = QtWidgets.QCheckBox(self.startup_group_box)
        self.show_splash_check_box.setObjectName('show_splash_check_box')
        self.startup_layout.addWidget(self.show_splash_check_box)
        self.check_for_updates_check_box = QtWidgets.QCheckBox(self.startup_group_box)
        self.check_for_updates_check_box.setObjectName('check_for_updates_check_box')
        self.startup_layout.addWidget(self.check_for_updates_check_box)
        self.right_layout.addWidget(self.startup_group_box)
        # Logo
        self.logo_group_box = QtWidgets.QGroupBox(self.right_column)
        self.logo_group_box.setObjectName('logo_group_box')
        self.logo_layout = QtWidgets.QFormLayout(self.logo_group_box)
        self.logo_layout.setObjectName('logo_layout')
        self.logo_file_label = QtWidgets.QLabel(self.logo_group_box)
        self.logo_file_label.setObjectName('logo_file_label')
        self.logo_file_path_edit = PathEdit(self.logo_group_box,
                                            default_path=Path(':/graphics/openlp-splash-screen.png'))
        self.logo_layout.addRow(self.logo_file_label, self.logo_file_path_edit)
        self.logo_color_label = QtWidgets.QLabel(self.logo_group_box)
        self.logo_color_label.setObjectName('logo_color_label')
        self.logo_color_button = ColorButton(self.logo_group_box)
        self.logo_color_button.setObjectName('logo_color_button')
        self.logo_layout.addRow(self.logo_color_label, self.logo_color_button)
        self.logo_hide_on_startup_check_box = QtWidgets.QCheckBox(self.logo_group_box)
        self.logo_hide_on_startup_check_box.setObjectName('logo_hide_on_startup_check_box')
        self.logo_layout.addRow(self.logo_hide_on_startup_check_box)
        self.right_layout.addWidget(self.logo_group_box)
        self.logo_color_button.colorChanged.connect(self.on_logo_background_color_changed)
        # Application Settings
        self.settings_group_box = QtWidgets.QGroupBox(self.right_column)
        self.settings_group_box.setObjectName('settings_group_box')
        self.settings_layout = QtWidgets.QFormLayout(self.settings_group_box)
        self.settings_layout.setObjectName('settings_layout')
        self.save_check_service_check_box = QtWidgets.QCheckBox(self.settings_group_box)
        self.save_check_service_check_box.setObjectName('save_check_service_check_box')
        self.settings_layout.addRow(self.save_check_service_check_box)
        self.auto_unblank_check_box = QtWidgets.QCheckBox(self.settings_group_box)
        self.auto_unblank_check_box.setObjectName('auto_unblank_check_box')
        self.settings_layout.addRow(self.auto_unblank_check_box)
        self.click_live_slide_to_unblank_check_box = QtWidgets.QCheckBox(self.settings_group_box)
        self.click_live_slide_to_unblank_check_box.setObjectName('click_live_slide_to_unblank')
        self.settings_layout.addRow(self.click_live_slide_to_unblank_check_box)
        self.auto_preview_check_box = QtWidgets.QCheckBox(self.settings_group_box)
        self.auto_preview_check_box.setObjectName('auto_preview_check_box')
        self.settings_layout.addRow(self.auto_preview_check_box)
        # Moved here from image tab
        self.timeout_label = QtWidgets.QLabel(self.settings_group_box)
        self.timeout_label.setObjectName('timeout_label')
        self.timeout_spin_box = QtWidgets.QSpinBox(self.settings_group_box)
        self.timeout_spin_box.setObjectName('timeout_spin_box')
        self.timeout_spin_box.setRange(1, 180)
        self.settings_layout.addRow(self.timeout_label, self.timeout_spin_box)
        self.right_layout.addWidget(self.settings_group_box)
        self.right_layout.addStretch()
        # Remove for now
        self.username_label.setVisible(False)
        self.username_edit.setVisible(False)
        self.password_label.setVisible(False)
        self.password_edit.setVisible(False)

    def retranslate_ui(self):
        """
        Translate the general settings tab to the currently selected language
        """
        self.tab_title_visible = translate('OpenLP.GeneralTab', 'General')
        self.startup_group_box.setTitle(translate('OpenLP.GeneralTab', 'Application Startup'))
        self.warning_check_box.setText(translate('OpenLP.GeneralTab', 'Show blank screen warning'))
        self.auto_open_check_box.setText(translate('OpenLP.GeneralTab', 'Automatically open the previous service file'))
        self.show_splash_check_box.setText(translate('OpenLP.GeneralTab', 'Show the splash screen'))
        self.logo_group_box.setTitle(translate('OpenLP.GeneralTab', 'Logo'))
        self.logo_color_label.setText(UiStrings().BackgroundColorColon)
        self.logo_file_label.setText(translate('OpenLP.GeneralTab', 'Logo file:'))
        self.logo_hide_on_startup_check_box.setText(translate('OpenLP.GeneralTab', 'Don\'t show logo on startup'))
        self.check_for_updates_check_box.setText(translate('OpenLP.GeneralTab', 'Check for updates to OpenLP'))
        self.settings_group_box.setTitle(translate('OpenLP.GeneralTab', 'Application Settings'))
        self.save_check_service_check_box.setText(translate('OpenLP.GeneralTab',
                                                  'Prompt to save before starting a new service'))
        self.click_live_slide_to_unblank_check_box.setText(translate('OpenLP.GeneralTab',
                                                           'Unblank display when changing slide in Live'))
        self.auto_unblank_check_box.setText(translate('OpenLP.GeneralTab', 'Unblank display when sending '
                                                                           'items to Live'))
        self.auto_preview_check_box.setText(translate('OpenLP.GeneralTab',
                                                      'Automatically preview the next item in service'))
        self.timeout_label.setText(translate('OpenLP.GeneralTab', 'Timed slide interval:'))
        self.timeout_spin_box.setSuffix(translate('OpenLP.GeneralTab', ' sec'))
        self.ccli_group_box.setTitle(translate('OpenLP.GeneralTab', 'CCLI Details'))
        self.number_label.setText(UiStrings().CCLINumberLabel)
        self.username_label.setText(translate('OpenLP.GeneralTab', 'SongSelect username:'))
        self.password_label.setText(translate('OpenLP.GeneralTab', 'SongSelect password:'))
        self.logo_file_path_edit.dialog_caption = translate('OpenLP.AdvancedTab', 'Select Logo File')
        self.logo_file_path_edit.dialog_caption = translate('OpenLP.AdvancedTab', 'Select Logo File')
        self.logo_file_path_edit.filters = '{text};;{names} (*)'.format(
            text=get_images_filter(), names=UiStrings().AllFiles)

    def load(self):
        """
        Load the settings to populate the form
        """
        self.settings.beginGroup(self.settings_section)
        self.number_edit.setText(self.settings.value('ccli number'))
        self.username_edit.setText(self.settings.value('songselect username'))
        self.password_edit.setText(self.settings.value('songselect password'))
        self.save_check_service_check_box.setChecked(self.settings.value('save prompt'))
        self.auto_unblank_check_box.setChecked(self.settings.value('auto unblank'))
        self.click_live_slide_to_unblank_check_box.setChecked(self.settings.value('click live slide to unblank'))
        self.warning_check_box.setChecked(self.settings.value('blank warning'))
        self.auto_open_check_box.setChecked(self.settings.value('auto open'))
        self.show_splash_check_box.setChecked(self.settings.value('show splash'))
        self.logo_background_color = self.settings.value('logo background color')
        self.logo_file_path_edit.path = self.settings.value('logo file')
        self.logo_hide_on_startup_check_box.setChecked(self.settings.value('logo hide on startup'))
        self.logo_color_button.color = self.logo_background_color
        self.check_for_updates_check_box.setChecked(self.settings.value('update check'))
        self.auto_preview_check_box.setChecked(self.settings.value('auto preview'))
        self.timeout_spin_box.setValue(self.settings.value('loop delay'))
        settings.endGroup()

    def save(self):
        """
        Save the settings from the form
        """
        self.settings.beginGroup(self.settings_section)
        self.settings.setValue('blank warning', self.warning_check_box.isChecked())
        self.settings.setValue('auto open', self.auto_open_check_box.isChecked())
        self.settings.setValue('show splash', self.show_splash_check_box.isChecked())
        self.settings.setValue('logo background color', self.logo_background_color)
        self.settings.setValue('logo file', self.logo_file_path_edit.path)
        self.settings.setValue('logo hide on startup', self.logo_hide_on_startup_check_box.isChecked())
        self.settings.setValue('update check', self.check_for_updates_check_box.isChecked())
        self.settings.setValue('save prompt', self.save_check_service_check_box.isChecked())
        self.settings.setValue('auto unblank', self.auto_unblank_check_box.isChecked())
        self.settings.setValue('click live slide to unblank', self.click_live_slide_to_unblank_check_box.isChecked())
        self.settings.setValue('auto preview', self.auto_preview_check_box.isChecked())
        self.settings.setValue('loop delay', self.timeout_spin_box.value())
        self.settings.setValue('ccli number', self.number_edit.displayText())
        self.settings.setValue('songselect username', self.username_edit.displayText())
        self.settings.setValue('songselect password', self.password_edit.displayText())
        self.settings.endGroup()
        self.post_set_up()

    def post_set_up(self):
        """
        Apply settings after the tab has loaded
        """
        self.settings_form.register_post_process('slidecontroller_live_spin_delay')

    def on_logo_background_color_changed(self, color):
        """
        Select the background color for logo.
        """
        self.logo_background_color = color
