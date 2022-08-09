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
Package to test the openlp.core.themes.editor_widgets.areaposition package.
"""

from unittest.mock import MagicMock, patch
from openlp.core.themes.editor_widgets.areaposition import DEBOUNCE_TIME, AreaPositionWidget


def test_init_(settings):
    """
    Test the initialisation of AreaPositionWidget
    """
    # GIVEN: The AreaPositionWidget class
    # WHEN: Initialising AreaPositionWidget
    # THEN: We should have an instance of the widget with no errors
    AreaPositionWidget()


def test_get_use_main_default_location(settings):
    """
    Test the use_main_default_location getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to index 1
    page = AreaPositionWidget()
    page.main_position_check_box.setChecked(False)

    # WHEN: The property is accessed
    result = page.use_main_default_location

    # THEN: The result should be correct
    assert result is False


def test_set_use_main_default_location(settings):
    """
    Test the use_main_default_location setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.use_main_default_location = True

    # THEN: The combobox should be correct
    assert page.main_position_check_box.isChecked() is True


def test_get_main_x(settings):
    """
    Test the main_x getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to index 1
    page = AreaPositionWidget()
    page.main_x_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.main_x

    # THEN: The result should be correct
    assert result == 10


def test_set_main_x(settings):
    """
    Test the main_x setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.main_x = 20

    # THEN: The combobox should be correct
    assert page.main_x_spin_box.value() == 20


def test_get_main_y(settings):
    """
    Test the main_y getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indey 1
    page = AreaPositionWidget()
    page.main_y_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.main_y

    # THEN: The result should be correct
    assert result == 10


def test_set_main_y(settings):
    """
    Test the main_y setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.main_y = 20

    # THEN: The combobox should be correct
    assert page.main_y_spin_box.value() == 20


def test_get_main_width(settings):
    """
    Test the main_width getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indewidth 1
    page = AreaPositionWidget()
    page.main_width_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.main_width

    # THEN: The result should be correct
    assert result == 10


def test_set_main_width(settings):
    """
    Test the main_width setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.main_width = 20

    # THEN: The combobox should be correct
    assert page.main_width_spin_box.value() == 20


def test_get_main_height(settings):
    """
    Test the main_height getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indeheight 1
    page = AreaPositionWidget()
    page.main_height_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.main_height

    # THEN: The result should be correct
    assert result == 10


def test_set_main_height(settings):
    """
    Test the main_height setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.main_height = 20

    # THEN: The combobox should be correct
    assert page.main_height_spin_box.value() == 20


def test_get_footer_x(settings):
    """
    Test the footer_x getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to index 1
    page = AreaPositionWidget()
    page.footer_x_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.footer_x

    # THEN: The result should be correct
    assert result == 10


def test_set_footer_x(settings):
    """
    Test the footer_x setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.footer_x = 20

    # THEN: The combobox should be correct
    assert page.footer_x_spin_box.value() == 20


def test_get_footer_y(settings):
    """
    Test the footer_y getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indey 1
    page = AreaPositionWidget()
    page.footer_y_spin_box.setValue(10)

    # WHEN: The property is accessed
    result = page.footer_y

    # THEN: The result should be correct
    assert result == 10


def test_set_footer_y(settings):
    """
    Test the footer_y setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.footer_y = 20

    # THEN: The combobox should be correct
    assert page.footer_y_spin_box.value() == 20


def test_get_footer_width(settings):
    """
    Test the footer_width getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indewidth 1
    page = AreaPositionWidget()
    page.footer_width_spin_box.setValue(1900)

    # WHEN: The property is accessed
    result = page.footer_width

    # THEN: The result should be correct
    assert result == 1900


def test_set_footer_width(settings):
    """
    Test the footer_width setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.footer_width = 1900

    # THEN: The combobox should be correct
    assert page.footer_width_spin_box.value() == 1900


def test_get_footer_height(settings):
    """
    Test the footer_height getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to indeheight 1
    page = AreaPositionWidget()
    page.footer_height_spin_box.setValue(1080)

    # WHEN: The property is accessed
    result = page.footer_height

    # THEN: The result should be correct
    assert result == 1080


def test_set_footer_height(settings):
    """
    Test the footer_height setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.footer_height = 1080

    # THEN: The combobox should be correct
    assert page.footer_height_spin_box.value() == 1080


def test_get_use_footer_default_location(settings):
    """
    Test the use_footer_default_location getter
    """
    # GIVEN: An AreaPositionWidget instance with the combobox set to index 1
    page = AreaPositionWidget()
    page.footer_position_check_box.setChecked(False)

    # WHEN: The property is accessed
    result = page.use_footer_default_location

    # THEN: The result should be correct
    assert result is False


def test_set_use_footer_default_location(settings):
    """
    Test the use_footer_default_location setter with an int
    """
    # GIVEN: An AreaPositionWidget instance
    page = AreaPositionWidget()

    # WHEN: The property is set
    page.use_footer_default_location = True

    # THEN: The combobox should be correct
    assert page.footer_position_check_box.isChecked() is True


def test_main_position_check_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the main_position_check_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.main_position_check_box.toggle()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_footer_position_check_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the footer_position_check_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.footer_position_check_box.toggle()

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_main_x_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the main_x_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.main_x_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_main_y_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the main_y_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.main_y_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_main_width_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the main_width_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.main_width_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_main_height_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the main_height_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.main_height_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_footer_x_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the footer_x_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.footer_x_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_footer_y_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the footer_y_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.footer_y_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_footer_width_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the footer_width_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.footer_width_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


def test_footer_height_spin_box_triggers_on_value_changed(settings):
    """
    Test if on_value_changed signal is triggered when the footer_height_spin_box value is changed
    """
    # GIVEN: An instance of AreaPositionWidget and a mocked debounce handler
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget._on_value_changed_emit_debounce = MagicMock(side_effect=lambda _: widget.on_value_changed.emit())
    widget.connect_signals()

    # WHEN: The value is changed
    widget.footer_height_spin_box.setValue(2)

    # THEN: An on_value_changed event should be emitted
    widget.on_value_changed.emit.assert_called_once()


@patch('openlp.core.themes.editor_widgets.areaposition.QtCore.QTimer')
def test_on_value_changed_debouncer(mocked_QTimer, settings):
    """
    Test if on_value_changed debouncer is constructed with DEBOUNCE_TIME
    """
    # GIVEN: An instance of AreaPositionWidget
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: Some value is changed
    widget.footer_height_spin_box.setValue(2)

    # THEN: The debounce timer should be fired after DEBOUNCE_TIME
    mocked_QTimer.assert_called_once()
    widget.debounce_timer.setInterval.assert_called_with(DEBOUNCE_TIME)


@patch('openlp.core.themes.editor_widgets.areaposition.QtCore.QTimer')
def test_on_value_changed_debouncer_after_started(mocked_QTimer, settings):
    """
    Test if on_value_changed debouncer is triggered on second time being invoked
    """
    # GIVEN: An instance of AreaPositionWidget
    widget = AreaPositionWidget()
    widget.on_value_changed = MagicMock()
    widget.connect_signals()

    # WHEN: Some value is changed twice
    widget.footer_height_spin_box.setValue(2)
    widget.footer_height_spin_box.setValue(3)

    # THEN: An on_value_changed event should be constructed once and started twice
    mocked_QTimer.assert_called_once()
    assert widget.debounce_timer.start.call_count == 2
