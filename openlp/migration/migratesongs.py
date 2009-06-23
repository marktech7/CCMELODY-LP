"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008 Martin Thompson, Tim Bentley

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
import os
import sys
import logging
import sqlite3
from openlp.core.lib import PluginConfig

from sqlalchemy import  *
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, mapper, relation, clear_mappers
from openlp.plugins.songs.lib.models import metadata, session, \
    engine, songs_table, Song, Author, Topic,  Book
from openlp.plugins.songs.lib.tables import *
from openlp.plugins.songs.lib.classes import *

def init_models(url):
    engine = create_engine(url)
    metadata.bind = engine
    session = scoped_session(sessionmaker(autoflush=True, autocommit=False,
                                          bind=engine))
    mapper(Author, authors_table)
    mapper(TAuthor, temp_authors_table)
    mapper(Book, song_books_table)
    mapper(Song, songs_table,
       properties={'authors': relation(Author, backref='songs',
                                       secondary=authors_songs_table),
                   'book': relation(Book, backref='songs'),
                   'topics': relation(Topic, backref='songs',
                                      secondary=songs_topics_table)})
    mapper(TSong, temp_songs_table)
    mapper(TSongAuthor, temp_authors_songs_table)
    mapper(Topic, topics_table)
    return session

temp_authors_table = Table(u'authors_temp', metadata,
    Column(u'authorid', types.Integer,  primary_key=True),
    Column(u'authorname', String(40))
)

temp_songs_table = Table(u'songs_temp', metadata,
    Column(u'songid', types.Integer, primary_key=True),
    Column(u'songtitle', String(60)),
    Column(u'lyrics', types.UnicodeText),
    Column(u'copyrightinfo', String(255)),
    Column(u'settingsid', types.Integer)
)

# Definition of the "authors_songs" table
temp_authors_songs_table = Table(u'songauthors_temp', metadata,
    Column(u'authorid', types.Integer, primary_key=True),
    Column(u'songid', types.Integer)
)
class BaseModel(object):
    """
    BaseModel provides a base object with a set of generic functions
    """

    @classmethod
    def populate(cls, **kwargs):
        """
        Creates an instance of a class and populates it, returning the instance
        """
        me = cls()
        keys = kwargs.keys()
        for key in keys:
            me.__setattr__(key, kwargs[key])
        return me

class TAuthor(BaseModel):
    """
    Author model
    """
    pass

class TSong(BaseModel):
    """
    Author model
    """
    pass

class TSongAuthor(BaseModel):
    """
    Author model
    """
    pass

class MigrateSongs():
    def __init__(self, display):
        self.display = display
        self.config = PluginConfig(u'Songs')
        self.data_path = self.config.get_data_path()
        self.database_files = self.config.get_files(u'sqlite')
        print self.database_files

    def process(self):
        self.display.output(u'Songs processing started')
        for f in self.database_files:
            self.v_1_9_0(f)
        self.display.output(u'Songs processing finished')

    def v_1_9_0(self, database):
        self.display.output(u'Migration 1.9.0 Started for ' + database)
        self._v1_9_0_old(database)
        self._v1_9_0_new(database)
        self._v1_9_0_cleanup(database)
        self.display.output(u'Migration 1.9.0 Finished for ' + database)

    def _v1_9_0_old(self, database):
        self.display.sub_output(u'Rename Tables ' + database)
        conn = sqlite3.connect(self.data_path + os.sep + database)
        conn.execute(u'alter table authors rename to authors_temp;')
        conn.commit()
        conn.execute(u'alter table songs rename to songs_temp;')
        conn.commit()
        conn.execute(u'alter table songauthors rename to songauthors_temp;')
        conn.commit()

    def _v1_9_0_new(self, database):
        self.display.sub_output(u'Create new Tables ' + database)
        self.db_url = u'sqlite:///' + self.data_path + u'/songs.sqlite'
        print self.db_url
        self.session = init_models(self.db_url)
        if not songs_table.exists():
            metadata.create_all()
        results = self.session.query(TSong).order_by(TSong.songid).all()
        for songs_temp in results:
            song = Song()
            song.title = songs_temp.songtitle
            song.lyrics = songs_temp.lyrics.replace(u'\r\n', u'\n')
            song.copyright = songs_temp.copyrightinfo
            song.search_title = u''
            song.search_lyrics = u''
            print songs_temp.songtitle
            aa  = self.session.execute(u'select * from songauthors_temp where songid =' + unicode(songs_temp.songid) )
            for row in aa:
                a = row['authorid']
                author = Author()
                authors_temp = self.session.query(TAuthor).get(a)
                author.display_name =  authors_temp.authorname
                song.authors.append(author)
            try:
                self.session.add(song)
                self.session.commit()
            except:
                self.session.rollback()
                print u'Errow thrown = ', sys.exc_info()[1]

    def _v1_9_0_cleanup(self, database):
        self.display.sub_output(u'Update Internal Data ' + database)
        conn = sqlite3.connect(self.data_path + os.sep + database)
        conn.execute("""update songs set search_title =
            replace(replace(replace(replace(replace(replace(replace(replace(
            replace(title,  '&', 'and'), ',', ''), ';', ''), ':', ''),
            '(u', ''), ')', ''), '{', ''), '}',''),'?','');""")
        conn.execute("""update songs set search_lyrics =
            replace(replace(replace(replace(replace(replace(replace(replace(
            replace(lyrics,  '&', 'and'), ',', ''), ';', ''), ':', ''),
            '(u', ''), ')', ''), '{', ''), '}',''),'?','')
            ;""")
        conn.commit()
