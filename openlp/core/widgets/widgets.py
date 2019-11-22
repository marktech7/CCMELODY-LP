# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
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
The :mod:`~openlp.core.widgets.widgets` module contains custom widgets used in OpenLP
"""
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.settings import ProxyMode, Settings
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.buttons import ColorButton


SCREENS_LAYOUT_STYLE = """
#screen_frame {
  background-color: palette(base);
}
#screen_frame QPushButton  {
  background-color: palette(window);
  border: 3px solid palette(text);
  border-radius: 3px;
  height: 100px;
  outline: 0;
  width: 150px;
}
#screen_frame QPushButton:checked  {
    border-color: palette(highlight);
}
"""


class ProxyWidget(QtWidgets.QGroupBox):
    """
    A proxy settings widget that implements loading and saving its settings.
    """
    def __init__(self, parent=None):
        """
        Initialise the widget.

        :param QtWidgets.QWidget | None parent: The widgets parent
        """
        super().__init__(parent)
        self._setup()

    def _setup(self):
        """
        A setup method seperate from __init__ to allow easier testing
        """
        self.setup_ui()
        self.load()

    def setup_ui(self):
        """
        Create the widget layout and sub widgets
        """
        self.layout = QtWidgets.QFormLayout(self)
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.no_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.no_proxy_radio, ProxyMode.NO_PROXY)
        self.layout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.no_proxy_radio)
        self.use_sysem_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.use_sysem_proxy_radio, ProxyMode.SYSTEM_PROXY)
        self.layout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.use_sysem_proxy_radio)
        self.manual_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.manual_proxy_radio, ProxyMode.MANUAL_PROXY)
        self.layout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.manual_proxy_radio)
        self.http_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTP:', self.http_edit)
        self.https_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTPS:', self.https_edit)
        self.username_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('Username:', self.username_edit)
        self.password_edit = QtWidgets.QLineEdit(self)
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.layout.addRow('Password:', self.password_edit)
        # Signal / Slots
        self.radio_group.buttonToggled.connect(self.on_radio_group_button_toggled)

    def on_radio_group_button_toggled(self, button, checked):
        """
        Handles the toggled signal on the radio buttons. The signal is emitted twice if a radio butting being toggled on
        causes another radio button in the group to be toggled off.

        En/Disables the `Manual Proxy` line edits depending on the currently selected radio button

        :param QtWidgets.QRadioButton button: The button that has toggled
        :param bool checked: The buttons new state
        """
        group_id = self.radio_group.id(button)  # The work around (see above comment)
        enable_manual_edits = group_id == ProxyMode.MANUAL_PROXY and checked
        self.http_edit.setEnabled(enable_manual_edits)
        self.https_edit.setEnabled(enable_manual_edits)
        self.username_edit.setEnabled(enable_manual_edits)
        self.password_edit.setEnabled(enable_manual_edits)

    def retranslate_ui(self):
        """
        Translate the Ui
        """
        self.setTitle(translate('OpenLP.ProxyWidget', 'Proxy Server Settings'))
        self.no_proxy_radio.setText(translate('OpenLP.ProxyWidget', 'No prox&y'))
        self.use_sysem_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Use system proxy'))
        self.manual_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Manual proxy configuration'))
        proxy_example = translate('OpenLP.ProxyWidget', 'e.g. proxy_server_address:port_no')
        self.layout.labelForField(self.http_edit).setText(translate('OpenLP.ProxyWidget', 'HTTP:'))
        self.http_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.https_edit).setText(translate('OpenLP.ProxyWidget', 'HTTPS:'))
        self.https_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.username_edit).setText(translate('OpenLP.ProxyWidget', 'Username:'))
        self.layout.labelForField(self.password_edit).setText(translate('OpenLP.ProxyWidget', 'Password:'))

    def load(self):
        """
        Load the data from the settings to the widget.
        """
        settings = Settings()
        checked_radio = self.radio_group.button(settings.value('advanced/proxy mode'))
        checked_radio.setChecked(True)
        self.http_edit.setText(settings.value('advanced/proxy http'))
        self.https_edit.setText(settings.value('advanced/proxy https'))
        self.username_edit.setText(settings.value('advanced/proxy username'))
        self.password_edit.setText(settings.value('advanced/proxy password'))

    def save(self):
        """
        Save the widget data to the settings
        """
        settings = Settings()  # TODO: Migrate from old system
        settings.setValue('advanced/proxy mode', self.radio_group.checkedId())
        settings.setValue('advanced/proxy http', self.http_edit.text())
        settings.setValue('advanced/proxy https', self.https_edit.text())
        settings.setValue('advanced/proxy username', self.username_edit.text())
        settings.setValue('advanced/proxy password', self.password_edit.text())


class ProxyDialog(QtWidgets.QDialog):
    """
    A basic dialog to show proxy settingd
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.proxy_widget = ProxyWidget(self)
        self.layout.addWidget(self.proxy_widget)
        self.button_box = \
            QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.retranslate_ui()

    def accept(self):
        """
        Reimplement the the accept slot so that the ProxyWidget settings can be saved.
        :rtype: None
        """
        self.proxy_widget.save()
        super().accept()

    def retranslate_ui(self):
        self.proxy_widget.retranslate_ui()
        self.setWindowTitle(translate('OpenLP.ProxyDialog', 'Proxy Server Settings'))


