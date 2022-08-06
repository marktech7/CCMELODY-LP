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
The :mod:`~openlp.core.themes.editor_widgets.areaposition` module contains the area position widget used in the
theme editor
"""
from PyQt5 import QtWidgets, QtCore

from openlp.core.common.i18n import translate
from openlp.core.themes.editor_widgets import ThemeEditorWidget, create_label


class AreaPositionWidget(ThemeEditorWidget):
    on_value_changed = QtCore.pyqtSignal()

    """
    A widget for the area positioning in the theme editor
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_signals = False

    def setup_ui(self):
        """
        Set up the UI
        """
        # Main area position
        self.main_position_group_box = QtWidgets.QGroupBox(self)
        self.main_position_group_box.setObjectName('main_position_group_box')
        self.main_position_layout = QtWidgets.QGridLayout(self.main_position_group_box)
        self.main_position_layout.setObjectName('main_position_layout')
        self.main_position_check_box = QtWidgets.QCheckBox(self.main_position_group_box)
        self.main_position_check_box.setObjectName('main_position_check_box')
        self.main_position_layout.addWidget(self.main_position_check_box, 0, 0, 1, 2)
        self.main_x_label = create_label(self, self.main_position_group_box)
        self.main_x_label.setObjectName('main_x_label')
        self.main_position_layout.addWidget(self.main_x_label, 1, 0)
        self.main_x_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_x_spin_box.setMaximum(9999)
        self.main_x_spin_box.setObjectName('main_x_spin_box')
        self.main_position_layout.addWidget(self.main_x_spin_box, 1, 1)
        self.main_y_label = create_label(self, self.main_position_group_box)
        self.main_y_label.setObjectName('main_y_label')
        self.main_position_layout.addWidget(self.main_y_label, 2, 0)
        self.main_y_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_y_spin_box.setMaximum(9999)
        self.main_y_spin_box.setObjectName('main_y_spin_box')
        self.main_position_layout.addWidget(self.main_y_spin_box, 2, 1)
        self.main_width_label = create_label(self, self.main_position_group_box)
        self.main_width_label.setObjectName('main_width_label')
        self.main_width_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_width_spin_box.setMaximum(9999)
        self.main_width_spin_box.setObjectName('main_width_spin_box')
        self.main_position_layout.addWidget(self.main_width_label, 3, 0)
        self.main_position_layout.addWidget(self.main_width_spin_box, 3, 1)
        self.main_height_label = create_label(self, self.main_position_group_box)
        self.main_height_label.setObjectName('main_height_label')
        self.main_height_spin_box = QtWidgets.QSpinBox(self.main_position_group_box)
        self.main_height_spin_box.setMaximum(9999)
        self.main_height_spin_box.setObjectName('main_height_spin_box')
        self.main_position_layout.addWidget(self.main_height_label, 4, 0)
        self.main_position_layout.addWidget(self.main_height_spin_box, 4, 1)
        self.main_layout.addWidget(self.main_position_group_box)
        # Footer area position
        self.footer_position_group_box = QtWidgets.QGroupBox(self)
        self.footer_position_group_box.setObjectName('footer_position_group_box')
        self.footer_position_layout = QtWidgets.QGridLayout(self.footer_position_group_box)
        self.footer_position_layout.setObjectName('footer_position_layout')
        self.footer_position_check_box = QtWidgets.QCheckBox(self.footer_position_group_box)
        self.footer_position_check_box.setObjectName('footer_position_check_box')
        self.footer_position_layout.addWidget(self.footer_position_check_box, 0, 0, 1, 2)
        self.footer_x_label = create_label(self, self.footer_position_group_box)
        self.footer_x_label.setObjectName('footer_x_label')
        self.footer_x_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_x_spin_box.setMaximum(9999)
        self.footer_x_spin_box.setObjectName('footer_x_spin_box')
        self.footer_position_layout.addWidget(self.footer_x_label, 1, 0)
        self.footer_position_layout.addWidget(self.footer_x_spin_box, 1, 1)
        self.footer_y_label = create_label(self, self.footer_position_group_box)
        self.footer_y_label.setObjectName('footer_y_label')
        self.footer_y_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_y_spin_box.setMaximum(9999)
        self.footer_y_spin_box.setObjectName('footer_y_spin_box')
        self.footer_position_layout.addWidget(self.footer_y_label, 2, 0)
        self.footer_position_layout.addWidget(self.footer_y_spin_box, 2, 1)
        self.footer_width_label = create_label(self, self.footer_position_group_box)
        self.footer_width_label.setObjectName('footer_width_label')
        self.footer_width_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_width_spin_box.setMaximum(9999)
        self.footer_width_spin_box.setObjectName('footer_width_spin_box')
        self.footer_position_layout.addWidget(self.footer_width_label, 3, 0)
        self.footer_position_layout.addWidget(self.footer_width_spin_box, 3, 1)
        self.footer_height_label = create_label(self, self.footer_position_group_box)
        self.footer_height_label.setObjectName('footer_height_label')
        self.footer_height_spin_box = QtWidgets.QSpinBox(self.footer_position_group_box)
        self.footer_height_spin_box.setMaximum(9999)
        self.footer_height_spin_box.setObjectName('footer_height_spin_box')
        self.footer_position_layout.addWidget(self.footer_height_label, 4, 0)
        self.footer_position_layout.addWidget(self.footer_height_spin_box, 4, 1)
        self.main_layout.addWidget(self.footer_position_group_box)

    def connect_signals(self):
        # Connect signals to slots
        if not self.connected_signals:
            self.connected_signals = True
            self.main_position_check_box.toggled.connect(self.main_x_spin_box.setDisabled)
            self.main_position_check_box.toggled.connect(self.main_y_spin_box.setDisabled)
            self.main_position_check_box.toggled.connect(self.main_width_spin_box.setDisabled)
            self.main_position_check_box.toggled.connect(self.main_height_spin_box.setDisabled)
            self.main_position_check_box.toggled.connect(self._on_value_changed_emit)
            self.footer_position_check_box.toggled.connect(self.footer_x_spin_box.setDisabled)
            self.footer_position_check_box.toggled.connect(self.footer_y_spin_box.setDisabled)
            self.footer_position_check_box.toggled.connect(self.footer_width_spin_box.setDisabled)
            self.footer_position_check_box.toggled.connect(self.footer_height_spin_box.setDisabled)
            self.footer_position_check_box.toggled.connect(self._on_value_changed_emit)
            self.main_x_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.main_y_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.main_width_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.main_height_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.footer_x_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.footer_y_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.footer_width_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            self.footer_height_spin_box.valueChanged.connect(self._on_value_changed_emit_debounce)
            # Re-checking after connecting signals
            self.main_x_spin_box.setDisabled(self.main_position_check_box.isChecked())
            self.main_y_spin_box.setDisabled(self.main_position_check_box.isChecked())
            self.main_width_spin_box.setDisabled(self.main_position_check_box.isChecked())
            self.main_height_spin_box.setDisabled(self.main_position_check_box.isChecked())
            self.footer_x_spin_box.setDisabled(self.footer_position_check_box.isChecked())
            self.footer_y_spin_box.setDisabled(self.footer_position_check_box.isChecked())
            self.footer_width_spin_box.setDisabled(self.footer_position_check_box.isChecked())
            self.footer_height_spin_box.setDisabled(self.footer_position_check_box.isChecked())

    def disconnect_signals(self):
        self.connected_signals = False
        self.main_position_check_box.toggled.disconnect(self.main_x_spin_box.setDisabled)
        self.main_position_check_box.toggled.disconnect(self.main_y_spin_box.setDisabled)
        self.main_position_check_box.toggled.disconnect(self.main_width_spin_box.setDisabled)
        self.main_position_check_box.toggled.disconnect(self.main_height_spin_box.setDisabled)
        self.main_position_check_box.toggled.disconnect(self._on_value_changed_emit)
        self.footer_position_check_box.toggled.disconnect(self.footer_x_spin_box.setDisabled)
        self.footer_position_check_box.toggled.disconnect(self.footer_y_spin_box.setDisabled)
        self.footer_position_check_box.toggled.disconnect(self.footer_width_spin_box.setDisabled)
        self.footer_position_check_box.toggled.disconnect(self.footer_height_spin_box.setDisabled)
        self.footer_position_check_box.toggled.disconnect(self._on_value_changed_emit)
        self.main_x_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.main_y_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.main_width_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.main_height_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.footer_x_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.footer_y_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.footer_width_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)
        self.footer_height_spin_box.valueChanged.disconnect(self._on_value_changed_emit_debounce)

    def retranslate_ui(self):
        """
        Translate the UI
        """
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

    @property
    def use_main_default_location(self):
        return self.main_position_check_box.isChecked()

    @use_main_default_location.setter
    def use_main_default_location(self, value):
        self.main_position_check_box.setChecked(value)

    @property
    def main_x(self):
        return self.main_x_spin_box.value()

    @main_x.setter
    def main_x(self, value):
        self.main_x_spin_box.setValue(value)

    @property
    def main_y(self):
        return self.main_y_spin_box.value()

    @main_y.setter
    def main_y(self, value):
        self.main_y_spin_box.setValue(value)

    @property
    def main_width(self):
        return self.main_width_spin_box.value()

    @main_width.setter
    def main_width(self, value):
        self.main_width_spin_box.setValue(value)

    @property
    def main_height(self):
        return self.main_height_spin_box.value()

    @main_height.setter
    def main_height(self, value):
        self.main_height_spin_box.setValue(value)

    @property
    def use_footer_default_location(self):
        return self.footer_position_check_box.isChecked()

    @use_footer_default_location.setter
    def use_footer_default_location(self, value):
        self.footer_position_check_box.setChecked(value)

    @property
    def footer_x(self):
        return self.footer_x_spin_box.value()

    @footer_x.setter
    def footer_x(self, value):
        self.footer_x_spin_box.setValue(value)

    @property
    def footer_y(self):
        return self.footer_y_spin_box.value()

    @footer_y.setter
    def footer_y(self, value):
        self.footer_y_spin_box.setValue(value)

    @property
    def footer_width(self):
        return self.footer_width_spin_box.value()

    @footer_width.setter
    def footer_width(self, value):
        self.footer_width_spin_box.setValue(value)

    @property
    def footer_height(self):
        return self.footer_height_spin_box.value()

    @footer_height.setter
    def footer_height(self, value):
        self.footer_height_spin_box.setValue(value)

    def _on_value_changed_emit(self):
        self.on_value_changed.emit()

    def _on_value_changed_emit_debounce(self):
        if not hasattr(self, 'debounce_timer'):
            self.debounce_timer = QtCore.QTimer(self)
            self.debounce_timer.setInterval(200)
            self.debounce_timer.setSingleShot(True)
            self.debounce_timer.timeout.connect(self._on_value_changed_emit)
        self.debounce_timer.start()
