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
The Theme Editor Form
"""
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import is_not_image_file
from openlp.core.common.enum import ServiceItemType
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.lib.theme import BackgroundType
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.themes.themeeditordialog import Ui_ThemeEditorDialog
from openlp.core.ui.themelayoutform import ThemeLayoutForm


log = logging.getLogger(__name__)


class ThemeEditorForm(QtWidgets.QDialog, Ui_ThemeEditorDialog, RegistryProperties):
    """
    This is the Theme Editor Wizard, which allows easy creation and editing of
    OpenLP themes.
    """
    log.info('ThemeEditorForm loaded')

    def __init__(self, parent):
        """
        Instantiate the editor, and run any extra setup we need to.
        """
        super(ThemeEditorForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                        QtCore.Qt.WindowCloseButtonHint)
        self._setup()

    def _setup(self):
        self.has_changes = False
        self.theme = None
        self.can_update_theme = True
        self.temp_background_filename = None
        self.display_aspect_ratio = 16 / 9
        self.setup_ui(self)
        self.preview_area.resizeEvent = self._preview_area_resize_event
    
    def connect_events(self):
        self.background_widget.on_value_changed.connect(self.do_update)
        self.alignment_widget.on_value_changed.connect(self.do_update)
        self.main_area_widget.on_value_changed.connect(self.do_update)
        self.footer_area_widget.on_value_changed.connect(self.do_update)
        self.transition_widget.on_value_changed.connect(self.do_update)
        self.area_position_widget.on_value_changed.connect(self.do_update)
        self.preview_area_layout.resize.connect(self._update_preview_box_scale)
        self.background_widget.connect_signals()
        self.alignment_widget.connect_signals()
        self.main_area_widget.connect_signals()
        self.footer_area_widget.connect_signals()
        self.transition_widget.connect_signals()
        self.area_position_widget.connect_signals()
    
    def disconnect_events(self):
        self.background_widget.disconnect_signals()
        self.alignment_widget.disconnect_signals()
        self.main_area_widget.disconnect_signals()
        self.footer_area_widget.disconnect_signals()
        self.transition_widget.disconnect_signals()
        self.area_position_widget.disconnect_signals()
        self.background_widget.on_value_changed.disconnect(self.do_update)
        self.alignment_widget.on_value_changed.disconnect(self.do_update)
        self.main_area_widget.on_value_changed.disconnect(self.do_update)
        self.footer_area_widget.on_value_changed.disconnect(self.do_update)
        self.transition_widget.on_value_changed.disconnect(self.do_update)
        self.area_position_widget.on_value_changed.disconnect(self.do_update)
        self.preview_area_layout.resize.disconnect(self._update_preview_box_scale)

    def provide_help(self):
        """
        Provide help within the editor by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/themes.html"))

    def _preview_area_resize_event(self, event=None):
        """
        Rescale the theme preview thumbnail on resize events.
        """
        if not event:
            event = QtGui.QResizeEvent(self.size(), self.size())
        QtWidgets.QWidget.resizeEvent(self.preview_area, event)
        self.update_aspect_ratio()

    def update_aspect_ratio(self):
        try:
            display_aspect_ratio = self.renderer.width() / self.renderer.height()
        except ZeroDivisionError:
            display_aspect_ratio = 1

        if display_aspect_ratio != self.display_aspect_ratio:
            self.display_aspect_ratio = display_aspect_ratio
            # Make sure we don't resize before the widgets are actually created
            if hasattr(self, 'preview_area_layout'):
                self.preview_area_layout.set_aspect_ratio(self.display_aspect_ratio)

    def _update_preview_box_scale(self):
        self.preview_box.set_scale(float(self.preview_box.width()) / self.renderer.width())
        self.preview_box.reload_theme()

    def set_defaults(self):
        """
        Set up display at start of theme edit.
        """
        self.set_background_widget_values()
        self.set_main_area_widget_values()
        self.set_footer_area_widget_values()
        self.set_alignment_widget_values()
        self.set_transition_widget_values()
        self.set_position_widget_values()

    def set_background_widget_values(self):
        """
        Handle the display and state of the Background widget.
        """
        self.background_widget.background_type = self.theme.background_type
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            self.background_widget.color = self.theme.background_color
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Gradient):
            self.background_widget.gradient_start = self.theme.background_start_color
            self.background_widget.gradient_end = self.theme.background_end_color
            self.background_widget.gradient_type = self.theme.background_direction
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.background_widget.image_color = self.theme.background_border_color
            if self.theme.background_source and self.theme.background_source.exists():
                self.background_widget.image_path = self.theme.background_source
            else:
                self.background_widget.image_path = self.theme.background_filename
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Video):
            self.background_widget.video_color = self.theme.background_border_color
            if self.theme.background_source and self.theme.background_source.exists():
                self.background_widget.video_path = self.theme.background_source
            else:
                self.background_widget.video_path = self.theme.background_filename
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Stream):
            self.background_widget.stream_color = self.theme.background_border_color
            self.background_widget.stream_mrl = self.theme.background_source

    def set_main_area_widget_values(self):
        """
        Handle the display and state of the Main Area widget.
        """
        self.main_area_widget.font_name = self.theme.font_main_name
        self.main_area_widget.font_color = self.theme.font_main_color
        self.main_area_widget.font_size = self.theme.font_main_size
        self.main_area_widget.line_spacing = self.theme.font_main_line_adjustment
        self.main_area_widget.is_outline_enabled = self.theme.font_main_outline
        self.main_area_widget.outline_color = self.theme.font_main_outline_color
        self.main_area_widget.outline_size = self.theme.font_main_outline_size
        self.main_area_widget.is_shadow_enabled = self.theme.font_main_shadow
        self.main_area_widget.shadow_color = self.theme.font_main_shadow_color
        self.main_area_widget.shadow_size = self.theme.font_main_shadow_size
        self.main_area_widget.is_bold = self.theme.font_main_bold
        self.main_area_widget.is_italic = self.theme.font_main_italics

    def set_footer_area_widget_values(self):
        """
        Handle the display and state of the Footer Area widget.
        """
        self.footer_area_widget.font_name = self.theme.font_footer_name
        self.footer_area_widget.font_color = self.theme.font_footer_color
        self.footer_area_widget.is_bold = self.theme.font_footer_bold
        self.footer_area_widget.is_italic = self.theme.font_footer_italics
        self.footer_area_widget.font_size = self.theme.font_footer_size

    def set_position_widget_values(self):
        """
        Handle the display and state of the _position widget.
        """
        # Main Area
        self.area_position_widget.use_main_default_location = not self.theme.font_main_override
        self.area_position_widget.main_x = int(self.theme.font_main_x)
        self.area_position_widget.main_y = int(self.theme.font_main_y)
        self.area_position_widget.main_height = int(self.theme.font_main_height)
        self.area_position_widget.main_width = int(self.theme.font_main_width)
        # Footer
        self.area_position_widget.use_footer_default_location = not self.theme.font_footer_override
        self.area_position_widget.footer_x = int(self.theme.font_footer_x)
        self.area_position_widget.footer_y = int(self.theme.font_footer_y)
        self.area_position_widget.footer_height = int(self.theme.font_footer_height)
        self.area_position_widget.footer_width = int(self.theme.font_footer_width)

    def set_alignment_widget_values(self):
        """
        Handle the display and state of the Alignments widget.
        """
        self.alignment_widget.horizontal_align = self.theme.display_horizontal_align
        self.alignment_widget.vertical_align = self.theme.display_vertical_align

    def set_transition_widget_values(self):
        """
        Handle the display and state of the Alignments widget.
        """
        self.transition_widget.is_transition_enabled = self.theme.display_slide_transition
        self.transition_widget.transition_type = self.theme.display_slide_transition_type
        self.transition_widget.transition_speed = self.theme.display_slide_transition_speed
        self.transition_widget.transition_direction = self.theme.display_slide_transition_direction
        self.transition_widget.is_transition_reverse_enabled = self.theme.display_slide_transition_reverse

    def do_update(self, mark_as_changed = True):
        if mark_as_changed:
            self.has_changes = True
        self.update_theme()
        self.preview_box.clear_slides()
        self.preview_box.show()
        self.preview_box.generate_preview(self.theme, False, False, False)

    def update_theme(self):
        """
        Update the theme object from the UI for fields not already updated
        when the are changed.
        """
        if not self.can_update_theme:
            return
        log.debug('update_theme')
        # background widget
        self.theme.background_type = self.background_widget.background_type
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            self.theme.background_color = self.background_widget.color
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Gradient):
            self.theme.background_direction = self.background_widget.gradient_type
            self.theme.background_start_color = self.background_widget.gradient_start
            self.theme.background_end_color = self.background_widget.gradient_end
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.theme.background_border_color = self.background_widget.image_color
            self.theme.background_source = self.background_widget.image_path
            self.theme.background_filename = self.background_widget.image_path
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Video):
            self.theme.background_border_color = self.background_widget.video_color
            self.theme.background_source = self.background_widget.video_path
            self.theme.background_filename = self.background_widget.video_path
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Stream):
            self.theme.background_border_color = self.background_widget.stream_color
            self.theme.background_source = self.background_widget.stream_mrl
            self.theme.background_filename = self.background_widget.stream_mrl
        # main font widget
        self.theme.font_main_name = self.main_area_widget.font_name
        self.theme.font_main_color = self.main_area_widget.font_color
        self.theme.font_main_size = self.main_area_widget.font_size
        self.theme.font_main_line_adjustment = self.main_area_widget.line_spacing
        self.theme.font_main_outline = self.main_area_widget.is_outline_enabled
        self.theme.font_main_outline_color = self.main_area_widget.outline_color
        self.theme.font_main_outline_size = self.main_area_widget.outline_size
        self.theme.font_main_shadow = self.main_area_widget.is_shadow_enabled
        self.theme.font_main_shadow_size = self.main_area_widget.shadow_size
        self.theme.font_main_shadow_color = self.main_area_widget.shadow_color
        self.theme.font_main_bold = self.main_area_widget.is_bold
        self.theme.font_main_italics = self.main_area_widget.is_italic
        # footer font widget
        self.theme.font_footer_name = self.footer_area_widget.font_name
        self.theme.font_footer_color = self.footer_area_widget.font_color
        self.theme.font_footer_size = self.footer_area_widget.font_size
        self.theme.font_footer_bold = self.footer_area_widget.is_bold
        self.theme.font_footer_italics = self.footer_area_widget.is_italic
        # position widget (main)
        self.theme.font_main_override = not self.area_position_widget.use_main_default_location
        if self.theme.font_main_override:
            self.theme.font_main_x = self.area_position_widget.main_x
            self.theme.font_main_y = self.area_position_widget.main_y
            self.theme.font_main_height = self.area_position_widget.main_height
            self.theme.font_main_width = self.area_position_widget.main_width
        else:
            self.theme.set_default_header()
        # position widget (footer)
        self.theme.font_footer_override = not self.area_position_widget.use_footer_default_location
        if self.theme.font_footer_override:
            self.theme.font_footer_x = self.area_position_widget.footer_x
            self.theme.font_footer_y = self.area_position_widget.footer_y
            self.theme.font_footer_height = self.area_position_widget.footer_height
            self.theme.font_footer_width = self.area_position_widget.footer_width
        else:
            self.theme.set_default_footer()
        # alignment widget
        self.theme.display_horizontal_align = self.alignment_widget.horizontal_align
        self.theme.display_vertical_align = self.alignment_widget.vertical_align
        # transition widget
        self.theme.display_slide_transition = self.transition_widget.is_transition_enabled
        self.theme.display_slide_transition_type = self.transition_widget.transition_type
        self.theme.display_slide_transition_speed = self.transition_widget.transition_speed
        self.theme.display_slide_transition_direction = self.transition_widget.transition_direction
        self.theme.display_slide_transition_reverse = self.transition_widget.is_transition_reverse_enabled

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # Avoiding dialog accept when pressing Enter on input fields
        if event.key() != QtCore.Qt.Key.Key_Return:
            super().keyPressEvent(event)

    def reject(self):
        """
        Warns user when trying to close with unsaved changes
        """
        if self.has_changes:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                            translate('OpenLP.ThemeEditor', 'Unsaved Changes'),
                                            translate('OpenLP.ThemeEditor', 'Any changes made in this theme will be lost.'
                                                                            ' Are you sure you want to cancel?'),
                                            QtWidgets.QMessageBox.StandardButtons(QtWidgets.QMessageBox.Yes |
                                                                                    QtWidgets.QMessageBox.No),
                                            self)
            if msg_box.exec() != QtWidgets.QMessageBox.Yes:
                return
        self.unload()
        return super().reject()

    def accept(self):
        """
        Lets save the theme as Finish has been triggered
        """
        self.preview_box.set_theme(self.theme, service_item_type=ServiceItemType.Text)
        # Save the theme name
        self.theme.theme_name = self.theme_name_edit.text()
        if not self.theme.theme_name:
            critical_error_message_box(
                translate('OpenLP.ThemeWizard', 'Theme Name Missing'),
                translate('OpenLP.ThemeWizard', 'There is no name for this theme. Please enter one.'))
            return
        if self.theme.theme_name == '-1' or self.theme.theme_name == 'None':
            critical_error_message_box(
                translate('OpenLP.ThemeWizard', 'Theme Name Invalid'),
                translate('OpenLP.ThemeWizard', 'Invalid theme name. Please enter one.'))
            return
        self.setDisabled(True)
        destination_path = None
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Image) or \
                self.theme.background_type == BackgroundType.to_string(BackgroundType.Video):
            file_name = self.theme.background_filename.name
            destination_path = self.path / self.theme.theme_name / file_name
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Stream):
            destination_path = self.theme.background_source
        if not self.edit_mode and not self.theme_manager.check_if_theme_exists(self.theme.theme_name):
            return
        # Set the theme background to the cache location
        self.theme.background_filename = destination_path
        self.theme_manager.save_theme(self.theme)
        self.theme_manager.save_preview(self.theme.theme_name, self.preview_box.save_screenshot())
        self.unload()
        return super().accept()

    def exec(self, edit=False):
        """
        Run the editor.
        """
        log.debug('Editing theme {name}'.format(name=self.theme.theme_name))
        self.temp_background_filename = self.theme.background_source
        self.can_update_theme = False
        self.set_defaults()
        self.can_update_theme = True
        self.edit_mode = edit
        if edit:
            self.setWindowTitle(translate('OpenLP.ThemeWizard', 'Edit Theme - {name}'
                                          ).format(name=self.theme.theme_name))
            self.theme_name_edit.setVisible(False)
            self.theme_name_label.setVisible(False)
            self.theme_name_edit.setText(self.theme.theme_name)
        else:
            self.setWindowTitle(UiStrings().NewTheme)
            self.theme_name_edit.setVisible(True)
            self.theme_name_label.setVisible(True)
            self.theme_name_edit.setText(None)
        self.has_changes = False
        self.setDisabled(False)
        return super().exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.connect_events()
        self.do_update(False)

    def unload(self):
        self.disconnect_events()
        self.has_changes = False
        self.preview_box.hide()
