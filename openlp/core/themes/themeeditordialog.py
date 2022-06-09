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
"""
The Create/Edit theme editor dialog
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from openlp.core.common.i18n import translate
from openlp.core.display.render import ThemePreviewRenderer
from openlp.core.lib.ui import create_button_box
from openlp.core.themes.editor_widgets.alignment import AlignmentWidget
from openlp.core.themes.editor_widgets.areaposition import AreaPositionWidget
from openlp.core.themes.editor_widgets.background import BackgroundWidget
from openlp.core.themes.editor_widgets.fontselect import FontSelectFeatures, FontSelectWidget
from openlp.core.themes.editor_widgets.transition import TransitionWidget

from openlp.core.ui.icons import UiIcons
from openlp.core.ui.style import get_library_stylesheet
from openlp.core.widgets.layouts import AspectRatioLayout


class Ui_ThemeEditorDialog(object):
    """
    The Create/Edit theme editor dialog
    """
    def setup_ui(self, theme_editor: QtWidgets.QDialog):
        """
        Set up the UI
        """
        self.setMinimumSize(800, 600)
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        self.main_layout = QtWidgets.QVBoxLayout(theme_editor)
        theme_editor.setObjectName('OpenLP.ThemeEditor')
        theme_editor.setWindowIcon(UiIcons().main_icon)
        theme_editor.setModal(True)
        # Splitter
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_splitter.setContentsMargins(0, 0, 0, 8)
        self.main_layout.addWidget(self.main_splitter)
        # Toolbox
        self.main_toolbox_container = QtWidgets.QWidget()
        self.main_toolbox_layout = QtWidgets.QVBoxLayout()
        self.main_toolbox_layout.setSpacing(0)
        self.main_toolbox_layout.setContentsMargins(0, 0, 0, 0)
        self.theme_name_label = QtWidgets.QLabel(self.main_toolbox_container)
        self.theme_name_label.setObjectName('theme_name_label')
        self.theme_name_edit = QtWidgets.QLineEdit(self.main_toolbox_container)
        self.theme_name_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'[^/\\?*|<>\[\]":<>+%]+'), self))
        self.theme_name_edit.setObjectName('ThemeNameEdit')
        self.theme_name_edit.setContentsMargins(0, 0, 0, 8)
        self.main_toolbox_layout.addWidget(self.theme_name_label)
        self.main_toolbox_layout.addWidget(self.theme_name_edit)
        self.main_toolbox = QtWidgets.QToolBox(self.main_toolbox_container)
        self.main_toolbox.setObjectName('theme_editor_tool_box')
        self.main_toolbox.setMaximumWidth(750)
        self.main_toolbox.setMinimumWidth(300)
        self.main_toolbox.setStyleSheet(get_library_stylesheet())
        self.main_toolbox_layout.addWidget(self.main_toolbox)
        self.main_toolbox_container.setLayout(self.main_toolbox_layout)
        self.main_splitter.insertWidget(0, self.main_toolbox_container)
        # Bottom Buttons
        self.button_box = create_button_box(theme_editor, 'button_box', ['cancel', 'save', 'help'])
        self.main_layout.addWidget(self.button_box)
        # Background Toolbox Section
        self.background_section = QtWidgets.QWidget(self.main_toolbox)
        self.background_section_layout = QtWidgets.QVBoxLayout(self.background_section)
        self.background_section_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop
                                                    or QtCore.Qt.AlignmentFlag.AlignLeft)
        self.background_section_label = QtWidgets.QLabel(self.background_section)
        self.background_section_label.setWordWrap(True)
        self.background_widget = BackgroundWidget(theme_editor)
        self.background_widget.setObjectName('background_widget')
        self.background_section_layout.addWidget(self.background_section_label)
        self.background_section_layout.addWidget(self.background_widget)
        self.main_toolbox.addItem(self.background_section, UiIcons().picture, translate('OpenLP.ThemeEditor',
                                                                                             'Background'))
        # Main Area Section
        self.main_area_section = QtWidgets.QWidget(self.main_toolbox)
        self.main_area_section_layout = QtWidgets.QVBoxLayout(self.main_area_section)
        self.main_area_section_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop
                                                    or QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_area_section_label = QtWidgets.QLabel(self.main_area_section)
        self.main_area_section_label.setWordWrap(True)
        self.main_area_widget = FontSelectWidget(theme_editor)
        self.main_area_widget.setObjectName('main_area_widget')
        self.main_area_section_layout.addWidget(self.main_area_section_label)
        self.main_area_section_layout.addWidget(self.main_area_widget)
        self.main_toolbox.addItem(self.main_area_section, UiIcons().text, translate('OpenLP.ThemeEditor',
                                                                                    'Main Area Font'))
        # Footer Area Section
        self.footer_area_section = QtWidgets.QWidget(self.main_toolbox)
        self.footer_area_section_layout = QtWidgets.QVBoxLayout(self.footer_area_section)
        self.footer_area_section_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop
                                                      or QtCore.Qt.AlignmentFlag.AlignLeft)
        self.footer_area_section_label = QtWidgets.QLabel(self.footer_area_section)
        self.footer_area_section_label.setWordWrap(True)
        self.footer_area_widget = FontSelectWidget(theme_editor)
        self.footer_area_widget.setObjectName('footer_area_widget')
        self.footer_area_widget.disable_features(FontSelectFeatures.Outline, FontSelectFeatures.Shadow,
                                               FontSelectFeatures.LineSpacing)
        self.footer_area_section_layout.addWidget(self.footer_area_section_label)
        self.footer_area_section_layout.addWidget(self.footer_area_widget)
        self.main_toolbox.addItem(self.footer_area_section, UiIcons().text, translate('OpenLP.ThemeEditor',
                                                                                      'Footer Area Text'))
        # Alignment Widget
        self.alignment_widget = AlignmentWidget(theme_editor)
        self.alignment_widget.setObjectName('alignment_widget')
        self.main_toolbox.addItem(self.alignment_widget, UiIcons().alignment, translate('OpenLP.ThemeEditor',
                                                                                   'Alignment'))
        # Area Position Widget
        self.area_position_section = QtWidgets.QWidget(self.main_toolbox)
        self.area_position_section_layout = QtWidgets.QVBoxLayout(self.area_position_section)
        self.area_position_section_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop
                                                        or QtCore.Qt.AlignmentFlag.AlignLeft)
        self.area_position_section_label = QtWidgets.QLabel(self.area_position_section)
        self.area_position_section_label.setWordWrap(True)
        self.area_position_widget = AreaPositionWidget(theme_editor)
        self.area_position_widget.setObjectName('area_position_widget')
        self.area_position_section_layout.addWidget(self.area_position_section_label)
        self.area_position_section_layout.addWidget(self.area_position_widget)
        self.main_toolbox.addItem(self.area_position_section, UiIcons().position, translate('OpenLP.ThemeEditor',
                                                                                            'Position'))
        # Transition Widget
        self.transition_widget = TransitionWidget(theme_editor)
        self.transition_widget.setObjectName('transition_widget')
        self.main_toolbox.addItem(self.transition_widget, UiIcons().transition, translate('OpenLP.ThemeEditor',
                                                                                          'Transition'))
        # Preview Pane
        screen_ratio = 16 / 9
        self.preview_area = QtWidgets.QWidget(self.main_splitter)
        self.preview_area.setObjectName('PreviewArea')
        self.preview_area.setContentsMargins(8, 0, 0, 0)
        self.preview_area_layout = AspectRatioLayout(self.preview_area, screen_ratio)
        self.preview_area_layout.margin = 0
        self.preview_area_layout.setSpacing(0)
        self.preview_area_layout.setObjectName('preview_web_layout')
        self.preview_box = ThemePreviewRenderer(self)
        self.preview_box.setObjectName('preview_box')
        self.preview_area_layout.addWidget(self.preview_box)
        self.preview_area.setLayout(self.preview_area_layout)
        self.main_splitter.insertWidget(1, self.preview_area)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        self.retranslate_ui()
    
    def retranslate_ui(self):
        #self.alignment_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows additional display '
        #                                          'formatting information to be defined'))
        self.background_section_label.setText(translate('OpenLP.ThemeWizard', 'Set up your theme\'s background '
                                                             'according to the parameters below.'))
        self.main_area_section_label.setText(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                       'characteristics for the Display text'))
        self.footer_area_section_label.setText(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                         'characteristics for the Footer text'))
        self.area_position_section_label.setText(translate('OpenLP.ThemeWizard', 'Allows you to change and move the'
                                                           ' Main and Footer areas.'))
        self.theme_name_label.setText(translate('OpenLP.ThemeWizard', 'Theme name:'))
