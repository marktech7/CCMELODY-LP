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
The :mod:`~openlp.core.themes.editor_widgets` module contains editor widgets used by Theme Editor.
"""
from PyQt5 import QtWidgets, QtCore

from openlp.core.widgets.labels import FormLabel


class FakeGridLayout(QtWidgets.QVBoxLayout):
    """
    Serves as a shim to allow Theme Widgets to both work in ThemeEditor and ThemeWizard.
    """
    def addWidget(self, widget, row=None, column=None, rowSpan=None, columnSpan=None, alignment=None):
        super().addWidget(widget)

    def addLayout(self, widget, row=None, column=None, rowSpan=None, columnSpan=None, alignment=None):
        super().addLayout(widget)

    def addItem(self, item, row=None, column=None, rowSpan=None, columnSpan=None, alignment=None):
        super().addItem(item)


WIDGET_PROXY_DIRECT_ACCESS = ['_widget', '_column_width', 'layout', '_layout', 'resize_columns', 'create_widgets']


class WidgetProxy(object):
    def _get_widgets(self):
        if not hasattr(self, '_widget'):
            self._widget = object.__getattribute__(self, 'create_widgets')()
        if type(self._widget) is not list:
            self._widget = [self._widget]
        return self._widget

    def create_widgets(self):
        raise NotImplementedError("Must be implemented by inherited class.")

    def setup_ui(self):
        return self._get_widget_attribute('setup_ui')()

    def retranslate_ui(self):
        return self._get_widget_attribute('retranslate_ui')()

    def _get_widget_attribute(self, name):
        widgets = object.__getattribute__(self, '_get_widgets')()
        for widget in widgets:
            try:
                return getattr(widget, name)
            except AttributeError:
                continue
        raise AttributeError()

    def __getattribute__(self, name: str):
        value_except = False
        try:
            value = object.__getattribute__(self, name)
        except AttributeError:
            value_except = True
            value = None
        if value is None and name not in WIDGET_PROXY_DIRECT_ACCESS:
            try:
                return object.__getattribute__(self, '_get_widget_attribute')(name)
            except AttributeError:
                value_except = True
                value = None
        if value_except:
            raise AttributeError()
        return value

    def __setattr__(self, name, value):
        if name in WIDGET_PROXY_DIRECT_ACCESS:
            return object.__setattr__(self, name, value)
        widgets = object.__getattribute__(self, '_get_widgets')()
        for widget in widgets:
            setattr(widget, name, value)


class ThemeEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent, grid_layout=None):
        QtWidgets.QWidget.__init__(self, parent)
        if grid_layout is not None:
            # Compatibility with GridLayoutPage
            self.main_layout = grid_layout
            self.is_grid_layout = True
        else:
            self.main_layout = FakeGridLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.is_grid_layout = False
            self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop or QtCore.Qt.AlignmentFlag.AlignLeft)
            # Only need to call this on constructor if instantiated as widget
            self.setup_ui()
            self.retranslate_ui()

    def setup_ui(self):
        ...

    def retranslate_ui(self):
        ...

    def connect_signals(self):
        ...

    def disconnect_signals(self):
        ...


def create_label(widget, parent=None):
    if widget.is_grid_layout:
        return FormLabel(parent if parent else widget)
    else:
        return QtWidgets.QLabel(parent if parent else widget)
