import os
import shutil

from openlp.plugins.songs.lib.db import init_schema, Book, Song, SongBookEntry
from openlp.plugins.songs.forms.songmaintenanceform import SongMaintenanceForm
from tests.utils.constants import TEST_RESOURCES_PATH
from tempfile import mkdtemp

from sqlalchemy.sql import and_

from openlp.core.lib.db import Manager


def test_merge_song_books(registry, settings):
    """
    Test the functionality of merging 2 song books.
    """
    # GIVEN a test database with test songs and songbooks, and a song maintenance form
    tmp_folder = mkdtemp()
    db_path = os.path.join(TEST_RESOURCES_PATH, 'songs', 'songs-2.9.2.sqlite')
    db_tmp_path = os.path.join(tmp_folder, 'songs-2.9.2.sqlite')
    shutil.copyfile(db_path, db_tmp_path)
    manager = Manager('songs', init_schema, db_file_path=db_tmp_path)

    # create 2 song books, both with the same name
    book1 = Book()
    book1.name = 'test book1'
    manager.save_object(book1)
    book2 = Book()
    book2.name = 'test book1'
    manager.save_object(book2)

    # create 3 songs, all with same search_title
    song1 = Song()
    song1.title = 'test song1'
    song1.lyrics = 'lyrics1'
    song1.search_title = 'test song'
    song1.search_lyrics = 'lyrics1'
    manager.save_object(song1)
    song2 = Song()
    song2.title = 'test song2'
    song2.lyrics = 'lyrics2'
    song2.search_title = 'test song'
    song2.search_lyrics = 'lyrics2'
    manager.save_object(song2)
    song3 = Song()
    song3.title = 'test song3'
    song3.lyrics = 'lyrics3'
    song3.search_title = 'test song'
    song3.search_lyrics = 'lyrics3'
    manager.save_object(song3)

    # associate songs with song books
    song1.add_songbook_entry(book1, '10')
    song2.add_songbook_entry(book1, '20')
    song2.add_songbook_entry(book2, '30')
    song3.add_songbook_entry(book1, '40')
    song3.add_songbook_entry(book2, '')

    song_maintenance_form = SongMaintenanceForm(manager)

    # WHEN the song books are merged, getting rid of book1
    song_maintenance_form.merge_song_books(book1)

    # THEN the database should reflect correctly the merge

    songs = manager.get_all_objects(Song, Song.search_title == 'test song')
    songbook1_entries = manager.get_all_objects(SongBookEntry, SongBookEntry.songbook_id == book1.id)
    songbook2_entries = manager.get_all_objects(SongBookEntry, SongBookEntry.songbook_id == book2.id)
    song1_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song1.id))
    song2_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song2.id))
    song3_book2_entry = manager.get_all_objects(SongBookEntry, and_(SongBookEntry.songbook_id == book2.id,
                                                                    SongBookEntry.song_id == song3.id))
    books = manager.get_all_objects(Book, Book.name == 'test book1')

    # song records should not be deleted
    assert len(songs) == 3
    # the old book should have been deleted, with its songs_songbooks records
    assert len(books) == 1
    assert len(songbook1_entries) == 0

    # each of the 3 songs should be associated with book2
    assert len(songbook2_entries) == 3

    # the individual SongBookEntry records should be correct
    assert len(song1_book2_entry) == 1
    assert song1_book2_entry[0].entry == '10'

    assert len(song2_book2_entry) == 1
    # entry field should not be overridden, as it was set previously for book2
    assert song2_book2_entry[0].entry == '30'

    assert len(song3_book2_entry) == 1
    # entry field should be overridden, as it was not set previously
    assert song3_book2_entry[0].entry == '40'
