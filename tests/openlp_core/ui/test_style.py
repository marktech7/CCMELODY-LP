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
Package to test the :mod:`~openlp.core.ui.style` module.
"""
from unittest import skipIf
from unittest.mock import MagicMock, patch, call

from openlp.core.ui.style import MEDIA_MANAGER_STYLE, Themes, WIN_REPAIR_STYLESHEET, get_application_stylesheet, \
    get_library_stylesheet, has_theme, is_theme_dark, set_default_darkmode
import openlp.core.ui.style


@skipIf(not hasattr(openlp.core.ui.style, 'qdarkstyle'), 'qdarkstyle is not installed')
@patch('openlp.core.ui.style.HAS_QDARKSTYLE', True)
@patch('openlp.core.ui.style.qdarkstyle')
def test_get_application_stylesheet_qdarkstyle(mocked_qdarkstyle, mock_settings):
    """Test that the qdarkstyle stylesheet is returned when available and enabled"""
    # GIVEN: Theme is QDarkTheme
    mock_settings.value.return_value = Themes.QDarkTheme
    mocked_qdarkstyle.load_stylesheet_pyqt5.return_value = 'dark_style'

    # WHEN: get_application_stylesheet() is called
    result = get_application_stylesheet()

    # THEN: the result should be QDarkStyle stylesheet
    assert result == 'dark_style'


@skipIf(not hasattr(openlp.core.ui.style, 'qdarkstyle'), 'qdarkstyle is not installed')
@patch('openlp.core.ui.style.HAS_QDARKSTYLE', True)
def test_has_theme_qdarkstyle_true_when_available(mock_settings):
    """Test that the QDarkStyle theme exists when qdarkstyle is available """
    # GIVEN: Theme is QDarkTheme
    mock_settings.value.return_value = Themes.QDarkTheme

    # WHEN: has_theme() is called
    result = has_theme(Themes.QDarkTheme)

    # THEN: the result should be true
    assert result is True


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_has_theme_qdarkstyle_false_when_unavailable(mock_settings):
    """Test that the QDarkStyle theme not exists when qdarkstyle is not available """
    # GIVEN: Theme is QDarkTheme
    mock_settings.value.return_value = Themes.QDarkTheme

    # WHEN: has_theme() is called
    result = has_theme(Themes.QDarkTheme)

    # THEN: the result should be false
    assert result is False


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_win')
@patch('openlp.core.app.QtWidgets.QApplication.palette')
def test_get_application_stylesheet_not_alternate_rows(mocked_palette, mocked_is_win, mock_settings):
    """Test that the alternate rows stylesheet is returned when enabled in settings"""
    def settings_values(key):
        if key == 'advanced/theme_name':
            return Themes.DefaultLight
        else:
            return False

    # GIVEN: We're not on Windows and theme is not QDarkStyle
    mocked_is_win.return_value = False
    mock_settings.value = MagicMock(side_effect=settings_values)
    mocked_palette.return_value.color.return_value.name.return_value = 'color'

    # WHEN: get_application_stylesheet() is called
    result = get_application_stylesheet()

    # THEN: result should match non-alternate-rows
    mock_settings.value.assert_has_calls([call('advanced/theme_name'), call('advanced/alternate rows')])
    assert result == 'QTableWidget, QListWidget, QTreeWidget {alternate-background-color: color;}\n', result


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_win')
def test_get_application_stylesheet_win_repair(mocked_is_win, mock_settings):
    """Test that the Windows repair stylesheet is returned when on Windows"""
    def settings_values(key):
        if key == 'advanced/theme_name':
            return Themes.DefaultLight
        else:
            return True

    # GIVEN: We're on Windows and Theme is not QDarkStyle
    mocked_is_win.return_value = True
    mock_settings.value = MagicMock(side_effect=settings_values)

    # WHEN: get_application_stylesheet() is called
    result = get_application_stylesheet()

    # THEN: result should return Windows repair stylesheet
    mock_settings.value.assert_has_calls([call('advanced/theme_name'), call('advanced/alternate rows')])
    assert result == WIN_REPAIR_STYLESHEET


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_win')
def test_get_application_stylesheet_not_win_repair(mocked_is_win, mock_settings):
    """Test that the Windows repair stylesheet is not returned when not in Windows"""
    def settings_values(key):
        if key == 'advanced/theme_name':
            return Themes.DefaultLight
        else:
            return True

    # GIVEN: We're on Windows and Theme is not QDarkStyle
    mocked_is_win.return_value = False
    mock_settings.value = MagicMock(side_effect=settings_values)

    # WHEN: get_application_stylesheet() is called
    result = get_application_stylesheet()

    # THEN: result should not return Windows repair stylesheet
    mock_settings.value.assert_has_calls([call('advanced/theme_name'), call('advanced/alternate rows')])
    assert result != WIN_REPAIR_STYLESHEET


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_get_library_stylesheet_automatic_theme(mock_settings):
    """Test that the media manager stylesheet is returned for Automatic theme"""
    # GIVEN: Theme is Automatic
    mock_settings.value.return_value = Themes.Automatic

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: the correct stylesheet should be returned
    assert result == MEDIA_MANAGER_STYLE


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_get_library_stylesheet_defaultlight_theme(mock_settings):
    """Test that the media manager stylesheet is returned for Default Light theme"""
    # GIVEN: Theme is DefaultLight
    mock_settings.value.return_value = Themes.DefaultLight

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: the correct stylesheet should be returned
    assert result == MEDIA_MANAGER_STYLE


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_get_library_stylesheet_defaultdark_theme(mock_settings):
    """Test that the media manager stylesheet is returned for Default Dark theme"""
    # GIVEN: Theme is DefaultDark
    mock_settings.value.return_value = Themes.DefaultDark

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: the correct stylesheet should be returned
    assert result == MEDIA_MANAGER_STYLE


@skipIf(not hasattr(openlp.core.ui.style, 'qdarkstyle'), 'qdarkstyle is not installed')
@patch('openlp.core.ui.style.HAS_QDARKSTYLE', True)
def test_get_library_stylesheet_qdarktheme_theme(mock_settings):
    """Test that the media manager stylesheet is not returned for QDarkTheme theme"""
    # GIVEN: Theme is QDarkTheme
    mock_settings.value.return_value = Themes.QDarkTheme

    # WHEN: get_library_stylesheet() is called
    result = get_library_stylesheet()

    # THEN: The correct stylesheet should be returned
    assert result == ''


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_system_darkmode')
def test_is_theme_automatic_dark_when_system_dark(mocked_is_system_darkmode,
                                                  mock_settings):
    """Test that the Automatic Theme is Dark on System Dark Theme"""
    # GIVEN: Theme is Automatic and System Theme is Dark
    mock_settings.value.return_value = Themes.Automatic
    mocked_is_system_darkmode.return_value = True

    # WHEN: is_theme_dark() is called
    result = is_theme_dark()

    # THEN: the result should be true
    assert result is True


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_system_darkmode')
def test_is_theme_automatic_light_when_system_light(mocked_is_system_darkmode,
                                                    mock_settings):
    """Test that the Automatic Theme is not Dark on System Light Theme"""
    # GIVEN: Theme is Automatic and System Theme is Light
    mocked_is_system_darkmode.return_value = False
    mock_settings.value.return_value = Themes.Automatic

    # WHEN: is_theme_dark() is called
    result = is_theme_dark()

    # THEN: the result should be false
    assert result is False


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_is_theme_lightdefault_not_dark(mock_settings):
    """Test that the DefaultLight Theme is not Dark"""
    # GIVEN: Theme is DefaultDark
    mock_settings.value.return_value = Themes.DefaultLight

    # WHEN: is_theme_dark() is called
    result = is_theme_dark()

    # THEN: the result should be false
    assert result is False


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_is_theme_darkdefault_dark(mock_settings):
    """Test that the DefaultDark Theme is Dark"""
    # GIVEN: Theme is DefaultDark
    mock_settings.value.return_value = Themes.DefaultDark

    # WHEN: is_theme_dark() is called
    result = is_theme_dark()

    # THEN: the result should be true
    assert result is True


@skipIf(not hasattr(openlp.core.ui.style, 'qdarkstyle'), 'qdarkstyle is not installed')
@patch('openlp.core.ui.style.HAS_QDARKSTYLE', True)
def test_is_theme_qdarkstyle_dark(mock_settings):
    """Test that the QDarkTheme Theme is Dark"""
    # GIVEN: Theme is DefaultDark
    mock_settings.value.return_value = Themes.QDarkTheme

    # WHEN: is_theme_dark() is called
    result = is_theme_dark()

    # THEN: the result should be true
    assert result is True


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
def test_set_default_darkmode_defaultdark_theme_sets_palette(mock_settings):
    """Test that the set_default_darkmode sets App Palette for DefaultDark theme"""
    # GIVEN: Theme is DefaultDark
    mock_settings.value.return_value = Themes.DefaultDark
    mock_app = MagicMock()

    # WHEN: set_default_darkmode() is called
    set_default_darkmode(mock_app)

    # THEN: app palette should be changed
    mock_app.setPalette.assert_called_once()


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_system_darkmode')
def test_set_default_darkmode_automatic_theme_win_dark_sets_palette(mocked_is_system_darkmode,
                                                                    mock_settings):
    """Test that the set_default_darkmode sets App Palette for Automatic theme on System with Dark Theme"""
    # GIVEN: Theme is automatic on System with Dark Theme
    mock_settings.value.return_value = Themes.Automatic
    mocked_is_system_darkmode.return_value = True
    mock_app = MagicMock()

    # WHEN: set_default_darkmode() is called
    set_default_darkmode(mock_app)

    # THEN: app palette should be changed
    mock_app.setPalette.assert_called_once()


@patch('openlp.core.ui.style.HAS_QDARKSTYLE', False)
@patch('openlp.core.ui.style.is_system_darkmode')
def test_set_default_darkmode_automatic_theme_win_light_not_sets_palette(mocked_is_system_darkmode,
                                                                         mock_settings):
    """Test that the set_default_darkmode doesnt't set App Palette for Automatic theme on System Light Theme"""
    # GIVEN: Theme is automatic with System Light Theme
    mock_settings.value.return_value = Themes.Automatic
    mocked_is_system_darkmode.return_value = False
    mock_app = MagicMock()

    # WHEN: set_default_darkmode() is called
    set_default_darkmode(mock_app)

    # THEN: app palette should not be changed
    mock_app.setPalette.assert_not_called()
