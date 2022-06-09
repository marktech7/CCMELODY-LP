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
The :mod:`~openlp.core.themes..editor_widgets.alignment` module contains the alignment widget used in the theme editor
"""
from PyQt5 import QtWidgets, QtCore

from openlp.core.common.i18n import translate
from openlp.core.lib.theme import HorizontalType, VerticalType
from openlp.core.lib.ui import create_valign_selection_widgets
from openlp.core.themes.editor_widgets import ThemeEditorWidget, create_label


class AlignmentWidget(ThemeEditorWidget):
    on_value_changed = QtCore.pyqtSignal()

    """
    A widget containing the alignment options
    """
    def __init__(self, parent, grid_layout=None):
        super().__init__(parent, grid_layout)
        self.connected_signals = False

    def setup_ui(self):
        """
        Set up the UI
        """
        # Alignment
        self.horizontal_label = create_label(self)
        self.horizontal_label.setObjectName('horizontal_label')
        self.main_layout.addWidget(self.horizontal_label, 0, 0)
        self.horizontal_combo_box = QtWidgets.QComboBox(self)
        self.horizontal_combo_box.addItems(['', '', '', ''])
        self.horizontal_combo_box.setObjectName('horizontal_combo_box')
        self.main_layout.addWidget(self.horizontal_combo_box, 0, 1, 1, 3)
        self.vertical_label, self.vertical_combo_box = create_valign_selection_widgets(self, self.is_grid_layout)
        self.vertical_label.setObjectName('vertical_label')
        self.main_layout.addWidget(self.vertical_label, 1, 0)
        self.vertical_combo_box.setObjectName('vertical_combo_box')
        self.main_layout.addWidget(self.vertical_combo_box, 1, 1, 1, 3)
    
    def connect_signals(self):
        # Connect signals to slots
        if not self.connected_signals:
            self.connected_signals = True
            self.horizontal_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)
            self.vertical_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)
    
    def disconnect_signals(self):
        self.connected_signals = False
        self.horizontal_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)
        self.vertical_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)

    def retranslate_ui(self):
        """
        Translate the widgets
        """
        self.horizontal_label.setText(translate('OpenLP.ThemeWizard', 'Horizontal Align:'))
        self.horizontal_combo_box.setItemText(HorizontalType.Left, translate('OpenLP.ThemeWizard', 'Left'))
        self.horizontal_combo_box.setItemText(HorizontalType.Right, translate('OpenLP.ThemeWizard', 'Right'))
        self.horizontal_combo_box.setItemText(HorizontalType.Center, translate('OpenLP.ThemeWizard', 'Center'))
        self.horizontal_combo_box.setItemText(HorizontalType.Justify, translate('OpenLP.ThemeWizard', 'Justify'))

    @property
    def horizontal_align(self):
        return self.horizontal_combo_box.currentIndex()

    @horizontal_align.setter
    def horizontal_align(self, value):
        if isinstance(value, str):
            self.horizontal_combo_box.setCurrentIndex(HorizontalType.from_string(value))
        elif isinstance(value, int):
            self.horizontal_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('horizontal_align must either be a string or an int')

    @property
    def vertical_align(self):
        return self.vertical_combo_box.currentIndex()

    @vertical_align.setter
    def vertical_align(self, value):
        if isinstance(value, str):
            self.vertical_combo_box.setCurrentIndex(VerticalType.from_string(value))
        elif isinstance(value, int):
            self.vertical_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('vertical_align must either be a string or an int')

    def _on_value_changed_emit(self):
        self.on_value_changed.emit()
