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


from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.ui.icons import UiIcons


class Ui_StreamSelector(object):
    def setup_ui(self, stream_selector):
        stream_selector.setObjectName('stream_selector')
        #stream_selector.resize(554, 654)
        self.combobox_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                          QtWidgets.QSizePolicy.Fixed)
        stream_selector.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.main_layout = QtWidgets.QGridLayout(stream_selector)
        self.main_layout.setSpacing(8)
        self.main_layout.setObjectName('main_layout')
        
        # Stream name
        self.stream_name_label = QtWidgets.QLabel(stream_selector)
        self.stream_name_label.setObjectName('stream_name_label')
        self.main_layout.addWidget(self.stream_name_label, 0, 0, 1, 1)
        self.stream_name_edit = QtWidgets.QLineEdit(stream_selector)
        self.stream_name_edit.setObjectName('stream_name_edit')
        self.main_layout.addWidget(self.stream_name_edit, 0, 1, 1, 3)
        # Devices radio button
        self.device_stream_radio_button = QtWidgets.QRadioButton(stream_selector)
        self.device_stream_radio_button.setObjectName('device_stream_radio_button')
        self.main_layout.addWidget(self.device_stream_radio_button, 1, 0, 1, 4)
        # Video devices
        self.video_devices_label = QtWidgets.QLabel(stream_selector)
        self.video_devices_label.setObjectName('video_devices_label')
        self.main_layout.addWidget(self.video_devices_label, 2, 1, 1, 1)
        self.video_devices_combo_box = QtWidgets.QComboBox(stream_selector)
        self.video_devices_combo_box.addItems([''])
        self.video_devices_combo_box.setObjectName('video_devices_combo_box')
        self.main_layout.addWidget(self.video_devices_combo_box, 2, 2, 1, 2)
        # Audio devices
        self.audio_devices_label = QtWidgets.QLabel(stream_selector)
        self.audio_devices_label.setObjectName('audio_devices_label')
        self.main_layout.addWidget(self.audio_devices_label, 3, 1, 1, 1)
        self.audio_devices_combo_box = QtWidgets.QComboBox(stream_selector)
        self.audio_devices_combo_box.addItems([''])
        self.audio_devices_combo_box.setObjectName('audio_devices_combo_box')
        self.main_layout.addWidget(self.audio_devices_combo_box, 3, 2, 1, 2)
        # VLC param
        self.vlc_param_label = QtWidgets.QLabel(stream_selector)
        self.vlc_param_label.setObjectName('vlc_param_label')
        self.main_layout.addWidget(self.vlc_param_label, 4, 1, 1, 1)
        self.vlc_param_edit = QtWidgets.QLineEdit(stream_selector)
        self.vlc_param_edit.setObjectName('vlc_param_edit')
        self.main_layout.addWidget(self.vlc_param_edit, 4, 2, 1, 2)
        # Network radio buttin
        self.network_stream_radio_button = QtWidgets.QRadioButton(stream_selector)
        self.network_stream_radio_button.setObjectName('network_stream_radio_button')
        self.main_layout.addWidget(self.network_stream_radio_button, 5, 0, 1, 4)
        # Network mrl
        self.network_mrl_label = QtWidgets.QLabel(stream_selector)
        self.network_mrl_label.setObjectName('network_mrl_label')
        self.main_layout.addWidget(self.network_mrl_label, 6, 1, 1, 1)
        self.network_mrl_combo_box = QtWidgets.QComboBox(stream_selector)
        self.network_mrl_combo_box.addItems([''])
        self.network_mrl_combo_box.setEditable(True)
        self.network_mrl_combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertAtTop)
        self.network_mrl_combo_box.setObjectName('network_mrl_combo_box')
        self.main_layout.addWidget(self.network_mrl_combo_box, 6, 2, 1, 2)

        # Insert texts
        self.retranslate_ui(stream_selector)

    def retranslate_ui(self, stream_selector):
        stream_selector.setWindowTitle(translate('MediaPlugin.StreamSelector', 'Select Input Stream'))
        self.stream_name_label.setText(translate('MediaPlugin.StreamSelector', 'Stream name:'))
        self.device_stream_radio_button.setText(translate('MediaPlugin.StreamSelector', 'Stream from device:'))
        self.network_stream_radio_button.setText(translate('MediaPlugin.StreamSelector', 'Stream from network:'))
        self.video_devices_label.setText(translate('MediaPlugin.StreamSelector', 'Video:'))
        self.audio_devices_label.setText(translate('MediaPlugin.StreamSelector', 'Audio:'))
        self.vlc_param_label.setText(translate('MediaPlugin.StreamSelector', 'VLC parameters:'))
        self.network_mrl_label.setText(translate('MediaPlugin.StreamSelector', 'Network MRL/URL:'))
