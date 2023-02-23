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
The :mod:`customxmlhandler` module provides the XML functionality for custom
slides

The basic XML is of the format::

    <?xml version="1.0" encoding="UTF-8"?>
    <song version="1.0">
        <lyrics language="en">
            <verse type="chorus" label="1">
                <![CDATA[ ... ]]>
            </verse>
        </lyrics>
    </song>
"""

import logging
from xml.dom.minidom import Document
from xml.etree.ElementTree import dump

from lxml import etree, objectify


log = logging.getLogger(__name__)


class CustomXML(object):
    """
    This class builds and parses the XML used to describe custom slides.
    """
    log.info('CustomXML Loaded')

    def __init__(self, xml=None):
        """
        Set up the custom builder.
        """
        if xml:
            self.parse_str(xml)
        else:
            # Create the minidom document if no input given
            self.custom_xml = Document()
            self.new_document()
            self.add_lyrics_to_song()

    def parse_str(self, xml):
        self.custom_xml = None
        if xml[:5] == '<?xml':
            xml = xml[38:]
        try:
            self.custom_xml = objectify.fromstring(xml)
            song_tags = self.custom_xml.getElementsByTagName('song')
            if song_tags:
                self.song = song_tags[0]
            else:
                self.new_document()
                log.error('Invalid xml {xml}, missing song tag'.format(xml=xml))
                return False
            lyrics_tags = self.custom_xml.getElementsByTagName('lyrics')
            if lyrics_tags:
                self.lyrics = lyrics_tags[0]
            else:
                log.error('Invalid xml {xml}, missing lyrics tag'.format(xml=xml))
                self.add_lyrics_to_song()
                return False
        except etree.XMLSyntaxError:
            log.exception('Invalid xml {xml}'.format(xml=xml))
            self.new_document()
            return False
        return True

    def new_document(self):
        """
        Create a new custom XML document.
        """
        # Create the <song> base element
        self.custom_xml = Document()
        self.song = self.custom_xml.createElement('song')
        self.custom_xml.appendChild(self.song)
        self.song.setAttribute('version', '1.0')
        self.add_lyrics_to_song()

    def add_lyrics_to_song(self):
        """
        Set up and add a ``<lyrics>`` tag which contains the lyrics of the
        custom item.
        """
        # Create the main <lyrics> element
        self.lyrics = self.custom_xml.createElement('lyrics')
        self.lyrics.setAttribute('language', 'en')
        self.song.appendChild(self.lyrics)

    def add_verse_to_lyrics(self, verse_type, number, content):
        """
        Add a verse to the ``<lyrics>`` tag.

        :param verse_type: A string denoting the type of verse. Possible values are "Chorus", "Verse", "Bridge",
            and "Custom".
        :param number:  An integer denoting the number of the item, for example: verse 1.
        :param content: The actual text of the verse to be stored.

        """
        verse = self.custom_xml.createElement('verse')
        verse.setAttribute('type', verse_type)
        verse.setAttribute('label', number)
        self.lyrics.appendChild(verse)
        # add data as a CDATA section to protect the XML from special chars
        cds = self.custom_xml.createCDATASection(content)
        verse.appendChild(cds)

    def get_verses(self):
        """
        Iterates through the verses in the XML and returns a list of verses and their attributes.
        """
        xml_iter = self.custom_xml.getiterator()
        verse_list = []
        for element in xml_iter:
            if element.tag == 'verse':
                if element.text is None:
                    element.text = ''
                verse_list.append([element.attrib, str(element.text)])
        return verse_list

    def _dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return self.custom_xml.toprettyxml(indent='  ')

    def extract_xml(self):
        """
        Extract our newly created XML custom.
        """
        return self.custom_xml.toxml('utf-8')

    def add_title_and_credit(self, title, credit):
        """
        """
        pass

    def get_title(self):
        """
        """
        return ''

    def get_credit(self):
        """
        """
        return ''
