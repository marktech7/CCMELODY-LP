OpenLP 3.0.2
============

* Only show hash if song book number exists
* FIX: Missing looping for theme background videos
* Fixing Songs' Topics media manager icon to be the same from the Song Maintenance dialog
* Adding ability to return transposed item with service_item format to avoid duplicate calls on remote
* Fix OpenLyrics whitespaces being 'eaten' (again)
* Fixing service manager's list exception when pressing 'Left' keyboard key without any item selected
* Force the use of SqlAlchemy 1.4 for now
* Removing login requirement from transpose endpoint
* Handle verse ranges in BibleServer
* Fix up loading 2.9.x services
* Attempt to fix #1287 by checking for both str and bytes, and decoding bytes to unicode
* Add debugging for VLC and fix strange state.
* Display the closing progress dialog during plugin shutdown
* Fix an issue with the Worship Center Pro importer
* Fix white preview display when previewing presentations
* Fix an issue where the websockets server would try to shut down even when -w is supplied
* Use a simpler approach when creating a tmp file when saving service files


OpenLP 2.5.1
============

* Fixed a bug where the author type upgrade was being ignore because it was looking at the wrong table
* Fixed a bug where the songs_songbooks table was not being created because the if expression was the wrong way round
* Changed the songs_songbooks migration SQL slightly to take into account a bug that has (hopefully) been fixed
* Sometimes the timer goes off as OpenLP is shutting down, and the application has already been deleted (reported via support system)
* Fix opening the data folder (KDE thought the old way was an SMB share)
* Fix a problem with the new QMediaPlayer not controlling the playlist anymore
* Added importing of author types to the OpenLP 2 song importer
* Refactored the merge script and gave it some options
* Fix a problem with loading Qt's translation files, bug #1676163
