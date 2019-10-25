# -*- coding: utf-8 -*-

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
The Create/Edit theme wizard
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import is_macosx
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.theme import BackgroundGradientType, BackgroundType, HorizontalType, TransitionType, TransitionSpeed
from openlp.core.lib.ui import add_welcome_page, create_valign_selection_widgets
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.buttons import ColorButton
from openlp.core.widgets.edits import PathEdit
from openlp.core.widgets.layouts import AspectRatioLayout
from openlp.core.display.render import ThemePreviewRenderer


class Ui_ThemeWizard(object):
    """
    The Create/Edit theme wizard
    """
    def setup_ui(self, theme_wizard):
        """
        Set up the UI
        """
        theme_wizard.setObjectName('OpenLP.ThemeWizard')
        theme_wizard.setWindowIcon(UiIcons().main_icon)
        theme_wizard.setModal(True)
        theme_wizard.setOptions(QtWidgets.QWizard.IndependentPages |
                                QtWidgets.QWizard.NoBackButtonOnStartPage | QtWidgets.QWizard.HaveCustomButton1)
        theme_wizard.setFixedWidth(640)
        if is_macosx():
            theme_wizard.setPixmap(QtWidgets.QWizard.BackgroundPixmap, QtGui.QPixmap(':/wizards/openlp-osx-wizard.png'))
        else:
            theme_wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.spacer = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        # Welcome Page
        add_welcome_page(theme_wizard, ':/wizards/wizard_createtheme.bmp')
        # Background Page
        self.background_page = QtWidgets.QWizardPage()
        self.background_page.setObjectName('background_page')
        self.background_layout = QtWidgets.QVBoxLayout(self.background_page)
        self.background_layout.setObjectName('background_layout')
        self.background_type_layout = QtWidgets.QFormLayout()
        self.background_type_layout.setObjectName('background_type_layout')
        self.background_label = QtWidgets.QLabel(self.background_page)
        self.background_label.setObjectName('background_label')
        self.background_combo_box = QtWidgets.QComboBox(self.background_page)
        self.background_combo_box.addItems(['', '', '', '', '', ''])
        self.background_combo_box.setObjectName('background_combo_box')
        self.background_type_layout.addRow(self.background_label, self.background_combo_box)
        self.background_type_layout.setItem(1, QtWidgets.QFormLayout.LabelRole, self.spacer)
        self.background_layout.addLayout(self.background_type_layout)
        self.background_stack = QtWidgets.QStackedLayout()
        self.background_stack.setObjectName('background_stack')
        self.color_widget = QtWidgets.QWidget(self.background_page)
        self.color_widget.setObjectName('color_widget')
        self.color_layout = QtWidgets.QFormLayout(self.color_widget)
        self.color_layout.setContentsMargins(0, 0, 0, 0)
        self.color_layout.setObjectName('color_layout')
        self.color_label = QtWidgets.QLabel(self.color_widget)
        self.color_label.setObjectName('color_label')
        self.color_button = ColorButton(self.color_widget)
        self.color_button.setObjectName('color_button')
        self.color_layout.addRow(self.color_label, self.color_button)
        self.color_layout.setItem(1, QtWidgets.QFormLayout.LabelRole, self.spacer)
        self.background_stack.addWidget(self.color_widget)
        self.gradient_widget = QtWidgets.QWidget(self.background_page)
        self.gradient_widget.setObjectName('Gradient_widget')
        self.gradient_layout = QtWidgets.QFormLayout(self.gradient_widget)
        self.gradient_layout.setContentsMargins(0, 0, 0, 0)
        self.gradient_layout.setObjectName('gradient_layout')
        self.gradient_start_label = QtWidgets.QLabel(self.gradient_widget)
        self.gradient_start_label.setObjectName('gradient_start_label')
        self.gradient_start_button = ColorButton(self.gradient_widget)
        self.gradient_start_button.setObjectName('gradient_start_button')
        self.gradient_layout.addRow(self.gradient_start_label, self.gradient_start_button)
        self.gradient_end_label = QtWidgets.QLabel(self.gradient_widget)
        self.gradient_end_label.setObjectName('gradient_end_label')
        self.gradient_end_button = ColorButton(self.gradient_widget)
        self.gradient_end_button.setObjectName('gradient_end_button')
        self.gradient_layout.addRow(self.gradient_end_label, self.gradient_end_button)
        self.gradient_type_label = QtWidgets.QLabel(self.gradient_widget)
        self.gradient_type_label.setObjectName('Gradient_type_label')
        self.gradient_combo_box = QtWidgets.QComboBox(self.gradient_widget)
        self.gradient_combo_box.setObjectName('gradient_combo_box')
        self.gradient_combo_box.addItems(['', '', '', '', ''])
        self.gradient_layout.addRow(self.gradient_type_label, self.gradient_combo_box)
        self.gradient_layout.setItem(3, QtWidgets.QFormLayout.LabelRole, self.spacer)
        self.background_stack.addWidget(self.gradient_widget)
        self.image_widget = QtWidgets.QWidget(self.background_page)
        self.image_widget.setObjectName('image_widget')
        self.image_layout = QtWidgets.QFormLayout(self.image_widget)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_layout.setObjectName('image_layout')
        self.image_color_label = QtWidgets.QLabel(self.color_widget)
        self.image_color_label.setObjectName('image_color_label')
        self.image_color_button = ColorButton(self.color_widget)
        self.image_color_button.setObjectName('image_color_button')
        self.image_layout.addRow(self.image_color_label, self.image_color_button)
        self.image_label = QtWidgets.QLabel(self.image_widget)
        self.image_label.setObjectName('image_label')
        self.image_path_edit = PathEdit(self.image_widget,
                                        dialog_caption=translate('OpenLP.ThemeWizard', 'Select Image'),
                                        show_revert=False)
        self.image_layout.addRow(self.image_label, self.image_path_edit)
        self.image_layout.setItem(2, QtWidgets.QFormLayout.LabelRole, self.spacer)
        self.background_stack.addWidget(self.image_widget)
        self.transparent_widget = QtWidgets.QWidget(self.background_page)
        self.transparent_widget.setObjectName('TransparentWidget')
        self.transparent_layout = QtWidgets.QFormLayout(self.transparent_widget)
        self.transparent_layout.setContentsMargins(0, 0, 0, 0)
        self.transparent_layout.setObjectName('Transparent_layout')
        self.background_stack.addWidget(self.transparent_widget)
        self.background_layout.addLayout(self.background_stack)
        self.video_widget = QtWidgets.QWidget(self.background_page)
        self.video_widget.setObjectName('video_widget')
        self.video_layout = QtWidgets.QFormLayout(self.video_widget)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_layout.setObjectName('video_layout')
        self.video_color_label = QtWidgets.QLabel(self.color_widget)
        self.video_color_label.setObjectName('video_color_label')
        self.video_color_button = ColorButton(self.color_widget)
        self.video_color_button.setObjectName('video_color_button')
        self.video_layout.addRow(self.video_color_label, self.video_color_button)
        self.video_label = QtWidgets.QLabel(self.video_widget)
        self.video_label.setObjectName('video_label')
        self.video_path_edit = PathEdit(self.video_widget,
                                        dialog_caption=translate('OpenLP.ThemeWizard', 'Select Video'),
                                        show_revert=False)
        self.video_layout.addRow(self.video_label, self.video_path_edit)
        self.video_layout.setItem(2, QtWidgets.QFormLayout.LabelRole, self.spacer)
        self.background_stack.addWidget(self.video_widget)
        theme_wizard.addPage(self.background_page)
        # Main Area Page
        self.main_area_page = QtWidgets.QWizardPage()
        self.main_area_page.setObjectName('main_area_page')
        self.main_area_layout = QtWidgets.QFormLayout(self.main_area_page)
        self.main_area_layout.setObjectName('main_area_layout')
        self.main_font_label = QtWidgets.QLabel(self.main_area_page)
        self.main_font_label.setObjectName('main_font_label')
        self.main_font_combo_box = QtWidgets.QFontComboBox(self.main_area_page)
        self.main_font_combo_box.setObjectName('main_font_combo_box')
        self.main_area_layout.addRow(self.main_font_label, self.main_font_combo_box)
        self.main_color_label = QtWidgets.QLabel(self.main_area_page)
        self.main_color_label.setObjectName('main_color_label')
        self.main_properties_layout = QtWidgets.QHBoxLayout()
        self.main_properties_layout.setObjectName('main_properties_layout')
        self.main_color_button = ColorButton(self.main_area_page)
        self.main_color_button.setObjectName('main_color_button')
        self.main_properties_layout.addWidget(self.main_color_button)
        self.main_properties_layout.addSpacing(20)
        self.main_bold_check_box = QtWidgets.QCheckBox(self.main_area_page)
        self.main_bold_check_box.setObjectName('main_bold_check_box')
        self.main_properties_layout.addWidget(self.main_bold_check_box)
        self.main_properties_layout.addSpacing(20)
        self.main_italics_check_box = QtWidgets.QCheckBox(self.main_area_page)
        self.main_italics_check_box.setObjectName('MainItalicsCheckBox')
        self.main_properties_layout.addWidget(self.main_italics_check_box)
        self.main_area_layout.addRow(self.main_color_label, self.main_properties_layout)
        self.main_size_label = QtWidgets.QLabel(self.main_area_page)
        self.main_size_label.setObjectName('main_size_label')
        self.main_size_layout = QtWidgets.QHBoxLayout()
        self.main_size_layout.setObjectName('main_size_layout')
        self.main_size_spin_box = QtWidgets.QSpinBox(self.main_area_page)
        self.main_size_spin_box.setMaximum(999)
        self.main_size_spin_box.setValue(16)
        self.main_size_spin_box.setObjectName('main_size_spin_box')
        self.main_size_layout.addWidget(self.main_size_spin_box)
        self.main_line_count_label = QtWidgets.QLabel(self.main_area_page)
        self.main_line_count_label.setObjectName('main_line_count_label')
        self.main_size_layout.addWidget(self.main_line_count_label)
        self.main_area_layout.addRow(self.main_size_label, self.main_size_layout)
        self.line_spacing_label = QtWidgets.QLabel(self.main_area_page)
        self.line_spacing_label.setObjectName('line_spacing_label')
        self.line_spacing_spin_box = QtWidgets.QSpinBox(self.main_area_page)
        self.line_spacing_spin_box.setMinimum(-250)
        self.line_spacing_spin_box.setMaximum(250)
        self.line_spacing_spin_box.setObjectName('line_spacing_spin_box')
        self.main_area_layout.addRow(self.line_spacing_label, self.line_spacing_spin_box)
        self.outline_check_box = QtWidgets.QCheckBox(self.main_area_page)
        self.outline_check_box.setObjectName('outline_check_box')
        self.outline_layout = QtWidgets.QHBoxLayout()
        self.outline_layout.setObjectName('outline_layout')
        self.outline_color_button = ColorButton(self.main_area_page)
        self.outline_color_button.setEnabled(False)
        self.outline_color_button.setObjectName('Outline_color_button')
        self.outline_layout.addWidget(self.outline_color_button)
        self.outline_layout.addSpacing(20)
        self.outline_size_label = QtWidgets.QLabel(self.main_area_page)
        self.outline_size_label.setObjectName('outline_size_label')
        self.outline_layout.addWidget(self.outline_size_label)
        self.outline_size_spin_box = QtWidgets.QSpinBox(self.main_area_page)
        self.outline_size_spin_box.setEnabled(False)
        self.outline_size_spin_box.setObjectName('outline_size_spin_box')
        self.outline_layout.addWidget(self.outline_size_spin_box)
        self.main_area_layout.addRow(self.outline_check_box, self.outline_layout)
        self.shadow_check_box = QtWidgets.QCheckBox(self.main_area_page)
        self.shadow_check_box.setObjectName('shadow_check_box')
        self.shadow_layout = QtWidgets.QHBoxLayout()
        self.shadow_layout.setObjectName('shadow_layout')
        self.shadow_color_button = ColorButton(self.main_area_page)
        self.shadow_color_button.setEnabled(False)
        self.shadow_color_button.setObjectName('shadow_color_button')
        self.shadow_layout.addWidget(self.shadow_color_button)
        self.shadow_layout.addSpacing(20)
        self.shadow_size_label = QtWidgets.QLabel(self.main_area_page)
        self.shadow_size_label.setObjectName('shadow_size_label')
        self.shadow_layout.addWidget(self.shadow_size_label)
        self.shadow_size_spin_box = QtWidgets.QSpinBox(self.main_area_page)
        self.shadow_size_spin_box.setEnabled(False)
        self.shadow_size_spin_box.setObjectName('shadow_size_spin_box')
        self.shadow_layout.addWidget(self.shadow_size_spin_box)
        self.main_area_layout.addRow(self.shadow_check_box, self.shadow_layout)
        theme_wizard.addPage(self.main_area_page)
        # Footer Area Page
        self.footer_area_page = QtWidgets.QWizardPage()
        self.footer_area_page.setObjectName('footer_area_page')
        self.footer_area_layout = QtWidgets.QFormLayout(self.footer_area_page)
        self.footer_area_layout.setObjectName('footer_area_layout')
        self.footer_font_label = QtWidgets.QLabel(self.footer_area_page)
        self.footer_font_label.setObjectName('FooterFontLabel')
        self.footer_font_combo_box = QtWidgets.QFontComboBox(self.footer_area_page)
        self.footer_font_combo_box.setObjectName('footer_font_combo_box')
        self.footer_area_layout.addRow(self.footer_font_label, self.footer_font_combo_box)
        self.footer_color_label = QtWidgets.QLabel(self.footer_area_page)
        self.footer_color_label.setObjectName('footer_color_label')
        self.footer_color_button = ColorButton(self.footer_area_page)
        self.footer_color_button.setObjectName('footer_color_button')
        self.footer_area_layout.addRow(self.footer_color_label, self.footer_color_button)
        self.footer_size_label = QtWidgets.QLabel(self.footer_area_page)
        self.footer_size_label.setObjectName('footer_size_label')
        self.footer_size_spin_box = QtWidgets.QSpinBox(self.footer_area_page)
        self.footer_size_spin_box.setMaximum(999)
        self.footer_size_spin_box.setValue(10)
        self.footer_size_spin_box.setObjectName('FooterSizeSpinBox')
        self.footer_area_layout.addRow(self.footer_size_label, self.footer_size_spin_box)
        self.footer_area_layout.setItem(3, QtWidgets.QFormLayout.LabelRole, self.spacer)
        theme_wizard.addPage(self.footer_area_page)
        # Alignment Page
        self.alignment_page = QtWidgets.QWizardPage()
        self.alignment_page.setObjectName('alignment_page')
        self.alignment_layout = QtWidgets.QFormLayout(self.alignment_page)
        self.alignment_layout.setObjectName('alignment_layout')
        self.horizontal_label = QtWidgets.QLabel(self.alignment_page)
        self.horizontal_label.setObjectName('horizontal_label')
        self.horizontal_combo_box = QtWidgets.QComboBox(self.alignment_page)
        self.horizontal_combo_box.addItems(['', '', '', ''])
        self.horizontal_combo_box.setObjectName('horizontal_combo_box')
        self.alignment_layout.addRow(self.horizontal_label, self.horizontal_combo_box)
        self.vertical_label, self.vertical_combo_box = create_valign_selection_widgets(self.alignment_page)
        self.vertical_label.setObjectName('vertical_label')
        self.vertical_combo_box.setObjectName('vertical_combo_box')
        self.alignment_layout.addRow(self.vertical_label, self.vertical_combo_box)
        self.transitions_check_box = QtWidgets.QCheckBox(self.alignment_page)
        self.transitions_check_box.setObjectName('transitions_check_box')
        self.transition_layout = QtWidgets.QHBoxLayout()
        self.transition_layout.setObjectName("transition_layout")
        self.transition_combo_box = QtWidgets.QComboBox(self.alignment_page)
        self.transition_combo_box.setObjectName("transition_combo_box")
        self.transition_combo_box.addItems(['', '', '', '', ''])
        self.transition_layout.addWidget(self.transition_combo_box)
        self.transition_speed_label = QtWidgets.QLabel(self.alignment_page)
        self.transition_speed_label.setObjectName("transition_speed_label")
        self.transition_layout.addWidget(self.transition_speed_label)
        self.transition_speed_combo_box = QtWidgets.QComboBox(self.alignment_page)
        self.transition_speed_combo_box.setObjectName("transition_speed_combo_box")
        self.transition_speed_combo_box.addItems(['', '', ''])
        self.transition_layout.addWidget(self.transition_speed_combo_box)
        self.alignment_layout.addRow(self.transitions_check_box, self.transition_layout)
        theme_wizard.addPage(self.alignment_page)
        # Area Position Page
        self.area_position_page = QtWidgets.QWizardPage()
        self.area_position_page.setObjectName('area_position_page')
        self.area_position_layout = QtWidgets.QHBoxLayout(self.area_position_page)
        self.area_position_layout.setObjectName('area_position_layout')
        self.main_position_group_box = QtWidgets.QGroupBox(self.area_position_page)
        self.main_position_group_box.setObjectName('main_position_group_box')
        self.main_position_layout = QtWidgets.QFormLayout(self.main_position_group_box)
        self.main_position_layout.setObjectName('main_position_layout')
        self.main_position_check_box = QtWidgets.QCheckBox(self.main_position_group_box)
        self.main_position_check_box.setObjectName('main_position_check_box')
        self.main_position_layout.addRow(self.main_position_check_box)
        self.main_x_label = QtWidgets.QLabel(self.main_position_group_box)
        self.main_x_label.setObjectName('main_x_label')
        self.main_x_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_x_spin_box.setMaximum(9999)
        self.main_x_spin_box.setObjectName('main_x_spin_box')
        self.main_position_layout.addRow(self.main_x_label, self.main_x_spin_box)
        self.main_y_label = QtWidgets.QLabel(self.main_position_group_box)
        self.main_y_label.setObjectName('main_y_label')
        self.main_y_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_y_spin_box.setMaximum(9999)
        self.main_y_spin_box.setObjectName('main_y_spin_box')
        self.main_position_layout.addRow(self.main_y_label, self.main_y_spin_box)
        self.main_width_label = QtWidgets.QLabel(self.main_position_group_box)
        self.main_width_label.setObjectName('main_width_label')
        self.main_width_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_width_spin_box.setMaximum(9999)
        self.main_width_spin_box.setObjectName('main_width_spin_box')
        self.main_position_layout.addRow(self.main_width_label, self.main_width_spin_box)
        self.main_height_label = QtWidgets.QLabel(self.main_position_group_box)
        self.main_height_label.setObjectName('main_height_label')
        self.main_height_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_height_spin_box.setMaximum(9999)
        self.main_height_spin_box.setObjectName('main_height_spin_box')
        self.main_position_layout.addRow(self.main_height_label, self.main_height_spin_box)
        self.area_position_layout.addWidget(self.main_position_group_box)
        self.footer_position_group_box = QtWidgets.QGroupBox(self.area_position_page)
        self.footer_position_group_box.setObjectName('footer_position_group_box')
        self.footer_position_layout = QtWidgets.QFormLayout(self.footer_position_group_box)
        self.footer_position_layout.setObjectName('footer_position_layout')
        self.footer_position_check_box = QtWidgets.QCheckBox(self.footer_position_group_box)
        self.footer_position_check_box.setObjectName('footer_position_check_box')
        self.footer_position_layout.addRow(self.footer_position_check_box)
        self.footer_x_label = QtWidgets.QLabel(self.footer_position_group_box)
        self.footer_x_label.setObjectName('footer_x_label')
        self.footer_x_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_x_spin_box.setMaximum(9999)
        self.footer_x_spin_box.setObjectName('footer_x_spin_box')
        self.footer_position_layout.addRow(self.footer_x_label, self.footer_x_spin_box)
        self.footer_y_label = QtWidgets.QLabel(self.footer_position_group_box)
        self.footer_y_label.setObjectName('footer_y_label')
        self.footer_y_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_y_spin_box.setMaximum(9999)
        self.footer_y_spin_box.setObjectName('footer_y_spin_box')
        self.footer_position_layout.addRow(self.footer_y_label, self.footer_y_spin_box)
        self.footer_width_label = QtWidgets.QLabel(self.footer_position_group_box)
        self.footer_width_label.setObjectName('footer_width_label')
        self.footer_width_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_width_spin_box.setMaximum(9999)
        self.footer_width_spin_box.setObjectName('footer_width_spin_box')
        self.footer_position_layout.addRow(self.footer_width_label, self.footer_width_spin_box)
        self.footer_height_label = QtWidgets.QLabel(self.footer_position_group_box)
        self.footer_height_label.setObjectName('footer_height_label')
        self.footer_height_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_height_spin_box.setMaximum(9999)
        self.footer_height_spin_box.setObjectName('footer_height_spin_box')
        self.footer_position_layout.addRow(self.footer_height_label, self.footer_height_spin_box)
        self.area_position_layout.addWidget(self.footer_position_group_box)
        theme_wizard.addPage(self.area_position_page)
        # Preview Page
        self.preview_page = QtWidgets.QWizardPage()
        self.preview_page.setObjectName('preview_page')
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_page)
        self.preview_layout.setObjectName('preview_layout')
        self.theme_name_layout = QtWidgets.QFormLayout()
        self.theme_name_layout.setObjectName('theme_name_layout')
        self.theme_name_label = QtWidgets.QLabel(self.preview_page)
        self.theme_name_label.setObjectName('theme_name_label')
        self.theme_name_edit = QtWidgets.QLineEdit(self.preview_page)
        self.theme_name_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'[^/\\?*|<>\[\]":<>+%]+'), self))
        self.theme_name_edit.setObjectName('ThemeNameEdit')
        self.theme_name_layout.addRow(self.theme_name_label, self.theme_name_edit)
        self.preview_layout.addLayout(self.theme_name_layout)
        self.preview_area = QtWidgets.QWidget(self.preview_page)
        self.preview_area.setObjectName('PreviewArea')
        self.preview_area_layout = AspectRatioLayout(self.preview_area, 0.75)  # Dummy ratio, will be update
        self.preview_area_layout.margin = 8
        self.preview_area_layout.setSpacing(0)
        self.preview_area_layout.setObjectName('preview_web_layout')
        self.preview_box = ThemePreviewRenderer(self)
        self.preview_box.setObjectName('preview_box')
        self.preview_area_layout.addWidget(self.preview_box)
        self.preview_layout.addWidget(self.preview_area)
        theme_wizard.addPage(self.preview_page)
        self.retranslate_ui(theme_wizard)
        self.background_combo_box.currentIndexChanged.connect(self.background_stack.setCurrentIndex)
        self.outline_check_box.toggled.connect(self.outline_color_button.setEnabled)
        self.outline_check_box.toggled.connect(self.outline_size_spin_box.setEnabled)
        self.shadow_check_box.toggled.connect(self.shadow_color_button.setEnabled)
        self.shadow_check_box.toggled.connect(self.shadow_size_spin_box.setEnabled)
        self.main_position_check_box.toggled.connect(self.main_x_spin_box.setDisabled)
        self.main_position_check_box.toggled.connect(self.main_y_spin_box.setDisabled)
        self.main_position_check_box.toggled.connect(self.main_width_spin_box.setDisabled)
        self.main_position_check_box.toggled.connect(self.main_height_spin_box.setDisabled)
        self.footer_position_check_box.toggled.connect(self.footer_x_spin_box.setDisabled)
        self.footer_position_check_box.toggled.connect(self.footer_y_spin_box.setDisabled)
        self.footer_position_check_box.toggled.connect(self.footer_width_spin_box.setDisabled)
        self.footer_position_check_box.toggled.connect(self.footer_height_spin_box.setDisabled)

    def retranslate_ui(self, theme_wizard):
        """
        Translate the UI on the fly
        """
        theme_wizard.setWindowTitle(translate('OpenLP.ThemeWizard', 'Theme Wizard'))
        text = translate('OpenLP.ThemeWizard', 'Welcome to the Theme Wizard')
        self.title_label.setText('<span style="font-size:14pt; font-weight:600;">{text}</span>'.format(text=text))
        self.information_label.setText(
            translate('OpenLP.ThemeWizard', 'This wizard will help you to create and edit your themes. Click the next '
                      'button below to start the process by setting up your background.'))
        self.background_page.setTitle(translate('OpenLP.ThemeWizard', 'Set Up Background'))
        self.background_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Set up your theme\'s background '
                                         'according to the parameters below.'))
        self.background_label.setText(translate('OpenLP.ThemeWizard', 'Background type:'))
        self.background_combo_box.setItemText(BackgroundType.Solid, translate('OpenLP.ThemeWizard', 'Solid color'))
        self.background_combo_box.setItemText(BackgroundType.Gradient, translate('OpenLP.ThemeWizard', 'Gradient'))
        self.background_combo_box.setItemText(BackgroundType.Image, UiStrings().Image)
        self.background_combo_box.setItemText(BackgroundType.Video, UiStrings().Video)
        self.background_combo_box.setItemText(BackgroundType.Transparent,
                                              translate('OpenLP.ThemeWizard', 'Transparent'))
        self.background_combo_box.setItemText(BackgroundType.Stream,
                                              translate('OpenLP.ThemeWizard', 'Live Stream'))
        self.color_label.setText(translate('OpenLP.ThemeWizard', 'color:'))
        self.gradient_start_label.setText(translate('OpenLP.ThemeWizard', 'Starting color:'))
        self.gradient_end_label.setText(translate('OpenLP.ThemeWizard', 'Ending color:'))
        self.gradient_type_label.setText(translate('OpenLP.ThemeWizard', 'Gradient:'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Horizontal,
                                            translate('OpenLP.ThemeWizard', 'Horizontal'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Vertical,
                                            translate('OpenLP.ThemeWizard', 'Vertical'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Circular,
                                            translate('OpenLP.ThemeWizard', 'Circular'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.LeftTop,
                                            translate('OpenLP.ThemeWizard', 'Top Left - Bottom Right'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.LeftBottom,
                                            translate('OpenLP.ThemeWizard', 'Bottom Left - Top Right'))
        self.image_color_label.setText(translate('OpenLP.ThemeWizard', 'Background color:'))
        self.image_label.setText('{text}:'.format(text=UiStrings().Image))
        self.video_color_label.setText(translate('OpenLP.ThemeWizard', 'Background color:'))
        self.video_label.setText('{text}:'.format(text=UiStrings().Video))
        self.main_area_page.setTitle(translate('OpenLP.ThemeWizard', 'Main Area Font Details'))
        self.main_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                  'characteristics for the Display text'))
        self.main_font_label.setText(translate('OpenLP.ThemeWizard', 'Font:'))
        self.main_color_label.setText(translate('OpenLP.ThemeWizard', 'color:'))
        self.main_size_label.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.main_size_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.line_spacing_label.setText(translate('OpenLP.ThemeWizard', 'Line Spacing:'))
        self.line_spacing_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.outline_check_box.setText(translate('OpenLP.ThemeWizard', '&Outline:'))
        self.outline_size_label.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.outline_size_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.shadow_check_box.setText(translate('OpenLP.ThemeWizard', '&Shadow:'))
        self.shadow_size_label.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.shadow_size_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.main_bold_check_box.setText(translate('OpenLP.ThemeWizard', 'Bold'))
        self.main_italics_check_box.setText(translate('OpenLP.ThemeWizard', 'Italic'))
        self.footer_area_page.setTitle(translate('OpenLP.ThemeWizard', 'Footer Area Font Details'))
        self.footer_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                    'characteristics for the Footer text'))
        self.footer_font_label.setText(translate('OpenLP.ThemeWizard', 'Font:'))
        self.footer_color_label.setText(translate('OpenLP.ThemeWizard', 'color:'))
        self.footer_size_label.setText(translate('OpenLP.ThemeWizard', 'Size:'))
        self.footer_size_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.alignment_page.setTitle(translate('OpenLP.ThemeWizard', 'Text Formatting Details'))
        self.alignment_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows additional display '
                                                  'formatting information to be defined'))
        self.horizontal_label.setText(translate('OpenLP.ThemeWizard', 'Horizontal Align:'))
        self.horizontal_combo_box.setItemText(HorizontalType.Left, translate('OpenLP.ThemeWizard', 'Left'))
        self.horizontal_combo_box.setItemText(HorizontalType.Right, translate('OpenLP.ThemeWizard', 'Right'))
        self.horizontal_combo_box.setItemText(HorizontalType.Center, translate('OpenLP.ThemeWizard', 'Center'))
        self.horizontal_combo_box.setItemText(HorizontalType.Justify, translate('OpenLP.ThemeWizard', 'Justify'))
        self.transitions_check_box.setText(translate('OpenLP.ThemeWizard', 'Transitions:'))
        self.transition_combo_box.setItemText(TransitionType.Fade, translate('OpenLP.ThemeWizard', 'Fade'))
        self.transition_combo_box.setItemText(TransitionType.Slide, translate('OpenLP.ThemeWizard', 'Slide'))
        self.transition_combo_box.setItemText(TransitionType.Concave, translate('OpenLP.ThemeWizard', 'Concave'))
        self.transition_combo_box.setItemText(TransitionType.Convex, translate('OpenLP.ThemeWizard', 'Convex'))
        self.transition_combo_box.setItemText(TransitionType.Zoom, translate('OpenLP.ThemeWizard', 'Zoom'))
        self.transition_speed_label.setText(translate('OpenLP.ThemeWizard', 'Speed:'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Default, translate('OpenLP.ThemeWizard', 'Normal'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Fast, translate('OpenLP.ThemeWizard', 'Fast'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Slow, translate('OpenLP.ThemeWizard', 'Slow'))
        self.area_position_page.setTitle(translate('OpenLP.ThemeWizard', 'Output Area Locations'))
        self.area_position_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows you to change and move the'
                                                      ' Main and Footer areas.'))
        self.main_position_group_box.setTitle(translate('OpenLP.ThemeWizard', '&Main Area'))
        self.main_position_check_box.setText(translate('OpenLP.ThemeWizard', '&Use default location'))
        self.main_x_label.setText(translate('OpenLP.ThemeWizard', 'X position:'))
        self.main_x_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.main_y_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.main_y_label.setText(translate('OpenLP.ThemeWizard', 'Y position:'))
        self.main_width_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.main_width_label.setText(translate('OpenLP.ThemeWizard', 'Width:'))
        self.main_height_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.main_height_label.setText(translate('OpenLP.ThemeWizard', 'Height:'))
        self.footer_position_group_box.setTitle(translate('OpenLP.ThemeWizard', '&Footer Area'))
        self.footer_x_label.setText(translate('OpenLP.ThemeWizard', 'X position:'))
        self.footer_x_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footer_y_label.setText(translate('OpenLP.ThemeWizard', 'Y position:'))
        self.footer_y_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footer_width_label.setText(translate('OpenLP.ThemeWizard', 'Width:'))
        self.footer_width_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footer_height_label.setText(translate('OpenLP.ThemeWizard', 'Height:'))
        self.footer_height_spin_box.setSuffix(translate('OpenLP.ThemeWizard', 'px'))
        self.footer_position_check_box.setText(translate('OpenLP.ThemeWizard', 'Use default location'))
        theme_wizard.setOption(QtWidgets.QWizard.HaveCustomButton1, False)
        theme_wizard.setButtonText(QtWidgets.QWizard.CustomButton1, translate('OpenLP.ThemeWizard', 'Layout Preview'))
        self.preview_page.setTitle(translate('OpenLP.ThemeWizard', 'Preview and Save'))
        self.preview_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Preview the theme and save it.'))
        self.theme_name_label.setText(translate('OpenLP.ThemeWizard', 'Theme name:'))
        # Align all QFormLayouts towards each other.
        label_width = max(self.background_label.minimumSizeHint().width(),
                          self.horizontal_label.minimumSizeHint().width())
        self.spacer.changeSize(label_width, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
