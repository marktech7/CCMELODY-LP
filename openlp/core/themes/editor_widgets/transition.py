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
The :mod:`~openlp.core.themes.editor_widgets.transition` module contains the transition widget used in the theme editor
"""
from PyQt5 import QtWidgets, QtCore

from openlp.core.common.i18n import translate
from openlp.core.lib.theme import TransitionType, TransitionSpeed, TransitionDirection
from openlp.core.themes.editor_widgets import ThemeEditorWidget, create_label


class TransitionWidget(ThemeEditorWidget):
    on_value_changed = QtCore.pyqtSignal()

    """
    A widget containing the transition options
    """
    def __init__(self, parent, grid_layout=None):
        super().__init__(parent, grid_layout)
        self.connected_signals = False

    def setup_ui(self):
        """
        Set up the UI
        """
        # Transitions
        self.transitions_enabled_check_box = QtWidgets.QCheckBox(self)
        self.transitions_enabled_check_box.setObjectName('transitions_enabled_check_box')
        self.main_layout.addWidget(self.transitions_enabled_check_box, 3, 1)
        self.transition_effect_label = create_label(self)
        self.transition_effect_label.setObjectName('transition_effect_label')
        self.main_layout.addWidget(self.transition_effect_label, 4, 0)
        self.transition_effect_combo_box = QtWidgets.QComboBox(self)
        self.transition_effect_combo_box.setObjectName('transition_effect_combo_box')
        self.transition_effect_combo_box.addItems(['', '', '', '', ''])
        self.main_layout.addWidget(self.transition_effect_combo_box, 4, 1)
        self.transition_speed_label = create_label(self)
        self.transition_speed_label.setObjectName('transition_speed_label')
        self.main_layout.addWidget(self.transition_speed_label, 5, 0)
        self.transition_speed_combo_box = QtWidgets.QComboBox(self)
        self.transition_speed_combo_box.setObjectName('transition_speed_combo_box')
        self.transition_speed_combo_box.addItems(['', '', ''])
        self.main_layout.addWidget(self.transition_speed_combo_box, 5, 1)
        self.transition_direction_label = create_label(self)
        self.transition_direction_label.setObjectName('transition_direction_label')
        self.main_layout.addWidget(self.transition_direction_label, 4, 2)
        self.transition_direction_combo_box = QtWidgets.QComboBox(self)
        self.transition_direction_combo_box.setObjectName('transition_direction_combo_box')
        self.transition_direction_combo_box.addItems(['', ''])
        self.main_layout.addWidget(self.transition_direction_combo_box, 4, 3)
        self.transition_reverse_check_box = QtWidgets.QCheckBox(self)
        self.transition_reverse_check_box.setObjectName('transition_reverse_check_box')
        self.main_layout.addWidget(self.transition_reverse_check_box, 5, 3)

    def connect_signals(self):
        # Connect slots
        if not self.connected_signals:
            self.connected_signals = True
            self.transitions_enabled_check_box.stateChanged.connect(self._on_transition_enabled_changed)
            self.transitions_enabled_check_box.stateChanged.connect(self._on_value_changed_emit)
            self.transition_speed_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)
            self.transition_effect_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)
            self.transition_direction_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)

    def disconnect_signals(self):
        self.connected_signals = False
        self.transitions_enabled_check_box.stateChanged.disconnect(self._on_transition_enabled_changed)
        self.transitions_enabled_check_box.stateChanged.disconnect(self._on_value_changed_emit)
        self.transition_speed_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)
        self.transition_effect_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)
        self.transition_direction_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)

    def retranslate_ui(self):
        """
        Translate the widgets
        """
        self.transitions_enabled_check_box.setText(translate('OpenLP.ThemeWizard', 'Enable transitions'))
        self.transition_effect_label.setText(translate('OpenLP.ThemeWizard', 'Effect:'))
        self.transition_effect_combo_box.setItemText(TransitionType.Fade, translate('OpenLP.ThemeWizard', 'Fade'))
        self.transition_effect_combo_box.setItemText(TransitionType.Slide, translate('OpenLP.ThemeWizard', 'Slide'))
        self.transition_effect_combo_box.setItemText(TransitionType.Concave, translate('OpenLP.ThemeWizard', 'Concave'))
        self.transition_effect_combo_box.setItemText(TransitionType.Convex, translate('OpenLP.ThemeWizard', 'Convex'))
        self.transition_effect_combo_box.setItemText(TransitionType.Zoom, translate('OpenLP.ThemeWizard', 'Zoom'))
        self.transition_speed_label.setText(translate('OpenLP.ThemeWizard', 'Speed:'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Normal, translate('OpenLP.ThemeWizard', 'Normal'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Fast, translate('OpenLP.ThemeWizard', 'Fast'))
        self.transition_speed_combo_box.setItemText(TransitionSpeed.Slow, translate('OpenLP.ThemeWizard', 'Slow'))
        self.transition_direction_label.setText(translate('OpenLP.ThemeWizard', 'Direction:'))
        self.transition_direction_combo_box.setItemText(TransitionDirection.Horizontal, translate('OpenLP.ThemeWizard',
                                                                                                  'Horizontal'))
        self.transition_direction_combo_box.setItemText(TransitionDirection.Vertical, translate('OpenLP.ThemeWizard',
                                                                                                'Vertical'))
        self.transition_reverse_check_box.setText(translate('OpenLP.ThemeWizard', 'Reverse'))

    def _on_transition_enabled_changed(self, value):
        """
        Update the UI widgets when the transition is enabled or disabled
        """
        self.transition_effect_label.setEnabled(value)
        self.transition_effect_combo_box.setEnabled(value)
        self.transition_speed_label.setEnabled(value)
        self.transition_speed_combo_box.setEnabled(value)
        self.transition_direction_combo_box.setEnabled(value)
        self.transition_direction_label.setEnabled(value)
        self.transition_reverse_check_box.setEnabled(value)

    @property
    def is_transition_enabled(self):
        return self.transitions_enabled_check_box.isChecked()

    @is_transition_enabled.setter
    def is_transition_enabled(self, value):
        self.transitions_enabled_check_box.setChecked(value)
        self._on_transition_enabled_changed(value)

    @property
    def transition_type(self):
        return self.transition_effect_combo_box.currentIndex()

    @transition_type.setter
    def transition_type(self, value):
        if isinstance(value, str):
            self.transition_effect_combo_box.setCurrentIndex(TransitionType.from_string(value))
        elif isinstance(value, int):
            self.transition_effect_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('transition_type must either be a string or an int')

    @property
    def transition_speed(self):
        return self.transition_speed_combo_box.currentIndex()

    @transition_speed.setter
    def transition_speed(self, value):
        if isinstance(value, str):
            self.transition_speed_combo_box.setCurrentIndex(TransitionSpeed.from_string(value))
        elif isinstance(value, int):
            self.transition_speed_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('transition_speed must either be a string or an int')

    @property
    def transition_direction(self):
        return self.transition_direction_combo_box.currentIndex()

    @transition_direction.setter
    def transition_direction(self, value):
        if isinstance(value, str):
            self.transition_direction_combo_box.setCurrentIndex(TransitionDirection.from_string(value))
        elif isinstance(value, int):
            self.transition_direction_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('transition_direction must either be a string or an int')

    @property
    def is_transition_reverse_enabled(self):
        return self.transition_reverse_check_box.isChecked()

    @is_transition_reverse_enabled.setter
    def is_transition_reverse_enabled(self, value):
        self.transition_reverse_check_box.setChecked(value)

    def _on_value_changed_emit(self):
        self.on_value_changed.emit()
