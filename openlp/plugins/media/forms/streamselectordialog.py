# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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

import glob
import re
from PyQt5 import QtCore, QtWidgets

from openlp.core.common import is_linux, is_macosx, is_win
from openlp.core.common.i18n import translate
from openlp.core.ui.icons import UiIcons

# Copied from VLC source code: modules/access/v4l2/v4l2.c
VIDEO_STANDARDS_VLC = [
    "", "ALL",
    # Pseudo standards
    "PAL", "PAL_BG", "PAL_DK",
    "NTSC",
    "SECAM", "SECAM_DK",
    "MTS", "525_60", "625_50",
    "ATSC",

    # Chroma-agnostic ITU standards (PAL/NTSC or PAL/SECAM)
    "B",              "G",               "H",               "L",
    "GH",             "DK",              "BG",              "MN",

    # Individual standards
    "PAL_B",          "PAL_B1",          "PAL_G",           "PAL_H",
    "PAL_I",          "PAL_D",           "PAL_D1",          "PAL_K",
    "PAL_M",          "PAL_N",           "PAL_Nc",          "PAL_60",
    "NTSC_M",         "NTSC_M_JP",       "NTSC_443",        "NTSC_M_KR",
    "SECAM_B",        "SECAM_D",         "SECAM_G",         "SECAM_H",
    "SECAM_K",        "SECAM_K1",        "SECAM_L",         "SECAM_LC",
    "ATSC_8_VSB",     "ATSC_16_VSB",
]
VIDEO_STANDARDS_USER = [
    "Undefined", "All",
    "PAL",            "PAL B/G",         "PAL D/K",
    "NTSC",
    "SECAM",          "SECAM D/K",
    "Multichannel television sound (MTS)",
    "525 lines / 60 Hz", "625 lines / 50 Hz",
    "ATSC",

    "PAL/SECAM B",    "PAL/SECAM G",     "PAL/SECAM H",     "PAL/SECAM L",
    "PAL/SECAM G/H",  "PAL/SECAM D/K",   "PAL/SECAM B/G",   "PAL/NTSC M/N",

    "PAL B",          "PAL B1",          "PAL G",           "PAL H",
    "PAL I",          "PAL D",           "PAL D1",          "PAL K",
    "PAL M",          "PAL N",           "PAL N Argentina", "PAL 60",
    "NTSC M",        "NTSC M Japan", "NTSC 443",  "NTSC M South Korea",
    "SECAM B",        "SECAM D",         "SECAM G",         "SECAM H",
    "SECAM K",        "SECAM K1",        "SECAM L",         "SECAM L/C",
    "ATSC 8-VSB",     "ATSC 16-VSB",
]

DIGITAL_TV_STANDARDS = ['DVB-T', 'DVB-C', 'DVB-S', 'DVB-S2', 'DVB-T2', 'ATSC', 'Clear QAM']

class CaptureModeWidget(QtWidgets.QWidget):
    """
    Simple widget containing a groupbox to hold devices and a groupbox for options
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('capture_mode_widget')
        self.capture_mode_widget_layout = QtWidgets.QVBoxLayout(self)
        self.setObjectName('capture_mode_widget_layout')
        self.device_group = QtWidgets.QGroupBox(self)
        self.device_group.setObjectName('device_group')
        self.device_group_layout = QtWidgets.QFormLayout(self.device_group)
        self.device_group_layout.setObjectName('device_group_layout')
        self.capture_mode_widget_layout.addWidget(self.device_group)
        self.options_group = QtWidgets.QGroupBox(self)
        self.options_group.setObjectName('options_group')
        self.options_group_layout = QtWidgets.QFormLayout(self.options_group)
        self.options_group_layout.setObjectName('options_group_layout')
        self.capture_mode_widget_layout.addWidget(self.options_group)

    def retranslate_ui(self):
        self.device_group.setTitle(translate('MediaPlugin.StreamSelector', 'Device Selection'))
        self.options_group.setTitle(translate('MediaPlugin.StreamSelector', 'Options'))

    def find_devices(self):
        pass


class CaptureVideoWidget(CaptureModeWidget):
    """
    Widget inherits groupboxes from CaptureModeWidget and inserts comboboxes for audio and video devices
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()
        # Video devices
        self.video_devices_label = QtWidgets.QLabel(self)
        self.video_devices_label.setObjectName('video_devices_label')
        self.video_devices_combo_box = QtWidgets.QComboBox(self)
        self.video_devices_combo_box.addItems([''])
        self.video_devices_combo_box.setObjectName('video_devices_combo_box')
        if is_linux():
            self.video_devices_combo_box.setEditable(True)
        self.device_group_layout.addRow(self.video_devices_label, self.video_devices_combo_box)
        # Audio devices
        self.audio_devices_label = QtWidgets.QLabel(self)
        self.audio_devices_label.setObjectName('audio_devices_label')
        self.audio_devices_combo_box = QtWidgets.QComboBox(self)
        self.audio_devices_combo_box.addItems([''])
        self.audio_devices_combo_box.setObjectName('audio_devices_combo_box')
        if is_linux():
            self.audio_devices_combo_box.setEditable(True)
        self.device_group_layout.addRow(self.audio_devices_label, self.audio_devices_combo_box)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.video_devices_label.setText(translate('MediaPlugin.StreamSelector', 'Video device name'))
        self.audio_devices_label.setText(translate('MediaPlugin.StreamSelector', 'Audio device name'))