class ScreenButton(QtWidgets.QPushButton):
    """
    A special button class that holds the screen information about it
    """
    def __init__(self, parent, screen):
        """
        Initialise this button
        """
        super().__init__(parent)
        self.setObjectName('screen_{number}_button'.format(number=screen.number))
        self.setCheckable(True)
        self.setText(str(screen))
        self.screen = screen


class ScreenSelectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, screens=None):
        super().__init__(parent)
        self.current_screen = None
        self.identify_labels = []
        self.screens = screens or []
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self._on_identify_timer_shot)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(SCREENS_LAYOUT_STYLE)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.screen_frame = QtWidgets.QFrame(self)
        self.screen_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.screen_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.screen_frame.setObjectName('screen_frame')
        self.screen_frame_layout = QtWidgets.QHBoxLayout(self.screen_frame)
        self.screen_frame_layout.setContentsMargins(16, 16, 16, 16)
        self.screen_frame_layout.setSpacing(8)
        self.screen_frame_layout.setObjectName('screen_frame_layout')
        self.layout.addWidget(self.screen_frame)
        self.identify_layout = QtWidgets.QHBoxLayout()
        self.screen_details_layout = QtWidgets.QVBoxLayout()
        self.screen_details_layout.setObjectName('screen_details_layout')
        self.screen_number_label = QtWidgets.QLabel(self)
        self.screen_number_label.setObjectName('screen_number_label')
        self.screen_details_layout.addWidget(self.screen_number_label)
        self.use_screen_check_box = QtWidgets.QCheckBox(self)
        self.use_screen_check_box.setVisible(False)
        self.screen_details_layout.addWidget(self.use_screen_check_box)
        self.display_group_box = QtWidgets.QGroupBox(self)
        self.display_group_box.setObjectName('display_group_box')
        self.display_group_box.setCheckable(True)
        self.display_group_box_layout = QtWidgets.QGridLayout(self.display_group_box)
        self.display_group_box_layout.setSpacing(8)
        self.display_group_box_layout.setObjectName('display_group_box_layout')
        self.full_screen_radio_button = QtWidgets.QRadioButton(self.display_group_box)
        self.full_screen_radio_button.setObjectName('full_screen_radio_button')
        self.display_group_box_layout.addWidget(self.full_screen_radio_button, 0, 0, 1, 4)
        self.custom_geometry_button = QtWidgets.QRadioButton(self.display_group_box)
        self.custom_geometry_button.setObjectName('custom_geometry_button')
        self.display_group_box_layout.addWidget(self.custom_geometry_button, 1, 0, 1, 4)
        self.left_label = QtWidgets.QLabel(self.display_group_box)
        self.left_label.setObjectName('left_label')
        self.display_group_box_layout.addWidget(self.left_label, 2, 1, 1, 1)
        self.top_label = QtWidgets.QLabel(self.display_group_box)
        self.top_label.setObjectName('top_label')
        self.display_group_box_layout.addWidget(self.top_label, 2, 2, 1, 1)
        self.width_label = QtWidgets.QLabel(self.display_group_box)
        self.width_label.setObjectName('width_label')
        self.display_group_box_layout.addWidget(self.width_label, 2, 3, 1, 1)
        self.height_label = QtWidgets.QLabel(self.display_group_box)
        self.height_label.setObjectName('height_label')
        self.display_group_box_layout.addWidget(self.height_label, 2, 4, 1, 1)
        self.left_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.left_spin_box.setObjectName('left_spin_box')
        self.left_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.left_spin_box, 3, 1, 1, 1)
        self.top_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.top_spin_box.setObjectName('top_spin_box')
        self.top_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.top_spin_box, 3, 2, 1, 1)
        self.width_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.width_spin_box.setObjectName('width_spin_box')
        self.width_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.width_spin_box, 3, 3, 1, 1)
        self.height_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.height_spin_box.setObjectName('height_spin_box')
        self.height_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.height_spin_box, 3, 4, 1, 1)
        self.display_group_box_layout.setColumnStretch(3, 1)
        self.display_group_box.setLayout(self.display_group_box_layout)
        self.screen_details_layout.addWidget(self.display_group_box)
        self.identify_layout.addLayout(self.screen_details_layout)
        self.identify_button = QtWidgets.QPushButton(self)
        self.identify_button.setObjectName('identify_button')
        self.identify_layout.addWidget(
            self.identify_button, stretch=1, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.screen_button_group = QtWidgets.QButtonGroup(self.screen_frame)
        self.screen_button_group.setExclusive(True)
        self.screen_button_group.setObjectName('screen_button_group')
        self.layout.addLayout(self.identify_layout)
        self.layout.addStretch()

        # Signals and slots
        self.display_group_box.clicked.connect(self.on_display_clicked)
        self.use_screen_check_box.clicked.connect(self.on_display_clicked)
        self.use_screen_check_box.toggled.connect(self.display_group_box.setChecked)
        self.custom_geometry_button.toggled.connect(self.height_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.left_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.top_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.width_spin_box.setEnabled)
        self.identify_button.clicked.connect(self.on_identify_button_clicked)

        self._setup_spin_box(self.left_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.top_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.width_spin_box, 0, 9999, 0)
        self._setup_spin_box(self.height_spin_box, 0, 9999, 0)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.full_screen_radio_button.setText(translate('OpenLP.ScreensTab', 'F&ull screen'))
        self.width_label.setText(translate('OpenLP.ScreensTab', 'Width:'))
        use_screen_str = translate('OpenLP.ScreensTab', 'Use this screen as a display')
        self.use_screen_check_box.setText(use_screen_str)
        self.display_group_box.setTitle(use_screen_str)
        self.left_label.setText(translate('OpenLP.ScreensTab', 'Left:'))
        self.custom_geometry_button.setText(translate('OpenLP.ScreensTab', 'Custom &geometry'))
        self.top_label.setText(translate('OpenLP.ScreensTab', 'Top:'))
        self.height_label.setText(translate('OpenLP.ScreensTab', 'Height:'))
        self.identify_button.setText(translate('OpenLP.ScreensTab', 'Identify Screens'))

    def on_display_clicked(self, is_checked):
        if not is_checked:
            critical_error_message_box(translate('OpenLP.ScreensTab', 'Select a Display'),
                                       translate('OpenLP.ScreensTab', 'You need to select at least one screen to be '
                                                 'used as a display. Select the screen you wish to use as a display, '
                                                 'and check the checkbox for that screen.'),
                                       parent=self, question=False)
            self.use_screen_check_box.setChecked(True)
            self.display_group_box.setChecked(True)
        else:
            for screen in self.screens:
                screen.is_display = False
            self.current_screen.is_display = True

    def _save_screen(self, screen):
        """
        Save the details in the UI to the screen

        :param openlp.core.display.screens.Screen screen:
        :return: None
        """
        if not screen:
            return
        screen.is_display = self.display_group_box.isChecked()
        if self.custom_geometry_button.isChecked():
            screen.custom_geometry = QtCore.QRect(self.left_spin_box.value(), self.top_spin_box.value(),
                                                  self.width_spin_box.value(), self.height_spin_box.value())
        else:
            screen.custom_geometry = None

    def _setup_spin_box(self, spin_box, mininum, maximum, value):
        """
        Set up the spin box

        :param QtWidgets.QSpinBox spin_box:
        :param int minimun:
        :param int maximum:
        :param int value:
        :return: None
        """
        spin_box.setMinimum(mininum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)

    def load(self):
        # Remove all the existing items in the layout
        while self.screen_frame_layout.count() > 0:
            item = self.screen_frame_layout.takeAt(0)
            if item.widget() is not None:
                widget = item.widget()
                if widget in self.screen_button_group.buttons():
                    self.screen_button_group.removeButton(widget)
                widget.setParent(None)
                widget.deleteLater()
            del item
        # Add the existing screens into the frame
        self.screen_frame_layout.addStretch()
        for screen in self.screens:
            screen_button = ScreenButton(self.screen_frame, screen)
            screen_button.clicked.connect(self.on_screen_button_clicked)
            self.screen_frame_layout.addWidget(screen_button)
            self.screen_button_group.addButton(screen_button)
            if screen.number == 0:
                screen_button.click()
        self.screen_frame_layout.addStretch()

    def save(self):
        """
        Save the screen settings
        """
        self._save_screen(self.current_screen)
        settings = Settings()
        screen_settings = {}
        for screen in self.screens:
            screen_settings[screen.number] = screen.to_dict()
        settings.setValue('core/screens', screen_settings)
        # On save update the screens as well

    def use_simple_view(self):
        """
        Hide advanced options. Added for use in the FTW

        :rtype: None
        """
        self.use_screen_check_box.setVisible(True)
        self.display_group_box.setVisible(False)

    @QtCore.pyqtSlot()
    def _on_identify_timer_shot(self):
        for label in self.identify_labels:
            label.hide()
            label.setParent(None)
            label.deleteLater()
        self.identify_labels = []

    def on_identify_button_clicked(self):
        """
        Display a widget on every screen for 5 seconds
        """
        for screen in self.screens:
            label = QtWidgets.QLabel(None)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText(str(screen))
            label.setStyleSheet('font-size: 24pt; font-weight: bold; '
                                'background-color: #0C0; color: #000; border: 5px solid #000;')
            label.setGeometry(QtCore.QRect(screen.geometry.x(), screen.geometry.y(), screen.geometry.width(), 100))
            label.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint |
                                 QtCore.Qt.WindowDoesNotAcceptFocus)
            label.show()
            self.identify_labels.append(label)
        self.timer.start()

    def on_screen_button_clicked(self):
        """
        Respond to a screen button being clicked
        """
        screen = self.sender().screen
        if self.current_screen is not screen:
            self._save_screen(self.current_screen)
        self.screen_number_label.setText(str(screen))
        self.use_screen_check_box.setChecked(screen.is_display)
        self.display_group_box.setChecked(screen.is_display)
        self.full_screen_radio_button.setChecked(screen.custom_geometry is None)
        self.custom_geometry_button.setChecked(screen.custom_geometry is not None)
        self._setup_spin_box(self.left_spin_box, screen.display_geometry.y(), screen.display_geometry.right(),
                             screen.display_geometry.x())
        self._setup_spin_box(self.top_spin_box, screen.display_geometry.y(), screen.display_geometry.bottom(),
                             screen.display_geometry.y())
        self._setup_spin_box(self.width_spin_box, 0, screen.display_geometry.width(), screen.display_geometry.width())
        self._setup_spin_box(self.height_spin_box, 0, screen.display_geometry.height(),
                             screen.display_geometry.height())
        self.current_screen = screen


