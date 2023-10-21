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
The :mod:`~openlp.plugins.breeze.forms.selectplanform` module contains
the GUI for the Breeze Service Plan importer
"""
from sqlalchemy.sql import or_
import logging
import re
from datetime import date, datetime, timedelta

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.plugins.bibles.lib import parse_reference
from openlp.plugins.bibles.lib.mediaitem import BibleMediaItem
from openlp.plugins.breeze.forms.selectserviceplandialog import Ui_SelectPlanDialog
from openlp.plugins.breeze.lib.customimport import BreezeCustomImport
from openlp.plugins.breeze.lib.breeze_api import BreezeAPI
from openlp.plugins.songs.lib import Song, clean_string
from openlp.plugins.songs.lib.db import SongBookEntry, SongBook
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.songsplugin import SongsPlugin

log = logging.getLogger(__name__)


class BreezeForm(QtWidgets.QDialog, Ui_SelectPlanDialog):
    """
    The :class:`SelectServicePlanForm` class is the main Breeze dialog.
    """

    def __init__(self, parent=None, plugin=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.plugin = plugin
        # create Breeze API Object
        username = Registry().get('settings').value('breeze/username')
        secret = Registry().get('settings').value('breeze/secret')
        subdomain = Registry().get('settings').value('breeze/subdomain')
        token = Registry().get('settings').value('breeze/token')
        self.api = BreezeAPI(username, secret, subdomain, token)
        self.setup_ui(self)
        self.plan_selection_combo_box.currentIndexChanged.connect(self.on_plan_selection_combobox_changed)
        self.import_as_new_button.clicked.connect(self.on_import_as_new_button_clicked)
        self.update_existing_button.clicked.connect(self.on_update_existing_button_clicked)
        self.edit_auth_button.clicked.connect(self.on_edit_auth_button_clicked)

    def exec(self):
        """
        Execute the dialog. This method sets everything back to its initial
        values.
        """
        self.import_as_new_button.setEnabled(False)
        self.update_existing_button.setEnabled(False)
        # check our credentials and connection to Breeze
        organization = self.api.test()
        if len(organization) == 0:
            QtWidgets.QMessageBox.warning(self.parent(), 'Breeze Authentication Failed',
                                          'Authentication Failed.  '
                                          'Check your credentials in OpenLP Settings.',
                                          QtWidgets.QMessageBox.Ok)
            return

        # Fetch the Plans within a week
        event_list = self._fetch_events()
        # Get Today's date and see if it is listed... if it is, then select it in the combobox
        self.plan_selection_combo_box.clear()
        self.plan_selection_combo_box.addItem('Select Service Plan Date')
        self.plan_selection_combo_box.setCurrentIndex(0)
        today = date.today()

        for event in event_list:
            # start_datetime=str: 2023-09-26 00:00:00
            plan_datetime = datetime.strptime(event['start'], '%Y-%m-%d %H:%M:%S')
            plan_date = date(plan_datetime.year, plan_datetime.month, plan_datetime.day)
            self.plan_selection_combo_box.addItem('{0} ({1})'.format(
                event['name'],
                plan_date.strftime('%Y-%m-%d')
            ), event['service_plan_id'])
            # if we have any date that matches today or in the future, select it
            if plan_date >= today:
                self.plan_selection_combo_box.setCurrentIndex(self.plan_selection_combo_box.count() - 1)
                self.import_as_new_button.setEnabled(True)
                # self.update_existing_button.setEnabled(True)
        # Set the 2 lists of themes
        theme_manager = Registry().get('theme_manager')
        for theme in theme_manager.get_theme_names():
            self.song_theme_selection_combo_box.addItem(theme)
            self.slide_theme_selection_combo_box.addItem(theme)

        return QtWidgets.QDialog.exec(self)

    def done(self, result_code):
        """
        Close dialog.

        :param result_code: The result of the dialog.
        """
        log.debug('Closing BreezeForm')
        return QtWidgets.QDialog.done(self, result_code)

    def on_edit_auth_button_clicked(self):
        """
        Open the edit auth screen
        """
        self.done(QtWidgets.QDialog.Accepted)
        settings_form = Registry().get('settings_form')
        settings_form.exec(translate('BreezePlugin', 'Breeze'))

    def on_plan_selection_combobox_changed(self):
        """
        Set the Import button enable/disable based upon the current plan_selection_combo_box setting.
        """
        current_index = self.plan_selection_combo_box.currentIndex()
        if current_index == 0 or current_index == -1:
            self.import_as_new_button.setEnabled(False)
            self.update_existing_button.setEnabled(False)
        else:
            self.import_as_new_button.setEnabled(True)
            self.update_existing_button.setEnabled(True)

    def on_update_existing_button_clicked(self):
        """
        Call the import function but tell it to also do an update so that it can
        keep changed items
        """
        self._do_import(update=True)
        self.done(QtWidgets.QDialog.Accepted)

    def on_import_as_new_button_clicked(self):
        """
        Create a new service and import all of the PCO items into it
        """
        self._do_import(update=False)
        self.done(QtWidgets.QDialog.Accepted)

    def _do_import(self, update=False):
        """
        Utility function to perform the import or update as requested
        """
        service_manager = Registry().get('service_manager')
        service_manager.on_new_service_clicked()
        # we only continue here if the service_manager is now empty
        if len(service_manager.service_items) == 0:
            service_manager.application.set_busy_cursor()
            # get the plan ID for the current plan selection
            service_plan_id = self.plan_selection_combo_box.itemData(self.plan_selection_combo_box.currentIndex())
            # get the items array from Breeze
            # TODO: Fetching service plans loader box
            service_plan_items_dict = self.api.get_service_plan(service_plan_id)
            segments = service_plan_items_dict['segments']
            service_manager.main_window.display_progress_bar(len(segments))
            # convert the planning center dict to Songs and Add them to the ServiceManager
            segment_id_to_openlp_id = {}
            for segment in segments:
                item_title = segment['title']
                media_type = ''
                media_type_suffix = ''
                openlp_id = -1

                if segment['type'] == 'song':
                    # TODO: Replace with actual song ID when Breeze implements songs
                    song_id = segment['id']
                    if song_id not in segment_id_to_openlp_id:
                        # TODO: Waiting for Breeze Service Plan Songs
                        # Interface with Song Plugin to find song in local library or CCLI
                        # Add slide from there! We are not importing lyrics at all.
                        songs_plugin: SongsPlugin = Registry().get('songs').plugin
                        # Could get the songs (a SongMediaItem) and use search(string), which does an everything search.
                        # Check DB first if song exists so we don't overwrite anything
                        # If title starts with a number and a space, look in default songbook for the number.
                        # Search by title, search_title, and ccli_number
                        search_string = '%{text}%'.format(text=clean_string(segment['title']))
                        search = songs_plugin.manager.session.query(Song) \
                            .join(SongBookEntry, isouter=True) \
                            .join(SongBook, isouter=True) \
                            .filter(or_(SongBook.name.like(search_string),
                                        SongBookEntry.entry.like(search_string),
                                        Song.search_title.like(search_string)
                                        )).all()

                        if search:
                            # Let's add the first one for now
                            openlp_id = search[0].id
                            # TODO: If not there and we have a CCLI ID and the songselect is enabled, then init import
                        else:
                            # Else, create a song slide with just the title
                            song_import = SongImport(songs_plugin, file_path=None)
                            song_import.set_defaults()
                            song_import.title = segment['title']
                            song_import.add_verse('')
                            openlp_id = song_import.finish(temporary_flag=True)
                            if segment['updated_at']:
                                song = songs_plugin.manager.get_object(Song, openlp_id)
                                song.last_modified = datetime.strptime(segment['updated_at']
                                                                       .rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
                                songs_plugin.manager.save_object(song)
                        media_type = 'songs'
                        media_type_suffix = 'song'
                elif segment['type'] == 'scripture':
                    # get the bible manager
                    bible_media: BibleMediaItem = Registry().get('bibles')
                    bibles = bible_media.plugin.manager.get_bibles()
                    # get the current bible selected from the bibles plugin screen
                    bible = bible_media.version_combo_box.currentText()
                    if len(bible) == 0 and len(bibles) > 0:
                        # if we have no bible in the version_combo_box, but we have
                        # one or more bibles available, use one of those
                        bible = next(iter(bibles))
                    language_selection = bible_media.plugin.manager.get_language_selection(bible)
                    tmp_item_title = re.sub('–', '-', item_title)
                    ref_list = parse_reference(tmp_item_title, bibles[bible], language_selection)
                    if ref_list:
                        bible_media.search_results = bibles[bible].get_verses(ref_list)
                        bible_media.list_view.clear()
                        bible_media.display_results()
                        bible_media.add_to_service()
                    else:
                        log.warning('Could not resolve scripture for %s', item_title)
                elif segment['type'] == 'general':
                    theme_name = self.slide_theme_selection_combo_box.currentText()
                    openlp_id = BreezeCustomImport().add_slide(segment, theme_name)
                    media_type = 'custom'
                    media_type_suffix = 'custom'
                    # TODO: Handle Attachments (images/media) and URL's
                # Don't care about sections, notes or any new types.

                if openlp_id >= 0:
                    segment_id_to_openlp_id[song_id] = openlp_id

                if media_type:
                    media_type_plugin = Registry().get(media_type)
                    # turn on remote song feature to add to service
                    media_type_plugin.remote_triggered = True
                    setattr(media_type_plugin, 'remote_{0}'.format(media_type_suffix), openlp_id)
                    media_type_plugin.add_to_service(remote=openlp_id)

                # End of importing plan segment
                service_manager.main_window.increment_progress_bar()
            service_manager.main_window.finished_progress_bar()
            # select the first item
            segment = service_manager.service_manager_list.topLevelItem(0)
            service_manager.service_manager_list.setCurrentItem(segment)
            service_manager.repaint_service_list(-1, -1)
            service_manager.application.set_normal_cursor()

    def _fetch_events(self):
        log.debug('Fetching Breeze Events')

        today = date.today()
        week_ago = today - timedelta(days=7)
        week_later = today + timedelta(days=7)
        event_list = self.api.get_event_instances(week_ago, week_later)

        return event_list
