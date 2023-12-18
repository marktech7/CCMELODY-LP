# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2023 OpenLP Developers                              #
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
The :mod:`~openlp.core.themes.editor_widgets.background` module contains the background widget used in the theme editor
"""
from PyQt5 import QtWidgets, QtCore

from openlp.core.common import get_images_filter
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.theme import BackgroundGradientType, BackgroundType
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import VIDEO_EXT
from openlp.core.widgets.buttons import ColorButton
from openlp.core.widgets.edits import PathEdit
from openlp.core.themes.editor_widgets import ThemeEditorWidget, create_label
from openlp.core.ui.media.vlcplayer import get_vlc


class BackgroundWidget(ThemeEditorWidget):
    """
    A background selection widget
    """
    Color = 'color'
    Gradient = 'gradient'
    Image = 'image'
    Video = 'video'
    Stream = 'stream'

    on_value_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_signals = False

    def setup_ui(self):
        """
        Set up the ui
        """
        # background type
        self.background_label = create_label(self)
        self.background_label.setObjectName('background_label')
        self.main_layout.addWidget(self.background_label)
        self.background_combo_box = QtWidgets.QComboBox(self)
        self.background_combo_box.addItems(['', '', '', '', '', ''])
        self.background_combo_box.setObjectName('background_combo_box')
        self.main_layout.addWidget(self.background_combo_box)
        # color
        self.color_label = create_label(self)
        self.color_label.setObjectName('color_label')
        self.main_layout.addWidget(self.color_label)
        self.color_button = ColorButton(self)
        self.color_button.setObjectName('color_button')
        self.main_layout.addWidget(self.color_button)
        self.color_widgets = [self.color_label, self.color_button]
        # gradient
        self.gradient_type_label = create_label(self)
        self.gradient_type_label.setObjectName('gradient_type_label')
        self.main_layout.addWidget(self.gradient_type_label)
        self.gradient_combo_box = QtWidgets.QComboBox(self)
        self.gradient_combo_box.setObjectName('gradient_combo_box')
        self.gradient_combo_box.addItems(['', '', '', '', ''])
        self.main_layout.addWidget(self.gradient_combo_box)
        self.gradient_start_label = create_label(self)
        self.gradient_start_label.setObjectName('gradient_start_label')
        self.main_layout.addWidget(self.gradient_start_label)
        self.gradient_start_button = ColorButton(self)
        self.gradient_start_button.setObjectName('gradient_start_button')
        self.main_layout.addWidget(self.gradient_start_button)
        self.gradient_end_label = create_label(self)
        self.gradient_end_label.setObjectName('gradient_end_label')
        self.main_layout.addWidget(self.gradient_end_label)
        self.gradient_end_button = ColorButton(self)
        self.gradient_end_button.setObjectName('gradient_end_button')
        self.main_layout.addWidget(self.gradient_end_button)
        self.gradient_widgets = [self.gradient_type_label, self.gradient_combo_box, self.gradient_start_label,
                                 self.gradient_start_button, self.gradient_end_label, self.gradient_end_button]
        # image
        self.image_label = create_label(self)
        self.image_label.setObjectName('image_label')
        self.main_layout.addWidget(self.image_label)
        self.image_path_edit = PathEdit(self, dialog_caption=translate('OpenLP.ThemeWizard', 'Select Image'),
                                        show_revert=False)
        self.main_layout.addWidget(self.image_path_edit)
        self.image_color_label = create_label(self)
        self.image_color_label.setObjectName('image_color_label')
        self.main_layout.addWidget(self.image_color_label)
        self.image_color_button = ColorButton(self)
        self.image_color_button.color = '#000000'
        self.image_color_button.setObjectName('image_color_button')
        self.main_layout.addWidget(self.image_color_button)
        self.image_widgets = [self.image_label, self.image_path_edit, self.image_color_label, self.image_color_button]
        # video
        self.video_label = create_label(self)
        self.video_label.setObjectName('video_label')
        self.main_layout.addWidget(self.video_label)
        self.video_path_edit = PathEdit(self, dialog_caption=translate('OpenLP.ThemeWizard', 'Select Video'),
                                        show_revert=False)
        self.main_layout.addWidget(self.video_path_edit)
        self.video_color_label = create_label(self)
        self.video_color_label.setObjectName('video_color_label')
        self.main_layout.addWidget(self.video_color_label)
        self.video_color_button = ColorButton(self)
        self.video_color_button.color = '#000000'
        self.video_color_button.setObjectName('video_color_button')
        self.main_layout.addWidget(self.video_color_button)
        self.video_widgets = [self.video_label, self.video_path_edit, self.video_color_label, self.video_color_button]
        # streams
        self.stream_label = create_label(self)
        self.stream_label.setObjectName('stream_label')
        self.main_layout.addWidget(self.stream_label)
        self.stream_main_layout = QtWidgets.QHBoxLayout()
        self.stream_lineedit = QtWidgets.QLineEdit(self)
        self.stream_lineedit.setObjectName('stream_lineedit')
        self.stream_lineedit.setReadOnly(True)
        self.stream_main_layout.addWidget(self.stream_lineedit)
        # button to open select device stream form
        self.device_stream_select_button = QtWidgets.QToolButton(self)
        self.device_stream_select_button.setObjectName('device_stream_select_button')
        self.device_stream_select_button.setIcon(UiIcons().device_stream)
        self.stream_main_layout.addWidget(self.device_stream_select_button)
        # button to open select network stream form
        self.network_stream_select_button = QtWidgets.QToolButton(self)
        self.network_stream_select_button.setObjectName('network_stream_select_button')
        self.network_stream_select_button.setIcon(UiIcons().network_stream)
        self.stream_main_layout.addWidget(self.network_stream_select_button)
        self.main_layout.addLayout(self.stream_main_layout)
        self.stream_color_label = create_label(self)
        self.stream_color_label.setObjectName('stream_color_label')
        self.main_layout.addWidget(self.stream_color_label)
        self.stream_color_button = ColorButton(self)
        self.stream_color_button.color = '#000000'
        self.stream_color_button.setObjectName('stream_color_button')
        self.main_layout.addWidget(self.stream_color_button)
        self.stream_widgets = [self.stream_label, self.stream_lineedit, self.device_stream_select_button,
                               self.network_stream_select_button, self.stream_color_label, self.stream_color_button]
        # Force everything up
        self.main_layout_spacer = QtWidgets.QSpacerItem(1, 1)
        self.main_layout.addItem(self.main_layout_spacer)
        # Force the first set of widgets to show
        self._on_background_type_index_changed(0, emit=False)

    def connect_signals(self):
        # Connect slots
        if not self.connected_signals:
            self.connected_signals = True
            self.background_combo_box.currentIndexChanged.connect(self._on_background_type_index_changed)
            self.device_stream_select_button.clicked.connect(self._on_device_stream_select_button_triggered)
            self.network_stream_select_button.clicked.connect(self._on_network_stream_select_button_triggered)
            self.gradient_combo_box.currentIndexChanged.connect(self._on_value_changed_emit)
            self.color_button.colorChanged.connect(self._on_value_changed_emit)
            self.image_color_button.colorChanged.connect(self._on_value_changed_emit)
            self.gradient_start_button.colorChanged.connect(self._on_value_changed_emit)
            self.gradient_end_button.colorChanged.connect(self._on_value_changed_emit)
            self.video_color_button.colorChanged.connect(self._on_value_changed_emit)
            self.stream_color_button.colorChanged.connect(self._on_value_changed_emit)
            self.stream_lineedit.textChanged.connect(self._on_value_changed_emit)
            self.image_path_edit.pathChanged.connect(self._on_value_changed_emit)
            self.video_path_edit.pathChanged.connect(self._on_value_changed_emit)
            # Force the first set of widgets to show
            # Running after signal connect to ensure it's shown
            self._on_background_type_index_changed(self.background_combo_box.currentIndex(), emit=False)

    def disconnect_signals(self):
        self.connected_signals = False
        self.background_combo_box.currentIndexChanged.disconnect(self._on_background_type_index_changed)
        self.device_stream_select_button.clicked.disconnect(self._on_device_stream_select_button_triggered)
        self.network_stream_select_button.clicked.disconnect(self._on_network_stream_select_button_triggered)
        self.gradient_combo_box.currentIndexChanged.disconnect(self._on_value_changed_emit)
        self.color_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.image_color_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.gradient_start_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.gradient_end_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.video_color_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.stream_color_button.colorChanged.disconnect(self._on_value_changed_emit)
        self.stream_lineedit.textChanged.disconnect(self._on_value_changed_emit)
        self.image_path_edit.pathChanged.disconnect(self._on_value_changed_emit)
        self.video_path_edit.pathChanged.disconnect(self._on_value_changed_emit)

    def retranslate_ui(self):
        """
        Translate the text elements of the widget
        """
        self.background_label.setText(translate('OpenLP.ThemeWizard', 'Background type:'))
        self.background_combo_box.setItemText(BackgroundType.Solid, translate('OpenLP.ThemeWizard', 'Solid color'))
        self.background_combo_box.setItemText(BackgroundType.Gradient, translate('OpenLP.ThemeWizard', 'Gradient'))
        self.background_combo_box.setItemText(BackgroundType.Image, UiStrings().Image)
        self.background_combo_box.setItemText(BackgroundType.Video, UiStrings().Video)
        self.background_combo_box.setItemText(BackgroundType.Transparent,
                                              translate('OpenLP.ThemeWizard', 'Transparent'))
        self.background_combo_box.setItemText(BackgroundType.Stream,
                                              translate('OpenLP.ThemeWizard', 'Live stream'))
        self.color_label.setText(translate('OpenLP.ThemeWizard', 'Color:'))
        self.gradient_start_label.setText(translate('OpenLP.ThemeWizard', 'Starting color:'))
        self.gradient_end_label.setText(translate('OpenLP.ThemeWizard', 'Ending color:'))
        self.gradient_type_label.setText(translate('OpenLP.ThemeWizard', 'Gradient:'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Horizontal,
                                            translate('OpenLP.ThemeWizard', 'Horizontal'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Vertical,
                                            translate('OpenLP.ThemeWizard', 'Vertical'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.Circular,
                                            translate('OpenLP.ThemeWizard', 'Circular'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.LeftTop,
                                            translate('OpenLP.ThemeWizard', 'Top Left - Bottom Right'))
        self.gradient_combo_box.setItemText(BackgroundGradientType.LeftBottom,
                                            translate('OpenLP.ThemeWizard', 'Bottom Left - Top Right'))
        self.image_color_label.setText(translate('OpenLP.ThemeWizard', 'Background color:'))
        self.image_label.setText('{text}:'.format(text=UiStrings().Image))
        self.video_color_label.setText(translate('OpenLP.ThemeWizard', 'Background color:'))
        self.video_label.setText('{text}:'.format(text=UiStrings().Video))
        self.stream_color_label.setText(translate('OpenLP.ThemeWizard', 'Background color:'))
        self.stream_label.setText('{text}:'.format(text=UiStrings().LiveStream))
        self.image_path_edit.filters = \
            '{name};;{text} (*)'.format(name=get_images_filter(), text=UiStrings().AllFiles)
        visible_formats = '({name})'.format(name='; '.join(VIDEO_EXT))
        actual_formats = '({name})'.format(name=' '.join(VIDEO_EXT))
        video_filter = '{trans} {visible} {actual}'.format(trans=translate('OpenLP', 'Video Files'),
                                                           visible=visible_formats, actual=actual_formats)
        self.video_path_edit.filters = '{video};;{ui} (*)'.format(video=video_filter, ui=UiStrings().AllFiles)

    def _on_background_type_index_changed(self, index, emit=True):
        """
        Hide and show widgets based on index
        """
        widget_sets = [self.color_widgets, self.gradient_widgets, self.image_widgets, [], self.video_widgets,
                       self.stream_widgets]
        for widgets in widget_sets:
            for widget in widgets:
                widget.hide()
        if index < len(widget_sets):
            for widget in widget_sets[index]:
                widget.show()
        if emit:
            self._on_value_changed_emit()

    def _on_device_stream_select_button_triggered(self):
        """
        Open the Stream selection form.
        """
        if get_vlc():
            # Only import this form if VLC is available.
            from openlp.plugins.media.forms.streamselectorform import StreamSelectorForm

            stream_selector_form = StreamSelectorForm(self, self.set_stream, True)
            # prefill in the form any device stream already defined
            if self.stream_lineedit.text() and self.stream_lineedit.text().startswith('devicestream'):
                stream_selector_form.set_mrl(self.stream_lineedit.text())
            stream_selector_form.exec()
            del stream_selector_form
            self._on_value_changed_emit()
        else:
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'VLC is not available'),
                                       translate('MediaPlugin.MediaItem', 'Device streaming support requires VLC.'))

    def _on_network_stream_select_button_triggered(self):
        """
        Open the Stream selection form.
        """
        if get_vlc():
            # Only import this form is VLC is available
            from openlp.plugins.media.forms.networkstreamselectorform import NetworkStreamSelectorForm

            stream_selector_form = NetworkStreamSelectorForm(self, self.set_stream, True)
            # prefill in the form any network stream already defined
            if self.stream_lineedit.text() and self.stream_lineedit.text().startswith('networkstream'):
                stream_selector_form.set_mrl(self.stream_lineedit.text())
            stream_selector_form.exec()
            del stream_selector_form
            self._on_value_changed_emit()
        else:
            critical_error_message_box(translate('MediaPlugin.MediaItem', 'VLC is not available'),
                                       translate('MediaPlugin.MediaItem', 'Network streaming support requires VLC.'))

    def set_stream(self, stream_str):
        """
        callback method used to get the stream mrl and options
        """
        self.stream_lineedit.setText(stream_str)
        self._on_value_changed_emit()

    @property
    def background_type(self):
        return BackgroundType.to_string(self.background_combo_box.currentIndex())

    @background_type.setter
    def background_type(self, value):
        if isinstance(value, str):
            self.background_combo_box.setCurrentIndex(BackgroundType.from_string(value))
        elif isinstance(value, int):
            self.background_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('background_type must either be a string or an int')

    @property
    def color(self):
        return self.color_button.color

    @color.setter
    def color(self, value):
        self.color_button.color = value

    @property
    def gradient_type(self):
        return BackgroundGradientType.to_string(self.gradient_combo_box.currentIndex())

    @gradient_type.setter
    def gradient_type(self, value):
        if isinstance(value, str):
            self.gradient_combo_box.setCurrentIndex(BackgroundGradientType.from_string(value))
        elif isinstance(value, int):
            self.gradient_combo_box.setCurrentIndex(value)
        else:
            raise TypeError('gradient_type must either be a string or an int')

    @property
    def gradient_start(self):
        return self.gradient_start_button.color

    @gradient_start.setter
    def gradient_start(self, value):
        self.gradient_start_button.color = value

    @property
    def gradient_end(self):
        return self.gradient_end_button.color

    @gradient_end.setter
    def gradient_end(self, value):
        self.gradient_end_button.color = value

    @property
    def image_color(self):
        return self.image_color_button.color

    @image_color.setter
    def image_color(self, value):
        self.image_color_button.color = value

    @property
    def image_path(self):
        return self.image_path_edit.path

    @image_path.setter
    def image_path(self, value):
        self.image_path_edit.path = value

    @property
    def video_color(self):
        return self.video_color_button.color

    @video_color.setter
    def video_color(self, value):
        self.video_color_button.color = value

    @property
    def video_path(self):
        return self.video_path_edit.path

    @video_path.setter
    def video_path(self, value):
        self.video_path_edit.path = value

    @property
    def stream_color(self):
        return self.stream_color_button.color

    @stream_color.setter
    def stream_color(self, value):
        self.stream_color_button.color = value

    @property
    def stream_mrl(self):
        return self.stream_lineedit.text()

    @stream_mrl.setter
    def stream_mrl(self, value):
        self.stream_lineedit.setText(value)

    def _on_value_changed_emit(self):
        self.on_value_changed.emit()