class FontSelectWidget(QtWidgets.QWidget):
    """
    A font selection widget
    """
    Outline = 'outline'
    Shadow = 'shadow'
    LineSpacing = 'line_spacing'

    font_name_changed = QtCore.pyqtSignal(str)
    font_size_changed = QtCore.pyqtSignal(int)
    font_color_changed = QtCore.pyqtSignal(str)
    is_bold_changed = QtCore.pyqtSignal(bool)
    is_italic_changed = QtCore.pyqtSignal(bool)
    line_spacing_changed = QtCore.pyqtSignal(int)
    is_outline_enabled_changed = QtCore.pyqtSignal(bool)
    outline_color_changed = QtCore.pyqtSignal(str)
    outline_size_changed = QtCore.pyqtSignal(int)
    is_shadow_enabled_changed = QtCore.pyqtSignal(bool)
    shadow_color_changed = QtCore.pyqtSignal(str)
    shadow_size_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._column_width = 0
        self.setup_ui()
        self.feature_widgets = {
            FontSelectWidget.Outline: [self.outline_groupbox],
            FontSelectWidget.Shadow: [self.shadow_groupbox],
            FontSelectWidget.LineSpacing: [self.line_spacing_label, self.line_spacing_spinbox]
        }

    def setup_ui(self):
        self.layout = QtWidgets.QGridLayout(self)
        # Font name
        self.font_name_label = QtWidgets.QLabel(self)
        self.font_name_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.font_name_label.setObjectName('font_name_label')
        self.layout.addWidget(self.font_name_label, 0, 0)
        self.font_name_combobox = QtWidgets.QFontComboBox(self)
        self.font_name_combobox.setObjectName('font_name_combobox')
        self.layout.addWidget(self.font_name_combobox, 0, 1, 1, 3)
        # Font color
        self.font_color_label = QtWidgets.QLabel(self)
        self.font_color_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.font_color_label.setObjectName('font_color_label')
        self.layout.addWidget(self.font_color_label, 1, 0)
        self.font_color_button = ColorButton(self)
        self.font_color_button.setObjectName('font_color_button')
        self.layout.addWidget(self.font_color_button, 1, 1)
        # Font style
        self.font_style_label = QtWidgets.QLabel(self)
        self.font_style_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.font_style_label.setObjectName('font_style_label')
        self.layout.addWidget(self.font_style_label, 1, 2)
        self.style_layout = QtWidgets.QHBoxLayout()
        self.style_bold_button = QtWidgets.QToolButton(self)
        self.style_bold_button.setIcon(UiIcons().bold)
        self.style_bold_button.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Bold))
        self.style_bold_button.setObjectName('style_bold_button')
        self.style_layout.addWidget(self.style_bold_button)
        self.style_italic_button = QtWidgets.QToolButton(self)
        self.style_italic_button.setIcon(UiIcons().italic)
        self.style_italic_button.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Italic))
        self.style_italic_button.setObjectName('style_italic_button')
        self.style_layout.addWidget(self.style_italic_button)
        self.style_layout.addStretch(1)
        self.layout.addLayout(self.style_layout, 1, 3)
        # Font size
        self.font_size_label = QtWidgets.QLabel(self)
        self.font_size_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.font_size_label.setObjectName('font_size_label')
        self.layout.addWidget(self.font_size_label, 2, 0)
        self.font_size_spinbox = QtWidgets.QSpinBox(self)
        self.font_size_spinbox.setMaximum(999)
        self.font_size_spinbox.setValue(16)
        self.font_size_spinbox.setObjectName('font_size_spinbox')
        self.layout.addWidget(self.font_size_spinbox, 2, 1)
        # Line spacing
        self.line_spacing_label = QtWidgets.QLabel(self)
        self.line_spacing_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.line_spacing_label.setObjectName('line_spacing_label')
        self.layout.addWidget(self.line_spacing_label, 2, 2)
        self.line_spacing_spinbox = QtWidgets.QSpinBox(self)
        self.line_spacing_spinbox.setMinimum(-250)
        self.line_spacing_spinbox.setMaximum(250)
        self.line_spacing_spinbox.setObjectName('line_spacing_spinbox')
        self.layout.addWidget(self.line_spacing_spinbox, 2, 3)
        # Outline
        self.outline_groupbox = QtWidgets.QGroupBox(self)
        self.outline_groupbox.setCheckable(True)
        self.outline_groupbox.setChecked(False)
        self.outline_groupbox.setObjectName('outline_groupbox')
        self.outline_layout = QtWidgets.QGridLayout(self.outline_groupbox)
        self.layout.addWidget(self.outline_groupbox, 3, 0, 1, 2)
        # Outline colour
        self.outline_color_label = QtWidgets.QLabel(self.outline_groupbox)
        self.outline_color_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.outline_color_label.setObjectName('outline_color_label')
        self.outline_layout.addWidget(self.outline_color_label, 0, 0)
        self.outline_color_button = ColorButton(self.outline_groupbox)
        self.outline_color_button.setObjectName('outline_color_button')
        self.outline_layout.addWidget(self.outline_color_button, 0, 1)
        # Outline size
        self.outline_size_label = QtWidgets.QLabel(self.outline_groupbox)
        self.outline_size_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.outline_size_label.setObjectName('outline_size_label')
        self.outline_layout.addWidget(self.outline_size_label, 1, 0)
        self.outline_size_spinbox = QtWidgets.QSpinBox(self.outline_groupbox)
        self.outline_size_spinbox.setMaximum(9999)
        self.outline_size_spinbox.setObjectName('outline_size_spinbox')
        self.outline_layout.addWidget(self.outline_size_spinbox, 1, 1)
        # Shadow
        self.shadow_groupbox = QtWidgets.QGroupBox(self)
        self.shadow_groupbox.setCheckable(True)
        self.shadow_groupbox.setChecked(False)
        self.shadow_groupbox.setObjectName('shadow_groupbox')
        self.shadow_layout = QtWidgets.QGridLayout(self.shadow_groupbox)
        self.layout.addWidget(self.shadow_groupbox, 3, 2, 1, 2)
        # Shadow color
        self.shadow_color_label = QtWidgets.QLabel(self.shadow_groupbox)
        self.shadow_color_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shadow_color_label.setObjectName('shadow_color_label')
        self.shadow_layout.addWidget(self.shadow_color_label, 0, 0)
        self.shadow_color_button = ColorButton(self.shadow_groupbox)
        self.shadow_color_button.setObjectName('shadow_color_button')
        self.shadow_layout.addWidget(self.shadow_color_button, 0, 1)
        # Shadow size
        self.shadow_size_label = QtWidgets.QLabel(self.shadow_groupbox)
        self.shadow_size_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.shadow_size_label.setObjectName('shadow_size_label')
        self.shadow_layout.addWidget(self.shadow_size_label, 1, 0)
        self.shadow_size_spinbox = QtWidgets.QSpinBox(self.shadow_groupbox)
        self.shadow_size_spinbox.setMaximum(9999)
        self.shadow_size_spinbox.setObjectName('shadow_size_spinbox')
        self.shadow_layout.addWidget(self.shadow_size_spinbox, 1, 1)
        # Fix the size
        self.resize_widgets()
        # Connect all the signals
        self.font_name_combobox.activated.connect(self._on_font_name_changed)
        self.font_color_button.colorChanged.connect(self._on_font_color_changed)
        self.style_bold_button.toggled.connect(self._on_style_bold_toggled)
        self.style_italic_button.toggled.connect(self._on_style_italic_toggled)
        self.font_size_spinbox.valueChanged.connect(self._on_font_size_changed)
        self.line_spacing_spinbox.valueChanged.connect(self._on_line_spacing_changed)
        self.outline_groupbox.toggled.connect(self._on_outline_toggled)
        self.outline_color_button.colorChanged.connect(self._on_outline_color_changed)
        self.outline_size_spinbox.valueChanged.connect(self._on_outline_size_changed)
        self.shadow_groupbox.toggled.connect(self._on_shadow_toggled)
        self.shadow_color_button.colorChanged.connect(self._on_shadow_color_changed)
        self.shadow_size_spinbox.valueChanged.connect(self._on_shadow_size_changed)
        # Translate everything
        self.retranslate_ui()

    def retranslate_ui(self):
        self.font_name_label.setText(translate('OpenLP.FontSelectWidget', 'Font:'))
        self.font_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.font_style_label.setText(translate('OpenLP.FontSelectWidget', 'Style:'))
        self.style_bold_button.setToolTip('{name} ({shortcut})'.format(
            name=translate('OpenLP.FontSelectWidget', 'Bold'),
            shortcut=QtGui.QKeySequence(QtGui.QKeySequence.Bold).toString()
        ))
        self.style_italic_button.setToolTip('{name} ({shortcut})'.format(
            name=translate('OpenLP.FontSelectWidget', 'Italic'),
            shortcut=QtGui.QKeySequence(QtGui.QKeySequence.Italic).toString()
        ))
        self.font_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))
        self.font_size_spinbox.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.line_spacing_label.setText(translate('OpenLP.FontSelectWidget', 'Line Spacing:'))
        self.outline_groupbox.setTitle(translate('OpenLP.FontSelectWidget', 'Outline'))
        self.outline_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.outline_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))
        self.shadow_groupbox.setTitle(translate('OpenLP.FontSelectWidget', 'Shadow'))
        self.shadow_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.shadow_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))

    def resizeEvent(self, event):
        """
        Override inherited resize method
        """
        super().resizeEvent(event)
        self.resize_widgets()

    def _on_font_name_changed(self, name):
        if isinstance(name, str):
            self.font_name_changed.emit(name)

    def _on_font_color_changed(self, color):
        self.font_color_changed.emit(color)

    def _on_style_bold_toggled(self, is_bold):
        self.is_bold_changed.emit(is_bold)

    def _on_style_italic_toggled(self, is_italic):
        self.is_italic_changed.emit(is_italic)

    def _on_font_size_changed(self, size):
        self.font_size_changed.emit(size)

    def _on_line_spacing_changed(self, spacing):
        self.line_spacing_changed.emit(spacing)

    def _on_outline_toggled(self, is_enabled):
        self.is_outline_enabled_changed.emit(is_enabled)

    def _on_outline_color_changed(self, color):
        self.outline_color_changed.emit(color)

    def _on_outline_size_changed(self, size):
        self.outline_size_changed.emit(size)

    def _on_shadow_toggled(self, is_enabled):
        self.is_shadow_enabled_changed.emit(is_enabled)

    def _on_shadow_color_changed(self, color):
        self.shadow_color_changed.emit(color)

    def _on_shadow_size_changed(self, size):
        self.shadow_size_changed.emit(size)

    def resize_widgets(self):
        """
        Resize all the widgets and set the column widths
        """
        width = self.geometry().width()
        margins = self.layout.contentsMargins()
        spacing = self.layout.horizontalSpacing()
        self._column_width = (width - margins.left() - margins.right() - (spacing * 3)) // 4
        for column_number in range(4):
            self.layout.setColumnMinimumWidth(column_number, self._column_width)

    def enable_features(self, *features):
        """
        Enable a feature
        """
        for feature_name in features:
            if feature_name not in self.feature_widgets.keys():
                raise KeyError('No such feature: {feature_name}'.format(feature_name=feature_name))
            for widget in self.feature_widgets[feature_name]:
                widget.show()

    def disable_features(self, *features):
        """
        Disable a feature
        """
        for feature_name in features:
            if feature_name not in self.feature_widgets.keys():
                raise KeyError('No such feature: {feature_name}'.format(feature_name=feature_name))
            for widget in self.feature_widgets[feature_name]:
                widget.hide()

    @property
    def font_name(self):
        return self.font_name_combobox.currentFont().family()

    @font_name.setter
    def font_name(self, font):
        self.font_name_combobox.setCurrentFont(QtGui.QFont(font))

    @property
    def font_color(self):
        return self.font_color_button.color

    @font_color.setter
    def font_color(self, color):
        self.font_color_button.color = color

    @property
    def is_bold(self):
        return self.style_bold_button.isChecked()

    @is_bold.setter
    def is_bold(self, is_bold):
        self.style_bold_button.setChecked(is_bold)

    @property
    def is_italic(self):
        return self.style_italic_button.isChecked()

    @is_italic.setter
    def is_italic(self, is_italic):
        self.style_italic_button.setChecked(is_italic)

    @property
    def font_size(self):
        return self.font_size_spinbox.value()

    @font_size.setter
    def font_size(self, size):
        self.font_size_spinbox.setValue(size)

    @property
    def line_spacing(self):
        return self.line_spacing_spinbox.value()

    @line_spacing.setter
    def line_spacing(self, line_spacing):
        self.line_spacing_spinbox.setValue(line_spacing)

    @property
    def is_outline_enabled(self):
        return self.outline_groupbox.isChecked()

    @is_outline_enabled.setter
    def is_outline_enabled(self, is_enabled):
        self.outline_groupbox.setChecked(is_enabled)

    @property
    def outline_color(self):
        return self.outline_color_button.color

    @outline_color.setter
    def outline_color(self, color):
        self.outline_color_button.color = color

    @property
    def outline_size(self):
        return self.outline_size_spinbox.value()

    @outline_size.setter
    def outline_size(self, size):
        self.outline_size_spinbox.setValue(size)

    @property
    def is_shadow_enabled(self):
        return self.shadow_groupbox.isChecked()

    @is_shadow_enabled.setter
    def is_shadow_enabled(self, is_enabled):
        self.shadow_groupbox.setChecked(is_enabled)

    @property
    def shadow_color(self):
        return self.shadow_color_button.color

    @shadow_color.setter
    def shadow_color(self, color):
        self.shadow_color_button.color = color

    @property
    def shadow_size(self):
        return self.shadow_size_spinbox.value()

    @shadow_size.setter
    def shadow_size(self, size):
        self.shadow_size_spinbox.setValue(size)