class CaptureVideoLinuxWidget(CaptureVideoWidget):
    """
    Widget inherits groupboxes from CaptureVideoWidget and inserts widgets for linux
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()
        # Options
        self.video_std_label = QtWidgets.QLabel(self)
        self.video_std_label.setObjectName('video_std_label')
        self.video_std_combobox = QtWidgets.QComboBox(self)
        self.video_std_combobox.setObjectName('video_std_combobox')
        self.video_std_combobox.addItems(VIDEO_STANDARDS_USER)
        self.options_group_layout.addRow(self.video_std_label, self.video_std_combobox)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.video_std_label.setText(translate('MediaPlugin.StreamSelector', 'Video standard'))


class CaptureVideoLinuxV4L2Widget(CaptureVideoLinuxWidget):
    """
    Widget inherits groupboxes from CaptureVideoWidget and inserts widgets for linux
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def find_devices(self):
        """
        Insert devices for V4L2
        """
        video_devs = glob.glob('/dev/video*')
        self.video_devices_combo_box.addItems(video_devs)
        audio_devs = glob.glob('/dev/snd/pcmC*D*c')
        vlc_audio_devs = []
        for dev in audio_devs:
            vlc_dev = dev.replace('/dev/snd/pcmC', 'hw:')
            vlc_dev = re.sub(r'c$', '', vlc_dev).replace('D', ',')
            vlc_audio_devs.append(vlc_dev)
        self.audio_devices_combo_box.addItems(vlc_audio_devs)


class CaptureAnalogTVWidget(CaptureVideoLinuxV4L2Widget):
    """
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()
        # frequency
        self.freq_label = QtWidgets.QLabel(self)
        self.freq_label.setObjectName('freq_label')
        self.freq = QtWidgets.QSpinBox(self)
        self.freq.setAlignment(QtCore.Qt.AlignRight)
        self.freq.setSuffix(' kHz')
        self.freq.setSingleStep(1)
        self.freq.setMaximum(99999999) # Got no idea about this...
        self.options_group_layout.addRow(self.freq_label, self.freq)
        self.audio_devices_combo_box.clearEditText()

    def retranslate_ui(self):
        super().retranslate_ui()
        self.video_std_label.setText(translate('MediaPlugin.StreamSelector', 'Video standard'))
        self.freq_label.setText(translate('MediaPlugin.StreamSelector', 'Frequency'))


class CaptureDigitalTVWidget(CaptureModeWidget):
    """
    Widget inherits groupboxes from CaptureModeWidget and inserts widgets for digital TV
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()
        # Tuner card
        self.tuner_card_label = QtWidgets.QLabel(self)
        self.tuner_card_label.setObjectName('tuner_card_label')
        self.tuner_card = QtWidgets.QSpinBox(self)
        self.tuner_card.setObjectName('tuner_card')
        self.tuner_card.setAlignment(QtCore.Qt.AlignRight)
        if is_linux():
            self.tuner_card.setPrefix('/dev/dvb/adapter')
        self.device_group_layout.addRow(self.tuner_card_label, self.tuner_card)
        # Delivery system
        self.delivery_system_label = QtWidgets.QLabel(self)
        self.delivery_system_label.setObjectName('delivery_system_label')
        self.delivery_system_combo_box = QtWidgets.QComboBox(self)
        self.delivery_system_combo_box.addItems(DIGITAL_TV_STANDARDS)
        self.delivery_system_combo_box.setObjectName('delivery_system_combo_box')
        self.device_group_layout.addRow(self.delivery_system_label, self.delivery_system_combo_box)
        # Options
        # DVB frequency
        self.dvb_freq_label = QtWidgets.QLabel(self)
        self.dvb_freq_label.setObjectName('dvb_freq_label')
        self.dvb_freq = QtWidgets.QSpinBox(self)
        self.dvb_freq.setAlignment(QtCore.Qt.AlignRight)
        self.dvb_freq.setSuffix(' kHz')
        self.dvb_freq.setSingleStep(1000)
        self.dvb_freq.setMaximum(99999999) # Got no idea about this...
        # setSpinBoxFreq( dvbFreq  ); ?
        self.options_group_layout.addRow(self.dvb_freq_label, self.dvb_freq)
        # Bandwidth
        self.dvb_bandwidth_label = QtWidgets.QLabel(self)
        self.dvb_bandwidth_label.setObjectName('dvb_bandwidth_label')
        self.dvb_bandwidth_combo_box = QtWidgets.QComboBox(self)
        self.dvb_bandwidth_combo_box.addItems(['Automatic', '10 MHz', '8 MHz', '7 MHz', '6 MHz', '5 MHz', '1.712 MHz'])
        self.dvb_bandwidth_combo_box.setObjectName('dvb_bandwidth_combo_box')
        self.options_group_layout.addRow(self.dvb_bandwidth_label, self.dvb_bandwidth_combo_box)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.tuner_card_label.setText(translate('MediaPlugin.StreamSelector', 'Tuner card'))
        self.delivery_system_label.setText(translate('MediaPlugin.StreamSelector', 'Delivery system'))
        self.dvb_freq_label.setText(translate('MediaPlugin.StreamSelector', 'Transponder/multiplexer frequency'))
        self.dvb_bandwidth_label.setText(translate('MediaPlugin.StreamSelector', 'Bandwidth'))


