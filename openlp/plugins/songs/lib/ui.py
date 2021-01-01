# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
The :mod:`openlp.plugins.songs.lib.ui` module provides standard UI components
for the songs plugin.
"""
from openlp.core.common.i18n import translate


class SongStrings(object):
    """
    Provide standard strings for use throughout the songs plugin.
    """
    # These strings should need a good reason to be retranslated elsewhere.
    Author = translate('OpenLP.Ui', 'Author', 'Singular')
    Authors = translate('OpenLP.Ui', 'Authors', 'Plural')
    AuthorUnknown = translate('OpenLP.Ui', 'Author Unknown')  # Used to populate the database.
    CopyrightSymbol = '\xa9'
    SongBook = translate('OpenLP.Ui', 'Songbook', 'Singular')
    SongBooks = translate('OpenLP.Ui', 'Songbooks', 'Plural')
    SongIncomplete = translate('OpenLP.Ui', 'Title and/or verses not found')
    SongMaintenance = translate('OpenLP.Ui', 'Song Maintenance')
    Topic = translate('OpenLP.Ui', 'Topic', 'Singular')
    Topics = translate('OpenLP.Ui', 'Topics', 'Plural')
    XMLSyntaxError = translate('OpenLP.Ui', 'XML syntax error')
