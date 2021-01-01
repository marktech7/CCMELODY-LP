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
The :mod:`~openlp.core.ui.dark` module looks for and loads a dark theme
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import is_win
from openlp.core.common.registry import Registry


try:
    import qdarkstyle
    HAS_DARK_STYLE = True
except ImportError:
    HAS_DARK_STYLE = False

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


def set_windows_darkmode(app):
    """
    Setup darkmode on the application if enabled in the OS (windows) settings
    Source: https://github.com/worstje/manuskript/blob/develop/manuskript/main.py (GPL3)
    """
    theme_settings = QtCore.QSettings('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes'
                                      '\\Personalize',
                                      QtCore.QSettings.NativeFormat)
    if theme_settings.value('AppsUseLightTheme') == 0:
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
        app.setPalette(dark_palette)


def get_application_stylesheet():
    """
    Return the correct application stylesheet based on the current style and operating system

    :return str: The correct stylesheet as a string
    """
    stylesheet = ''
    if not is_win() and HAS_DARK_STYLE and Registry().get('settings').value('advanced/use_dark_style'):
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
    if not HAS_DARK_STYLE or not Registry().get('settings').value('advanced/use_dark_style'):
        return MEDIA_MANAGER_STYLE
    else:
        return ''