class JackAudioKitWidget(CaptureModeWidget):
    """
    Widget for JACK Audio Connection Kit
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()
        # Selected ports
        self.ports_label = QtWidgets.QLabel(self)
        self.ports_label.setObjectName('ports_label')
        self.ports = QtWidgets.QLineEdit(self)
        self.ports.setText('.*')
        self.ports.setObjectName('ports')
        self.ports.setAlignment(QtCore.Qt.AlignRight)
        self.device_group_layout.addRow(self.ports_label, self.ports)
        # channels
        self.channels_label = QtWidgets.QLabel(self)
        self.channels_label.setObjectName('channels_label')
        self.channels = QtWidgets.QSpinBox(self)
        self.channels.setObjectName('channels')
        self.channels.setMaximum(255)
        self.channels.setValue(2)
        self.channels.setAlignment(QtCore.Qt.AlignRight)
        self.device_group_layout.addRow(self.channels_label, self.channels)
        # Options
        self.jack_pace = QtWidgets.QCheckBox(translate('MediaPlugin.StreamSelector', 'Use VLC pace'));
        self.jack_connect = QtWidgets.QCheckBox(translate('MediaPlugin.StreamSelector', 'Auto connection'));
        self.options_group_layout.addRow(self.jack_pace, self.jack_connect)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.ports_label.setText(translate('MediaPlugin.StreamSelector', 'Selected ports'))
        self.channels_label.setText(translate('MediaPlugin.StreamSelector', 'Channels'))


class MacInputWidget(CaptureVideoWidget):
    """
    Widget for macOS
https://github.com/videolan/vlc/blob/13e18f3182e2a7b425411ce70ed83161108c3d1f/modules/gui/macosx/windows/VLCOpenWindowController.m#L472
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def setup_ui(self):
        super().setup_ui()




