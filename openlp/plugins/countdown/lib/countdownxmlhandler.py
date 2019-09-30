# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2014 Raoul Snyman                                        #
# Portions copyright (c) 2008-2014 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Samuel Findlay, Michael Gorven, Scott Guerrieri, Matthias Hub,      #
# Meinert Jordan, Armin Köhler, Erik Lundin, Edwin Lunando, Brian T. Meyer.   #
# Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias Põldaru,          #
# Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,             #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Dave Warnock,              #
# Frode Woldsund, Martin Zibricky, Patrick Zimmermann                         #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################
"""
The :mod:`countdownxmlhandler` module provides the XML functionality for countdown
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
import datetime
from xml.dom.minidom import Document
from xml.etree.ElementTree import dump
from lxml import etree, objectify

log = logging.getLogger(__name__)


# TODO: These classes need to be refactored into a single class.
class CountdownXMLBuilder(object):
    """
    This class builds the XML used to describe songs.
    """
    log.info('CountdownXMLBuilder Loaded')

    def __init__(self):
        """
        Set up the countdown builder.
        """
        # Create the minidom document
        self.countdown_xml = Document()
        self.new_document()
        self.add_lyrics_to_song()

    def new_document(self):
        """
        Create a new countdown XML document.
        """
        # Create the <song> base element
        self.song = self.countdown_xml.createElement('song')
        self.countdown_xml.appendChild(self.song)
        self.song.setAttribute('version', '1.0')

    def add_lyrics_to_song(self):
        """
        Set up and add a ``<lyrics>`` tag which contains the lyrics of the
        countdown item.
        """
        # Create the main <lyrics> element
        self.lyrics = self.countdown_xml.createElement('lyrics')
        self.lyrics.setAttribute('language', 'en')
        self.song.appendChild(self.lyrics)

    def add_verse_to_lyrics(self, verse_type, number, content):
        """
        Add a verse to the ``<lyrics>`` tag.

        :param verse_type: A string denoting the type of verse. Possible values are "Chorus", "Verse", "Bridge",
        and "Countdown".
        :param number:  An integer denoting the number of the item, for example: verse 1.
        :param content: The actual text of the verse to be stored.

        """
        verse = self.countdown_xml.createElement('verse')
        verse.setAttribute('type', verse_type)
        verse.setAttribute('label', number)
        self.lyrics.appendChild(verse)
        # add data as a CDATA section to protect the XML from special chars
        cds = self.countdown_xml.createCDATASection(content)
        verse.appendChild(cds)

    def _dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return self.countdown_xml.toprettyxml(indent='  ')

    def extract_xml(self):
        """
        Extract our newly created XML countdown.
        """
        return self.countdown_xml.toxml('utf-8')


class CountdownXMLParser(object):
    """
    A class to read in and parse a countdown's XML.
    """
    log.info('CountdownXMLParser Loaded')

    def __init__(self, xml):
        """
        Set up our countdown XML parser.

        :param xml: The XML of the countdown to be parsed.
        """
        self.countdown_xml = None
        if xml[:5] == '<?xml':
            xml = xml[38:]
        try:
            self.countdown_xml = objectify.fromstring(xml)
        except etree.XMLSyntaxError:
            log.exception('Invalid xml %s', xml)

    def get_time_remaining(self):
        """
        Iterates through the verses in the XML and returns a list of verses and their attributes.
        """
        """xml_iter = self.countdown_xml.getiterator()
        verse_list = []
        for element in xml_iter:
            if element.tag == 'verse':
                if element.text is None:
                    element.text = ''
                verse_list.append([element.attrib, str(element.text)])
		"""
        time_remaining = datetime.datetime(2011, 5, 5) - datetime.datetime.now()
        return str(time_remaining)

    def get_countdown_item_settings(self):
        test = 'test data'
        return test

    def _dump_xml(self):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        return dump(self.countdown_xml)