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
"""
The :mod:`serviceitem` provides the service item functionality including the
type and capability of an item.
"""
import datetime
import logging
import ntpath
import os
import uuid
from copy import deepcopy
from pathlib import Path

from PyQt5 import QtGui

from openlp.core.state import State
from openlp.core.common import ThemeLevel, md5_hash
from openlp.core.common.applocation import AppLocation
from openlp.core.common.enum import ServiceItemType
from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.settings import Settings
from openlp.core.common.registry import Registry
from openlp.core.display.render import remove_tags, render_tags, render_chords_for_printing
from openlp.core.lib import ItemCapabilities
from openlp.core.ui.icons import UiIcons


log = logging.getLogger(__name__)


class ServiceItem(RegistryProperties):
    """
    The service item is a base class for the plugins to use to interact with
    the service manager, the slide controller, and the projection screen
    compositor.
    """
    log.info('Service Item created')

    def __init__(self, plugin=None):
        """
        Set up the service item.

        :param plugin: The plugin that this service item belongs to.
        """
        if plugin:
            self.name = plugin.name
        self._rendered_slides = None
        self._display_slides = None
        self._print_slides = None
        self.title = ''
        self.slides = []
        self.processor = None
        self.audit = ''
        self.items = []
        self.icon = UiIcons().default
        self.raw_footer = []
        # Plugins can set footer_html themselves. If they don't, it will be generated from raw_footer.
        self.footer_html = ''
        self.theme = None
        self.service_item_type = None
        self.unique_identifier = 0
        self.notes = ''
        self.from_plugin = False
        self.capabilities = []
        self.is_valid = True
        self.icon = None
        self.main = None
        self.footer = None
        self.bg_image_bytes = None
        self.search_string = ''
        self.data_string = ''
        self.edit_id = None
        self.xml_version = None
        self.start_time = 0
        self.end_time = 0
        self.media_length = 0
        self.from_service = False
        self.image_border = '#000000'
        self.background_audio = []
        self.theme_overwritten = False
        self.temporary_edit = False
        self.auto_play_slides_once = False
        self.auto_play_slides_loop = False
        self.timed_slide_interval = 0
        self.will_auto_start = False
        self.has_original_files = True
        self._new_item()
        self.metadata = []

    def get_theme_data(self, theme_level=None):
        """
        Get the theme appropriate for this item

        :param theme_level: The theme_level to use,
                            the value in Settings is used when this value is missinig
        """
        if theme_level is None:
            theme_level = self.settings.value('themes/theme level')
        theme_manager = Registry().get('theme_manager')
        # Just assume we use the global theme.
        theme = theme_manager.global_theme
        if theme_level != ThemeLevel.Global:
            service_theme = self.settings.value('servicemanager/service theme')
            # Service or Song level, so assume service theme (if it exists and item in service)
            # but use song theme if level is song (and it exists)
            if service_theme and self.from_service:
                theme = service_theme
            if theme_level == ThemeLevel.Song and self.theme:
                theme = self.theme
        theme = theme_manager.get_theme_data(theme)
        return theme

    def _new_item(self):
        """
        Method to set the internal id of the item. This is used to compare service items to see if they are the same.
        """
        self.unique_identifier = str(uuid.uuid1())
        self.validate_item()

    def add_capability(self, capability):
        """
        Add an ItemCapability to a ServiceItem

        :param capability: The capability to add
        """
        self.capabilities.append(capability)

    def is_capable(self, capability):
        """
        Tell the caller if a ServiceItem has a capability

        :param capability: The capability to test for
        """
        return capability in self.capabilities

    def add_icon(self):
        """
        Add an icon to the service item. This is used when displaying the service item in the service manager.
        """
        if self.name == 'songs':
            self.icon = UiIcons().music
        elif self.name == 'bibles':
            self.icon = UiIcons().bible
        elif self.name == 'presentations':
            self.icon = UiIcons().presentation
        elif self.name == 'images':
            self.icon = UiIcons().picture
        elif self.name == 'media':
            self.icon = UiIcons().video
        else:
            self.icon = UiIcons().clone

    def _create_slides(self):
        """
        Create frames for rendering and display
        """
        self._rendered_slides = []
        self._display_slides = []

        # Save rendered pages to this dict. In the case that a slide is used twice we can use the pages saved to
        # the dict instead of rendering them again.
        previous_pages = {}
        index = 0
        if not self.footer_html:
            self.footer_html = '<br>'.join([_f for _f in self.raw_footer if _f])
        for raw_slide in self.slides:
            verse_tag = raw_slide['verse']
            if verse_tag in previous_pages and previous_pages[verse_tag][0] == raw_slide:
                pages = previous_pages[verse_tag][1]
            else:
                pages = self.renderer.format_slide(raw_slide['text'], self)
                previous_pages[verse_tag] = (raw_slide, pages)
            for page in pages:
                rendered_slide = {
                    'title': raw_slide['title'],
                    'text': render_tags(page),
                    'verse': index,
                    'footer': self.footer_html,
                }
                self._rendered_slides.append(rendered_slide)
                display_slide = {
                    'title': raw_slide['title'],
                    'text': remove_tags(page, can_remove_chords=True),
                    'verse': verse_tag,
                }
                self._display_slides.append(display_slide)
                index += 1

    @property
    def rendered_slides(self):
        """
        Render the frames and return them
        """
        if not self._rendered_slides:
            self._create_slides()
        return self._rendered_slides

    @property
    def display_slides(self):
        """
        Render the frames and return them
        """
        if not self._display_slides:
            self._create_slides()
        return self._display_slides

    @property
    def print_slides(self):
        """
        Render the frames for printing and return them

        """
        if not self._print_slides:
            self._print_slides = []
            previous_pages = {}
            index = 0
            for raw_slide in self.slides:
                verse_tag = raw_slide['verse']
                if verse_tag in previous_pages and previous_pages[verse_tag][0] == raw_slide:
                    pages = previous_pages[verse_tag][1]
                else:
                    pages = self.renderer.format_slide(raw_slide['text'], self)
                    previous_pages[verse_tag] = (raw_slide, pages)
                for page in pages:
                    slide = {
                        'title': raw_slide['title'],
                        'text': render_chords_for_printing(remove_tags(page), '\n'),
                        'verse': index,
                        'footer': self.raw_footer,
                    }
                    self._print_slides.append(slide)
        return self._print_slides

    def add_from_image(self, path, title, background=None, thumbnail=None):
        """
        Add an image slide to the service item.

        :param path: The directory in which the image file is located.
        :param title: A title for the slide in the service item.
        :param background: The background colour
        :param thumbnail: Optional alternative thumbnail, used for remote thumbnails.
        """
        if background:
            self.image_border = background
        self.service_item_type = ServiceItemType.Image
        slide = {'title': title, 'path': path}
        if thumbnail:
            slide['thumbnail'] = thumbnail
        self.slides.append(slide)
        # self.image_manager.add_image(path, ImageSource.ImagePlugin, self.image_border)
        self._new_item()

    def add_from_text(self, text, verse_tag=None):
        """
        Add a text slide to the service item.

        :param text: The raw text of the slide.
        :param verse_tag:
        """
        if verse_tag:
            verse_tag = verse_tag.upper()
        else:
            # For items that don't have a verse tag, autoincrement the slide numbers
            verse_tag = str(len(self.slides))
        self.service_item_type = ServiceItemType.Text
        title = text[:30].split('\n')[0]
        self.slides.append({'title': title, 'text': text, 'verse': verse_tag})
        self._new_item()

    def add_from_command(self, path, file_name, image, display_title=None, notes=None):
        """
        Add a slide from a command.

        :param path: The title of the slide in the service item.
        :param file_name: The title of the slide in the service item.
        :param image: The command of/for the slide.
        :param display_title: Title to show in gui/webinterface, optional.
        :param notes: Notes to show in the webinteface, optional.
        """
        self.service_item_type = ServiceItemType.Command
        # If the item should have a display title but this frame doesn't have one, we make one up
        if self.is_capable(ItemCapabilities.HasDisplayTitle) and not display_title:
            display_title = translate('OpenLP.ServiceItem',
                                      '[slide {frame:d}]').format(frame=len(self.slides) + 1)
        # Update image path to match servicemanager location if file was loaded from service
        if image and not self.has_original_files and self.name == 'presentations':
            file_location = os.path.join(path, file_name)
            file_location_hash = md5_hash(file_location.encode('utf-8'))
            image = os.path.join(AppLocation.get_section_data_path(self.name), 'thumbnails', file_location_hash,
                                 ntpath.basename(image))  # TODO: Pathlib
        self.slides.append({'title': file_name, 'image': image, 'path': path, 'display_title': display_title,
                            'notes': notes, 'thumbnail': image})
        # if self.is_capable(ItemCapabilities.HasThumbnails):
        #     self.image_manager.add_image(image, ImageSource.CommandPlugins, '#000000')
        self._new_item()

    def get_service_repr(self, lite_save):
        """
        This method returns some text which can be saved into the service file to represent this item.
        """
        service_header = {
            'name': self.name,
            'plugin': self.name,
            'theme': self.theme,
            'title': self.title,
            'footer': self.raw_footer,
            'type': self.service_item_type,
            'audit': self.audit,
            'notes': self.notes,
            'from_plugin': self.from_plugin,
            'capabilities': self.capabilities,
            'search': self.search_string,
            'data': self.data_string,
            'xml_version': self.xml_version,
            'auto_play_slides_once': self.auto_play_slides_once,
            'auto_play_slides_loop': self.auto_play_slides_loop,
            'timed_slide_interval': self.timed_slide_interval,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'media_length': self.media_length,
            'background_audio': self.background_audio,
            'theme_overwritten': self.theme_overwritten,
            'will_auto_start': self.will_auto_start,
            'processor': self.processor,
            'metadata': self.metadata
        }
        service_data = []
        if self.service_item_type == ServiceItemType.Text:
            for slide in self.slides:
                data_slide = deepcopy(slide)
                data_slide['raw_slide'] = data_slide.pop('text')
                data_slide['verseTag'] = data_slide.pop('verse')
                service_data.append(data_slide)
        elif self.service_item_type == ServiceItemType.Image:
            if lite_save:
                for slide in self.slides:
                    service_data.append({'title': slide['title'], 'path': slide['path']})
            else:
                service_data = [slide['title'] for slide in self.slides]
        elif self.service_item_type == ServiceItemType.Command:
            for slide in self.slides:
                if isinstance(slide['image'], QtGui.QIcon):
                    image = "clapperboard"
                else:
                    image = slide['image']
                service_data.append({'title': slide['title'], 'image': image, 'path': slide['path'],
                                     'display_title': slide['display_title'], 'notes': slide['notes']})
        return {'header': service_header, 'data': service_data}

    def render_text_items(self):
        """
        This method forces the display to be regenerated
        """
        self._display_slides = []
        self._rendered_slides = []

    def set_from_service(self, service_item, path=None):
        """
        This method takes a service item from a saved service file (passed from the ServiceManager) and extracts the
        data actually required.

        :param service_item: The item to extract data from.
        :param path: Defaults to *None*. This is the service manager path for things which have their files saved
            with them or None when the saved service is lite and the original file paths need to be preserved.
        """
        log.debug('set_from_service called with path {path}'.format(path=path))
        header = service_item['serviceitem']['header']
        self.title = header['title']
        self.name = header['name']
        self.service_item_type = header['type']
        self.theme = header['theme']
        self.add_icon()
        self.raw_footer = header['footer']
        self.audit = header['audit']
        self.notes = header['notes']
        self.from_plugin = header['from_plugin']
        self.capabilities = header['capabilities']
        # Added later so may not be present in older services.
        self.search_string = header.get('search', '')
        self.data_string = header.get('data', '')
        self.xml_version = header.get('xml_version')
        self.start_time = header.get('start_time', 0)
        self.end_time = header.get('end_time', 0)
        self.media_length = header.get('media_length', 0)
        self.auto_play_slides_once = header.get('auto_play_slides_once', False)
        self.auto_play_slides_loop = header.get('auto_play_slides_loop', False)
        self.timed_slide_interval = header.get('timed_slide_interval', 0)
        self.will_auto_start = header.get('will_auto_start', False)
        self.processor = header.get('processor', None)
        self.has_original_files = True
        self.metadata = header.get('item_meta_data', [])
        if 'background_audio' in header and State().check_preconditions('media'):
            self.background_audio = []
            for file_path in header['background_audio']:
                # In OpenLP 3.0 we switched to storing Path objects in JSON files
                if isinstance(file_path, str):
                    # Handle service files prior to OpenLP 3.0
                    # Windows can handle both forward and backward slashes, so we use ntpath to get the basename
                    file_path = path / ntpath.basename(file_path)
                self.background_audio.append(file_path)
        self.theme_overwritten = header.get('theme_overwritten', False)
        if self.service_item_type == ServiceItemType.Text:
            for slide in service_item['serviceitem']['data']:
                self.add_from_text(slide['raw_slide'], slide['verseTag'])
            self._create_slides()
        elif self.service_item_type == ServiceItemType.Image:
            settings_section = service_item['serviceitem']['header']['name']
            background = QtGui.QColor(self.settings.value(settings_section + '/background color'))
            if path:
                self.has_original_files = False
                for text_image in service_item['serviceitem']['data']:
                    file_path = path / text_image
                    self.add_from_image(file_path, text_image, background)
            else:
                for text_image in service_item['serviceitem']['data']:
                    self.add_from_image(text_image['path'], text_image['title'], background)
        elif self.service_item_type == ServiceItemType.Command:
            for text_image in service_item['serviceitem']['data']:
                if not self.title:
                    self.title = text_image['title']
                if self.is_capable(ItemCapabilities.IsOptical):
                    self.has_original_files = False
                    self.add_from_command(text_image['path'], text_image['title'], text_image['image'])
                elif path:
                    self.has_original_files = False
                    if text_image['image'] == "clapperboard":
                        text_image['image'] = UiIcons().clapperboard
                    self.add_from_command(path, text_image['title'], text_image['image'],
                                          text_image.get('display_title', ''), text_image.get('notes', ''))
                else:
                    self.add_from_command(Path(text_image['path']), text_image['title'], text_image['image'])
        self._new_item()

    def get_display_title(self):
        """
        Returns the title of the service item.
        """
        if self.is_text() or self.is_capable(ItemCapabilities.IsOptical) \
                or self.is_capable(ItemCapabilities.CanEditTitle):
            return self.title
        else:
            if len(self.slides) > 1:
                return self.title
            else:
                return self.slides[0]['title']

    def merge(self, other):
        """
        Updates the unique_identifier with the value from the original one
        The unique_identifier is unique for a given service item but this allows one to replace an original version.

        :param other: The service item to be merged with
        """
        self.unique_identifier = other.unique_identifier
        self.notes = other.notes
        self.temporary_edit = other.temporary_edit
        # Copy theme over if present.
        if other.theme is not None:
            self.theme = other.theme
            self._new_item()
        if self.is_capable(ItemCapabilities.HasBackgroundAudio):
            log.debug(self.background_audio)

    def __eq__(self, other):
        """
        Confirms the service items are for the same instance
        """
        if not other:
            return False
        return self.unique_identifier == other.unique_identifier

    def __ne__(self, other):
        """
        Confirms the service items are not for the same instance
        """
        return self.unique_identifier != other.unique_identifier

    def __hash__(self):
        """
        Return the hash for the service item.
        """
        return self.unique_identifier

    def is_media(self):
        """
        Confirms if the ServiceItem is media
        """
        return ItemCapabilities.RequiresMedia in self.capabilities

    def is_command(self):
        """
        Confirms if the ServiceItem is a command
        """
        return self.service_item_type == ServiceItemType.Command

    def is_image(self):
        """
        Confirms if the ServiceItem is an image
        """
        return self.service_item_type == ServiceItemType.Image

    def uses_file(self):
        """
        Confirms if the ServiceItem uses a file
        """
        return self.service_item_type == ServiceItemType.Image or \
            (self.service_item_type == ServiceItemType.Command and not self.is_capable(ItemCapabilities.IsOptical))

    def is_text(self):
        """
        Confirms if the ServiceItem is text
        """
        return self.service_item_type == ServiceItemType.Text

    def set_media_length(self, length):
        """
        Stores the media length of the item

        :param length: The length of the media item
        """
        self.media_length = length
        if length > 0:
            self.add_capability(ItemCapabilities.HasVariableStartTime)

    def get_frames(self):
        """
        Returns the frames for the ServiceItem
        """
        if self.service_item_type == ServiceItemType.Text:
            return self.display_slides
        else:
            return self.slides

    def get_rendered_frame(self, row):
        """
        Returns the correct frame for a given list and renders it if required.

        :param row: The service item slide to be returned
        """
        if self.service_item_type == ServiceItemType.Text:
            return self.rendered_slides[row]['text']
        elif self.service_item_type == ServiceItemType.Image:
            return self.slides[row]['path']
        else:
            return self.slides[row]['image']

    def get_frame_title(self, row=0):
        """
        Returns the title of the raw frame
        """
        try:
            return self.get_frames()[row]['title']
        except IndexError:
            return ''

    def get_frame_path(self, row=0, frame=None):
        """
        Returns the path of the raw frame
        """
        if not frame:
            try:
                frame = self.slides[row]
            except IndexError:
                return ''
        if self.is_image() or self.is_capable(ItemCapabilities.IsOptical):
            path_from = frame['path']
        else:
            path_from = os.path.join(frame['path'], frame['title'])
        if isinstance(path_from, str):
            # Handle service files prior to OpenLP 3.0
            # Windows can handle both forward and backward slashes, so we use ntpath to get the basename
            path_from = Path(path_from)
        return path_from

    def remove_frame(self, frame):
        """
        Remove the specified frame from the item
        """
        if frame in self.slides:
            self.slides.remove(frame)

    def get_media_time(self):
        """
        Returns the start and finish time for a media item
        """
        start = None
        end = None
        if self.start_time != 0:
            time = str(datetime.timedelta(seconds=self.start_time))
            start = translate('OpenLP.ServiceItem',
                              '<strong>Start</strong>: {start}').format(start=time)
        if self.media_length != 0:
            length = str(datetime.timedelta(seconds=self.media_length // 1000))
            end = translate('OpenLP.ServiceItem', '<strong>Length</strong>: {length}').format(length=length)

        if not start and not end:
            return ''
        elif start and not end:
            return start
        elif not start and end:
            return end
        else:
            return '{start} <br>{end}'.format(start=start, end=end)

    def update_theme(self, theme):
        """
        updates the theme in the service item

        :param theme: The new theme to be replaced in the service item
        """
        self.theme_overwritten = (theme is None)
        self.theme = theme
        self._new_item()

    def remove_invalid_frames(self, invalid_paths=None):
        """
        Remove invalid frames, such as ones where the file no longer exists.
        """
        if self.uses_file():
            for frame in self.get_frames():
                if self.get_frame_path(frame=frame) in invalid_paths:
                    self.remove_frame(frame)

    def missing_frames(self):
        """
        Returns if there are any frames in the service item
        """
        return not bool(self.slides)

    def validate_item(self, suffixes=None):
        """
        Validates a service item to make sure it is valid

        :param set[str] suffixes: A set of valid suffixes
        """
        self.is_valid = True
        for slide in self.slides:
            if self.is_image() and not os.path.exists(slide['path']):
                self.is_valid = False
                break
            elif self.is_command():
                if self.is_capable(ItemCapabilities.IsOptical) and State().check_preconditions('media'):
                    if not os.path.exists(slide['title']):
                        self.is_valid = False
                        break
                else:
                    file_name = os.path.join(slide['path'], slide['title'])
                    if not os.path.exists(file_name):
                        self.is_valid = False
                        break
                    if suffixes and not self.is_text():
                        file_suffix = "*.{suffx}".format(suffx=slide['title'].split('.')[-1])
                        if file_suffix.lower() not in suffixes:
                            self.is_valid = False
                            break