class Ui_StreamSelector(object):
    def setup_ui(self, stream_selector):
        stream_selector.setObjectName('stream_selector')
        #stream_selector.resize(554, 654)
        self.combobox_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                          QtWidgets.QSizePolicy.Fixed)
        stream_selector.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.main_layout = QtWidgets.QVBoxLayout(stream_selector)
        #self.main_layout.setSpacing(8)
        self.main_layout.setObjectName('main_layout')
        
        self.top_widget = QtWidgets.QWidget(stream_selector)
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QtWidgets.QFormLayout(self.top_widget)
        self.top_layout.setObjectName('top_layout')
        # Stream name
        self.stream_name_label = QtWidgets.QLabel(self.top_widget)
        self.stream_name_label.setObjectName('stream_name_label')
        self.stream_name_edit = QtWidgets.QLineEdit(self.top_widget)
        self.stream_name_edit.setObjectName('stream_name_edit')
        self.top_layout.addRow(self.stream_name_label, self.stream_name_edit)
        # Mode combobox
        self.capture_mode_label = QtWidgets.QLabel(self.top_widget)
        self.capture_mode_label.setObjectName('capture_mode_label')
        self.capture_mode_combo_box = QtWidgets.QComboBox(self.top_widget)
        self.capture_mode_combo_box.setObjectName('capture_mode_combo_box')
        self.top_layout.addRow(self.capture_mode_label, self.capture_mode_combo_box)
        self.main_layout.addWidget(self.top_widget)
        # Stacked Layout for capture modes
        self.stacked_modes = QtWidgets.QWidget(stream_selector)
        self.stacked_modes.setObjectName('stacked_modes')
        self.stacked_modes_layout = QtWidgets.QStackedLayout(self.stacked_modes)
        self.stacked_modes_layout.setObjectName('stacked_modes_layout')
        # Widget for DirectShow - Windows only
        if is_win():
            self.direct_show_widget = CaptureVideoWidget(stream_selector)
            # Options
            self.direct_show_widget.video_size_label = QtWidgets.QLabel(self.direct_show_widget)
            self.direct_show_widget.video_size_label.setObjectName('video_size_label')
            self.direct_show_widget.video_size_lineedit = QtWidgets.QLineEdit(self.direct_show_widget)
            self.direct_show_widget.video_size_lineedit.setObjectName('video_size_lineedit')
            self.direct_show_widget.options_group_layout.addRow(self.direct_show_widget.video_size_label,
                                                                self.direct_show_widget.video_size_lineedit)
            self.stacked_modes_layout.addWidget(self.direct_show_widget)
            self.capture_mode_combo_box.addItem(translate('MediaPlugin.StreamSelector', 'DirectShow'));
        elif is_linux():
            # Widget for V4L2 - Linux only
            self.v4l2_widget = CaptureVideoLinuxV4L2Widget(stream_selector)
            self.stacked_modes_layout.addWidget(self.v4l2_widget)
            self.capture_mode_combo_box.addItem(translate('MediaPlugin.StreamSelector', 'Video Camera'));
            # Widget for analog TV - Linux only
            self.analog_tv_widget = CaptureAnalogTVWidget(stream_selector)
            self.stacked_modes_layout.addWidget(self.analog_tv_widget)
            self.capture_mode_combo_box.addItem(translate('MediaPlugin.StreamSelector', 'TV - analog'));
            # Widget for JACK - Linux only
            self.jack_widget = JackAudioKitWidget(stream_selector)
            self.stacked_modes_layout.addWidget(self.jack_widget)
            self.capture_mode_combo_box.addItem(translate('MediaPlugin.StreamSelector', 'JACK Audio Connection Kit'));
        # Digital TV - both linux and windows
        if is_win() or is_linux():
            self.digital_tv_widget = CaptureDigitalTVWidget(stream_selector)
            self.stacked_modes_layout.addWidget(self.digital_tv_widget)
            self.capture_mode_combo_box.addItem(translate('MediaPlugin.StreamSelector', 'TV - digital'));
        # Setup the stacked widgets
        self.main_layout.addWidget(self.stacked_modes)
        self.stacked_modes_layout.setCurrentIndex(0)
        for i in range(self.stacked_modes_layout.count()):
            self.stacked_modes_layout.widget(i).find_devices()
            self.stacked_modes_layout.widget(i).retranslate_ui()
        # translate
        self.retranslate_ui(stream_selector)
        # connect
        self.capture_mode_combo_box.currentIndexChanged.connect(self.on_capture_mode_combo_box)

    def retranslate_ui(self, stream_selector):
        stream_selector.setWindowTitle(translate('MediaPlugin.StreamSelector', 'Select Input Stream'))
        self.stream_name_label.setText(translate('MediaPlugin.StreamSelector', 'Stream name'))
        self.capture_mode_label.setText(translate('MediaPlugin.StreamSelector', 'Capture Mode'))
        if is_win():
            self.direct_show_widget.video_size_label.setText(translate('MediaPlugin.StreamSelector', 'Video size'))

    def on_capture_mode_combo_box(self):
        self.stacked_modes_layout.setCurrentIndex(self.capture_mode_combo_box.currentIndex())
