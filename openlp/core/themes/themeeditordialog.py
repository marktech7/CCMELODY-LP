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
        self.main_layout = QtWidgets.QVBoxLayout(theme_editor)
        theme_editor.setObjectName('OpenLP.ThemeEditor')
        theme_editor.setWindowIcon(UiIcons().main_icon)
        theme_editor.setModal(True)
        # Splitter
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_splitter.setContentsMargins(0, 0, 0, 8)
        self.main_layout.addWidget(self.main_splitter)
        # Toolbox
        self.main_toolbox = QtWidgets.QToolBox(self.main_splitter)
        self.main_toolbox.setObjectName('theme_editor_tool_box')
        self.main_toolbox.setMaximumWidth(750)
        self.main_toolbox.setMinimumWidth(300)
        self.main_toolbox.setStyleSheet(get_library_stylesheet())
        self.main_splitter.insertWidget(0, self.main_toolbox)
        # Bottom Buttons
        self.button_box = create_button_box(theme_editor, 'button_box', ['close', 'save', 'help'])
        self.main_layout.addWidget(self.button_box)
        # Background Widget
        self.background_widget = BackgroundWidget(theme_editor)
        self.background_widget.setObjectName('background_widget')
        self.main_toolbox.addItem(self.background_widget, UiIcons().picture, translate('OpenLP.ThemeEditor',
                                                                                       'Background'))
        # Main Area Widget
        self.main_area_widget = FontSelectWidget(theme_editor)
        self.main_area_widget.setObjectName('main_area_widget')
        self.main_toolbox.addItem(self.main_area_widget, UiIcons().text, translate('OpenLP.ThemeEditor',
                                                                                   'Main Area Font'))
        # Footer Area Widget
        self.footer_area_widget = FontSelectWidget(theme_editor)
        self.footer_area_widget.setObjectName('footer_area_widget')
        self.footer_area_widget.disable_features(FontSelectFeatures.Outline, FontSelectFeatures.Shadow,
                                               FontSelectFeatures.LineSpacing)
        self.main_toolbox.addItem(self.footer_area_widget, UiIcons().text, translate('OpenLP.ThemeEditor',
                                                                                     'Footer Area Font'))
        # Alignment Widget
        self.alignment_widget = AlignmentWidget(theme_editor)
        self.alignment_widget.setObjectName('alignment_widget')
        self.main_toolbox.addItem(self.alignment_widget, UiIcons().text, translate('OpenLP.ThemeEditor',
                                                                                   'Alignment'))
        # Area Position Widget
        self.area_position_widget = AreaPositionWidget(theme_editor)
        self.area_position_widget.setObjectName('area_position_widget')
        self.main_toolbox.addItem(self.area_position_widget, UiIcons().position, translate('OpenLP.ThemeEditor',
                                                                                           'Position'))
        # Transition Widget
        self.transition_widget = TransitionWidget(theme_editor)
        self.transition_widget.setObjectName('transition_widget')
        self.main_toolbox.addItem(self.transition_widget, UiIcons().transition, translate('OpenLP.ThemeEditor',
                                                                                          'Transition'))
        #theme_wizard.addPage(self.area_position_widget)
        # Preview Pane
        #self.theme_name_layout = QtWidgets.QFormLayout()
        #self.theme_name_layout.setObjectName('theme_name_layout')
        #self.theme_name_label = QtWidgets.QLabel(self.preview_widget)
        #self.theme_name_label.setObjectName('theme_name_label')
        #self.theme_name_edit = QtWidgets.QLineEdit(self.preview_widget)
        #self.theme_name_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'[^/\\?*|<>\[\]":<>+%]+'), self))
        #self.theme_name_edit.setObjectName('ThemeNameEdit')
        #self.theme_name_layout.addRow(self.theme_name_label, self.theme_name_edit)
        #self.preview_layout.addLayout(self.theme_name_layout)
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
        #self.background_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Set up your theme\'s background '
        #                                 'according to the parameters below.'))
        #self.main_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
        #                                          'characteristics for the Display text'))
        #self.footer_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
        #                                            'characteristics for the Footer text'))
        #self.alignment_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows additional display '
        #                                          'formatting information to be defined'))
        #self.area_position_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows you to change and move the'
        #                                              ' Main and Footer areas.'))
        pass