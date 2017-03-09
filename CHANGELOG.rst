OpenLP 2.4.6
============

* Fixed a bug where the author type upgrade was being ignore because it was looking at the wrong table
* Fixed a bug where the songs_songbooks table was not being created because the if expression was the wrong way round
* Changed the songs_songbooks migration SQL slightly to take into account a bug that has (hopefully) been fixed
* Add another upgrade step to remove erroneous songs_songbooks entries due to the previous bug
* Added importing of author types to the OpenLP 2 song importer
