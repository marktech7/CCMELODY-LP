# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
The :mod:`~openlp.core.ui.style` contains style functions.
"""
import darkdetect
from enum import Enum
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import is_win
from openlp.core.common.registry import Registry

try:
    import qdarkstyle
    HAS_QDARKSTYLE = True
except ImportError:
    HAS_QDARKSTYLE = False

WIN_REPAIR_STYLESHEET = """
QMainWindow::separator
{
  border: none;
}

QDockWidget::title
{
  border: 1px solid palette(dark);
  padding-left: 5px;
  padding-top: 2px;
  margin: 1px 0;
}

QToolBar
{
  border: none;
  margin: 0;
  padding: 0;
}
"""

MEDIA_MANAGER_STYLE = """
::tab#media_tool_box {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 palette(button), stop: 1.0 palette(mid));
    border: 0;
    border-radius: 2px;
    margin-top: 0;
    margin-bottom: 0;
    text-align: left;
}
/* This is here to make the tabs on KDE with the Breeze theme work */
::tab:selected {}
"""

PROGRESSBAR_STYLE = """
QProgressBar{
    height: 10px;
}
"""


class Themes(Enum):
    """
    An enumeration for themes.
    """
    Automatic = 'automatic'
    DefaultLight = 'light:default'
    DefaultDark = 'dark:default'
    QDarkTheme = 'dark:qdarktheme'


def is_theme_dark():
    theme_name = Registry().get('settings').value('advanced/ui_theme_name')

    if init_theme_if_needed(theme_name):
        theme_name = Themes.Automatic

    if theme_name == Themes.Automatic:
        return is_system_darkmode()
    else:
        return theme_name.value.startswith('dark:')


def is_theme(theme: Themes):
    theme_name = Registry().get('settings').value('advanced/ui_theme_name')

    if init_theme_if_needed(theme_name):
        theme_name = Themes.Automatic

    return theme_name == theme


def init_theme_if_needed(theme_name):
    will_init = not isinstance(theme_name, Themes)

    if will_init:
        Registry().get('settings').setValue('advanced/ui_theme_name', Themes.Automatic)

    return will_init


def has_theme(theme: Themes):
    if theme == Themes.QDarkTheme:
        return HAS_QDARKSTYLE
    return True


IS_SYSTEM_DARKMODE = None


def is_system_darkmode():
    global IS_SYSTEM_DARKMODE

    if IS_SYSTEM_DARKMODE is None:
        try:
            IS_SYSTEM_DARKMODE = darkdetect.isDark()
        except Exception:
            IS_SYSTEM_DARKMODE = False

    return IS_SYSTEM_DARKMODE


def set_default_darkmode(app):
    """
    Setup darkmode on the application if enabled in the OpenLP Settings or using a dark mode system theme.
    Source: https://github.com/worstje/manuskript/blob/develop/manuskript/main.py (GPL3)
    Changes:
        * Allowed palette to be set on any operating system;
        * Split Windows Dark Mode detection to another function.
    """
    if is_theme(Themes.DefaultDark) or (is_theme(Themes.Automatic) and is_theme_dark()):
        app.setStyle('Fusion')
        dark_palette = QtGui.QPalette()
        dark_color = QtGui.QColor(45, 45, 45)
        disabled_color = QtGui.QColor(127, 127, 127)
        dark_palette.setColor(QtGui.QPalette.Window, dark_color)
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(18, 18, 18))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_color)
        dark_palette.setColor(QtGui.QPalette.Button, dark_color)
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_color)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, disabled_color)
        # Fixes ugly (not to mention hard to read) disabled menu items.
        # Source: https://bugreports.qt.io/browse/QTBUG-10322?focusedCommentId=371060#comment-371060
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtCore.Qt.transparent)
        # Fixes ugly media manager headers.
        dark_palette.setColor(QtGui.QPalette.Mid, QtGui.QColor(64, 64, 64))
        app.setPalette(dark_palette)


def get_application_stylesheet():
    """
    Return the correct application stylesheet based on the current style and operating system

    :return str: The correct stylesheet as a string
    """
    stylesheet = ''
    if is_theme(Themes.QDarkTheme):
        stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    else:
        if not Registry().get('settings').value('advanced/alternate rows'):
            base_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Base)
            alternate_rows_repair_stylesheet = \
                'QTableWidget, QListWidget, QTreeWidget {alternate-background-color: ' + base_color.name() + ';}\n'
            stylesheet += alternate_rows_repair_stylesheet
        if is_win():
            stylesheet += WIN_REPAIR_STYLESHEET
    return stylesheet


def get_library_stylesheet():
    """
    Return the correct stylesheet for the main window

    :return str: The correct stylesheet as a string
    """
    if not is_theme(Themes.QDarkTheme):
        return MEDIA_MANAGER_STYLE
    else:
        return ''
