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
The Theme wizard
"""
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.common import get_images_filter, is_not_image_file
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.lib.theme import BackgroundGradientType, BackgroundType
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.media import VIDEO_EXT
from openlp.core.ui.themelayoutform import ThemeLayoutForm
from openlp.core.ui.themewizard import Ui_ThemeWizard


log = logging.getLogger(__name__)


class ThemeForm(QtWidgets.QWizard, Ui_ThemeWizard, RegistryProperties):
    """
    This is the Theme Import Wizard, which allows easy creation and editing of
    OpenLP themes.
    """
    log.info('ThemeWizardForm loaded')

    def __init__(self, parent):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        """
        super(ThemeForm, self).__init__(parent)
        self._setup()

    def _setup(self):
        """
        Set up the class. This method is mocked out by the tests.
        """
        self.setup_ui(self)
        self.registerFields()
        self.update_theme_allowed = True
        self.temp_background_filename = None
        self.theme_layout_form = ThemeLayoutForm(self)
        self.background_combo_box.currentIndexChanged.connect(self.on_background_combo_box_current_index_changed)
        self.gradient_combo_box.currentIndexChanged.connect(self.on_gradient_combo_box_current_index_changed)
        self.color_button.colorChanged.connect(self.on_color_changed)
        self.image_color_button.colorChanged.connect(self.on_image_color_changed)
        self.video_color_button.colorChanged.connect(self.on_video_color_changed)
        self.gradient_start_button.colorChanged.connect(self.on_gradient_start_color_changed)
        self.gradient_end_button.colorChanged.connect(self.on_gradient_end_color_changed)
        self.image_path_edit.filters = \
            '{name};;{text} (*)'.format(name=get_images_filter(), text=UiStrings().AllFiles)
        self.image_path_edit.pathChanged.connect(self.on_image_path_edit_path_changed)
        visible_formats = '(*.{name})'.format(name='; *.'.join(VIDEO_EXT))
        actual_formats = '(*.{name})'.format(name=' *.'.join(VIDEO_EXT))
        video_filter = '{trans} {visible} {actual}'.format(trans=translate('OpenLP', 'Video Files'),
                                                           visible=visible_formats, actual=actual_formats)
        self.video_path_edit.filters = '{video};;{ui} (*)'.format(video=video_filter, ui=UiStrings().AllFiles)
        self.video_path_edit.pathChanged.connect(self.on_video_path_edit_path_changed)
        self.main_color_button.colorChanged.connect(self.on_main_color_changed)
        self.outline_color_button.colorChanged.connect(self.on_outline_color_changed)
        self.shadow_color_button.colorChanged.connect(self.on_shadow_color_changed)
        self.outline_check_box.stateChanged.connect(self.on_outline_check_check_box_state_changed)
        self.shadow_check_box.stateChanged.connect(self.on_shadow_check_check_box_state_changed)
        self.footer_color_button.colorChanged.connect(self.on_footer_color_changed)
        self.customButtonClicked.connect(self.on_custom_1_button_clicked)
        self.main_position_check_box.stateChanged.connect(self.on_main_position_check_box_state_changed)
        self.footer_position_check_box.stateChanged.connect(self.on_footer_position_check_box_state_changed)
        self.currentIdChanged.connect(self.on_current_id_changed)
        Registry().register_function('theme_line_count', self.update_lines_text)
        self.main_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.line_spacing_spin_box.valueChanged.connect(self.calculate_lines)
        self.outline_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.shadow_size_spin_box.valueChanged.connect(self.calculate_lines)
        self.main_font_combo_box.activated.connect(self.calculate_lines)
        self.footer_font_combo_box.activated.connect(self.update_theme)
        self.footer_size_spin_box.valueChanged.connect(self.update_theme)

    def set_defaults(self):
        """
        Set up display at start of theme edit.
        """
        self.restart()
        self.set_background_page_values()
        self.set_main_area_page_values()
        self.set_footer_area_page_values()
        self.set_alignment_page_values()
        self.set_position_page_values()
        self.set_preview_page_values()

    def registerFields(self):
        """
        Map field names to screen names,
        """
        self.background_page.registerField('background_type', self.background_combo_box)
        self.background_page.registerField('color', self.color_button)
        self.background_page.registerField('gradient_start', self.gradient_start_button)
        self.background_page.registerField('gradient_end', self.gradient_end_button)
        self.background_page.registerField('background_image', self.image_path_edit,
                                           'path', self.image_path_edit.pathChanged)
        self.background_page.registerField('gradient', self.gradient_combo_box)
        self.main_area_page.registerField('main_color_button', self.main_color_button)
        self.main_area_page.registerField('main_size_spin_box', self.main_size_spin_box)
        self.main_area_page.registerField('line_spacing_spin_box', self.line_spacing_spin_box)
        self.main_area_page.registerField('outline_check_box', self.outline_check_box)
        self.main_area_page.registerField('outline_color_button', self.outline_color_button)
        self.main_area_page.registerField('outline_size_spin_box', self.outline_size_spin_box)
        self.main_area_page.registerField('shadow_check_box', self.shadow_check_box)
        self.main_area_page.registerField('main_bold_check_box', self.main_bold_check_box)
        self.main_area_page.registerField('main_italics_check_box', self.main_italics_check_box)
        self.main_area_page.registerField('shadow_color_button', self.shadow_color_button)
        self.main_area_page.registerField('shadow_size_spin_box', self.shadow_size_spin_box)
        self.main_area_page.registerField('footer_size_spin_box', self.footer_size_spin_box)
        self.area_position_page.registerField('main_position_x', self.main_x_spin_box)
        self.area_position_page.registerField('main_position_y', self.main_y_spin_box)
        self.area_position_page.registerField('main_position_width', self.main_width_spin_box)
        self.area_position_page.registerField('main_position_height', self.main_height_spin_box)
        self.area_position_page.registerField('footer_position_x', self.footer_x_spin_box)
        self.area_position_page.registerField('footer_position_y', self.footer_y_spin_box)
        self.area_position_page.registerField('footer_position_width', self.footer_width_spin_box)
        self.area_position_page.registerField('footer_position_height', self.footer_height_spin_box)
        self.background_page.registerField('horizontal', self.horizontal_combo_box)
        self.background_page.registerField('vertical', self.vertical_combo_box)
        self.background_page.registerField('slide_transition', self.transitions_check_box)
        self.background_page.registerField('name', self.theme_name_edit)

    def calculate_lines(self):
        """
        Calculate the number of lines on a page by rendering text
        """
        # Do not trigger on start up
        if self.currentPage() != self.welcome_page:
            self.update_theme()
            self.theme_manager.generate_image(self.theme, True)

    def update_lines_text(self, lines):
        """
        Updates the lines on a page on the wizard
        :param lines: then number of lines to be displayed
        """
        self.main_line_count_label.setText(
            translate('OpenLP.ThemeForm', '(approximately %d lines per slide)') % int(lines))

    def resizeEvent(self, event=None):
        """
        Rescale the theme preview thumbnail on resize events.
        """
        if not event:
            event = QtGui.QResizeEvent(self.size(), self.size())
        QtWidgets.QWizard.resizeEvent(self, event)
        try:
            self.display_aspect_ratio = self.renderer.width() / self.renderer.height()
        except ZeroDivisionError:
            self.display_aspect_ratio = 1
        # Make sure we don't resize before the widgets are actually created
        if hasattr(self, 'preview_area_layout'):
            self.preview_area_layout.set_aspect_ratio(self.display_aspect_ratio)
            self.preview_box.set_scale(float(self.preview_box.width()) / self.renderer.width())

    def validateCurrentPage(self):
        """
        Validate the current page
        """
        background_image = BackgroundType.to_string(BackgroundType.Image)
        if self.page(self.currentId()) == self.background_page and \
                self.theme.background_type == background_image and is_not_image_file(self.theme.background_filename):
            QtWidgets.QMessageBox.critical(self, translate('OpenLP.ThemeWizard', 'Background Image Empty'),
                                           translate('OpenLP.ThemeWizard', 'You have not selected a '
                                                     'background image. Please select one before continuing.'))
            return False
        else:
            return True

    def on_current_id_changed(self, page_id):
        """
        Detects Page changes and updates as appropriate.
        :param page_id: current page number
        """
        enabled = self.page(page_id) == self.area_position_page
        self.setOption(QtWidgets.QWizard.HaveCustomButton1, enabled)
        if self.page(page_id) == self.preview_page:
            self.update_theme()
            self.preview_box.set_theme(self.theme)
            self.preview_box.clear_slides()
            self.preview_box.set_scale(float(self.preview_box.width()) / self.renderer.width())
            try:
                self.display_aspect_ratio = self.renderer.width() / self.renderer.height()
            except ZeroDivisionError:
                self.display_aspect_ratio = 1
            self.preview_area_layout.set_aspect_ratio(self.display_aspect_ratio)
            self.resizeEvent()
            self.preview_box.show()
            self.preview_box.generate_preview(self.theme, False, False)

    def on_custom_1_button_clicked(self, number):
        """
        Generate layout preview and display the form.
        """
        self.update_theme()
        width = self.renderer.width()
        height = self.renderer.height()
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.white)
        paint = QtGui.QPainter(pixmap)
        paint.setPen(QtGui.QPen(QtCore.Qt.blue, 2))
        main_rect = QtCore.QRect(self.theme.font_main_x, self.theme.font_main_y,
                                 self.theme.font_main_width - 1, self.theme.font_main_height - 1)
        paint.drawRect(main_rect)
        paint.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        footer_rect = QtCore.QRect(self.theme.font_footer_x, self.theme.font_footer_y,
                                   self.theme.font_footer_width - 1, self.theme.font_footer_height - 1)
        paint.drawRect(footer_rect)
        paint.end()
        self.theme_layout_form.exec(pixmap)

    def on_outline_check_check_box_state_changed(self, state):
        """
        Change state as Outline check box changed
        """
        if self.update_theme_allowed:
            self.theme.font_main_outline = state == QtCore.Qt.Checked
            self.outline_color_button.setEnabled(self.theme.font_main_outline)
            self.outline_size_spin_box.setEnabled(self.theme.font_main_outline)
            self.calculate_lines()

    def on_shadow_check_check_box_state_changed(self, state):
        """
        Change state as Shadow check box changed
        """
        if self.update_theme_allowed:
            if state == QtCore.Qt.Checked:
                self.theme.font_main_shadow = True
            else:
                self.theme.font_main_shadow = False
            self.shadow_color_button.setEnabled(self.theme.font_main_shadow)
            self.shadow_size_spin_box.setEnabled(self.theme.font_main_shadow)
            self.calculate_lines()

    def on_main_position_check_box_state_changed(self, value):
        """
        Change state as Main Area _position check box changed
        NOTE the font_main_override is the inverse of the check box value
        """
        if self.update_theme_allowed:
            self.theme.font_main_override = (value != QtCore.Qt.Checked)

    def on_footer_position_check_box_state_changed(self, value):
        """
        Change state as Footer Area _position check box changed
        NOTE the font_footer_override is the inverse of the check box value
        """
        if self.update_theme_allowed:
            self.theme.font_footer_override = (value != QtCore.Qt.Checked)

    def exec(self, edit=False):
        """
        Run the wizard.
        """
        log.debug('Editing theme {name}'.format(name=self.theme.theme_name))
        self.temp_background_filename = self.theme.background_source
        self.update_theme_allowed = False
        self.set_defaults()
        self.update_theme_allowed = True
        self.theme_name_label.setVisible(not edit)
        self.theme_name_edit.setVisible(not edit)
        self.edit_mode = edit
        if edit:
            self.setWindowTitle(translate('OpenLP.ThemeWizard', 'Edit Theme - {name}'
                                          ).format(name=self.theme.theme_name))
            self.next()
        else:
            self.setWindowTitle(UiStrings().NewTheme)
        return QtWidgets.QWizard.exec(self)

    def initializePage(self, page_id):
        """
        Set up the pages for Initial run through dialog
        """
        log.debug('initializePage {page}'.format(page=page_id))
        wizard_page = self.page(page_id)
        if wizard_page == self.background_page:
            self.set_background_page_values()
        elif wizard_page == self.main_area_page:
            self.set_main_area_page_values()
        elif wizard_page == self.footer_area_page:
            self.set_footer_area_page_values()
        elif wizard_page == self.alignment_page:
            self.set_alignment_page_values()
        elif wizard_page == self.area_position_page:
            self.set_position_page_values()

    def set_background_page_values(self):
        """
        Handle the display and state of the Background page.
        """
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Solid):
            self.color_button.color = self.theme.background_color
            self.setField('background_type', 0)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Gradient):
            self.gradient_start_button.color = self.theme.background_start_color
            self.gradient_end_button.color = self.theme.background_end_color
            self.setField('background_type', 1)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Image):
            self.image_color_button.color = self.theme.background_border_color
            self.image_path_edit.path = self.theme.background_source
            self.setField('background_type', 2)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Video):
            self.video_color_button.color = self.theme.background_border_color
            self.video_path_edit.path = self.theme.background_source
            self.setField('background_type', 4)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Stream):
            self.setField('background_type', 5)
        elif self.theme.background_type == BackgroundType.to_string(BackgroundType.Transparent):
            self.setField('background_type', 3)
        if self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Horizontal):
            self.setField('gradient', 0)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Vertical):
            self.setField('gradient', 1)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.Circular):
            self.setField('gradient', 2)
        elif self.theme.background_direction == BackgroundGradientType.to_string(BackgroundGradientType.LeftTop):
            self.setField('gradient', 3)
        else:
            self.setField('gradient', 4)

    def set_main_area_page_values(self):
        """
        Handle the display and state of the Main Area page.
        """
        self.main_font_combo_box.setCurrentFont(QtGui.QFont(self.theme.font_main_name))
        self.main_color_button.color = self.theme.font_main_color
        self.setField('main_size_spin_box', self.theme.font_main_size)
        self.setField('line_spacing_spin_box', self.theme.font_main_line_adjustment)
        self.setField('outline_check_box', self.theme.font_main_outline)
        self.outline_color_button.color = self.theme.font_main_outline_color
        self.setField('outline_size_spin_box', self.theme.font_main_outline_size)
        self.setField('shadow_check_box', self.theme.font_main_shadow)
        self.shadow_color_button.color = self.theme.font_main_shadow_color
        self.setField('shadow_size_spin_box', self.theme.font_main_shadow_size)
        self.setField('main_bold_check_box', self.theme.font_main_bold)
        self.setField('main_italics_check_box', self.theme.font_main_italics)

    def set_footer_area_page_values(self):
        """
        Handle the display and state of the Footer Area page.
        """
        self.footer_font_combo_box.setCurrentFont(QtGui.QFont(self.theme.font_footer_name))
        self.footer_color_button.color = self.theme.font_footer_color
        self.setField('footer_size_spin_box', self.theme.font_footer_size)

    def set_position_page_values(self):
        """
        Handle the display and state of the _position page.
        """
        # Main Area
        self.main_position_check_box.setChecked(not self.theme.font_main_override)
        self.setField('main_position_x', self.theme.font_main_x)
        self.setField('main_position_y', self.theme.font_main_y)
        self.setField('main_position_height', self.theme.font_main_height)
        self.setField('main_position_width', self.theme.font_main_width)
        # Footer
        self.footer_position_check_box.setChecked(not self.theme.font_footer_override)
        self.setField('footer_position_x', self.theme.font_footer_x)
        self.setField('footer_position_y', self.theme.font_footer_y)
        self.setField('footer_position_height', self.theme.font_footer_height)
        self.setField('footer_position_width', self.theme.font_footer_width)

    def set_alignment_page_values(self):
        """
        Handle the display and state of the Alignments page.
        """
        self.setField('horizontal', self.theme.display_horizontal_align)
        self.setField('vertical', self.theme.display_vertical_align)
        self.setField('slide_transition', self.theme.display_slide_transition)

    def set_preview_page_values(self):
        """
        Handle the display and state of the Preview page.
        """
        self.setField('name', self.theme.theme_name)
        self.preview_box.set_theme(self.theme)

    def on_background_combo_box_current_index_changed(self, index):
        """
        Background style Combo box has changed.
        """
        # do not allow updates when screen is building for the first time.
        if self.update_theme_allowed:
            self.theme.background_type = BackgroundType.to_string(index)
            if self.theme.background_type != BackgroundType.to_string(BackgroundType.Image) and \
                    self.theme.background_type != BackgroundType.to_string(BackgroundType.Video) and \
                    self.temp_background_filename is None:
                self.temp_background_filename = self.theme.background_filename
                self.theme.background_filename = None
            if (self.theme.background_type == BackgroundType.to_string(BackgroundType.Image) or
                    self.theme.background_type != BackgroundType.to_string(BackgroundType.Video)) and \
                    self.temp_background_filename is not None:
                self.theme.background_filename = self.temp_background_filename
                self.temp_background_filename = None
            self.set_background_page_values()

    def on_gradient_combo_box_current_index_changed(self, index):
        """
        Background gradient Combo box has changed.
        """
        if self.update_theme_allowed:
            self.theme.background_direction = BackgroundGradientType.to_string(index)
            self.set_background_page_values()

    def on_color_changed(self, color):
        """
        Background / Gradient 1 _color button pushed.
        """
        self.theme.background_color = color

    def on_image_color_changed(self, color):
        """
        Background / Gradient 1 _color button pushed.
        """
        self.theme.background_border_color = color

    def on_video_color_changed(self, color):
        """
        Background / Gradient 1 _color button pushed.
        """
        self.theme.background_border_color = color

    def on_gradient_start_color_changed(self, color):
        """
        Gradient 2 _color button pushed.
        """
        self.theme.background_start_color = color

    def on_gradient_end_color_changed(self, color):
        """
        Gradient 2 _color button pushed.
        """
        self.theme.background_end_color = color

    def on_image_path_edit_path_changed(self, new_path):
        """
        Handle the `pathEditChanged` signal from image_path_edit

        :param pathlib.Path new_path: Path to the new image
        :rtype: None
        """
        self.theme.background_source = new_path
        self.theme.background_filename = new_path
        self.set_background_page_values()

    def on_video_path_edit_path_changed(self, new_path):
        """
        Handle the `pathEditChanged` signal from video_path_edit

        :param pathlib.Path new_path: Path to the new video
        :rtype: None
        """
        self.theme.background_source = new_path
        self.theme.background_filename = new_path
        self.set_background_page_values()

    def on_main_color_changed(self, color):
        """
        Set the main colour value
        """
        self.theme.font_main_color = color

    def on_outline_color_changed(self, color):
        """
        Set the outline colour value
        """
        self.theme.font_main_outline_color = color

    def on_shadow_color_changed(self, color):
        """
        Set the shadow colour value
        """
        self.theme.font_main_shadow_color = color

    def on_footer_color_changed(self, color):
        """
        Set the footer colour value
        """
        self.theme.font_footer_color = color

    def update_theme(self):
        """
        Update the theme object from the UI for fields not already updated
        when the are changed.
        """
        if not self.update_theme_allowed:
            return
        log.debug('update_theme')
        # main page
        self.theme.font_main_name = self.main_font_combo_box.currentFont().family()
        self.theme.font_main_size = self.field('main_size_spin_box')
        self.theme.font_main_line_adjustment = self.field('line_spacing_spin_box')
        self.theme.font_main_outline_size = self.field('outline_size_spin_box')
        self.theme.font_main_shadow_size = self.field('shadow_size_spin_box')
        self.theme.font_main_bold = self.field('main_bold_check_box')
        self.theme.font_main_italics = self.field('main_italics_check_box')
        # footer page
        self.theme.font_footer_name = self.footer_font_combo_box.currentFont().family()
        self.theme.font_footer_size = self.field('footer_size_spin_box')
        # position page
        self.theme.font_main_x = self.field('main_position_x')
        self.theme.font_main_y = self.field('main_position_y')
        self.theme.font_main_height = self.field('main_position_height')
        self.theme.font_main_width = self.field('main_position_width')
        self.theme.font_footer_x = self.field('footer_position_x')
        self.theme.font_footer_y = self.field('footer_position_y')
        self.theme.font_footer_height = self.field('footer_position_height')
        self.theme.font_footer_width = self.field('footer_position_width')
        # position page
        self.theme.display_horizontal_align = self.horizontal_combo_box.currentIndex()
        self.theme.display_vertical_align = self.vertical_combo_box.currentIndex()
        self.theme.display_slide_transition = self.field('slide_transition')

    def accept(self):
        """
        Lets save the theme as Finish has been triggered
        """
        # Save the theme name
        self.theme.theme_name = self.field('name')
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
        destination_path = None
        if self.theme.background_type == BackgroundType.to_string(BackgroundType.Image) or \
           self.theme.background_type == BackgroundType.to_string(BackgroundType.Video):
            file_name = self.theme.background_filename.name
            destination_path = self.path / self.theme.theme_name / file_name
        if not self.edit_mode and not self.theme_manager.check_if_theme_exists(self.theme.theme_name):
            return
        # Set the theme background to the cache location
        self.theme.background_filename = destination_path
        self.theme_manager.save_theme(self.theme, self.preview_box.save_screenshot())
        return QtWidgets.QDialog.accept(self)
