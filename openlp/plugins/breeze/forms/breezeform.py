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
import logging
import re
import time
from datetime import date, datetime, timedelta

from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.plugins.bibles.lib import parse_reference
from openlp.plugins.breeze.forms.selectserviceplandialog import Ui_SelectPlanDialog
from openlp.plugins.breeze.lib.customimport import BreezeCustomImport
from openlp.plugins.breeze.lib.breeze_api import BreezeAPI
from openlp.plugins.breeze.lib.songimport import BreezeSongImport

log = logging.getLogger(__name__)


class BreezeForm(QtWidgets.QDialog, Ui_SelectPlanDialog):
    """
    The :class:`SelectServicePlanForm` class is the main Breeze dialog.
    """

    def __init__(self, parent=None, plugin=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.plugin = plugin
        # create Breeze API Object
        username = Registry().get('settings').value("breeze/username")
        secret = Registry().get('settings').value("breeze/secret")
        subdomain = Registry().get('settings').value("breeze/subdomain")
        token = Registry().get('settings').value("breeze/token")
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
        today = date.today()
        week_ago = today - timedelta(days=7)
        week_later = today + timedelta(days=7)
        event_list = self.api.get_event_instances(week_ago, week_later)
        self.plan_selection_combo_box.clear()
        self.plan_selection_combo_box.addItem('Select Service Plan Date')
        self.plan_selection_combo_box.setCurrentIndex(0)
        # Get Today's date and see if it is listed... if it is, then select it in the combobox

        for event in event_list:
            # start_datetime=str: 2023-09-26 00:00:00
            plan_datetime = datetime.strptime(event['start'], '%Y-%m-%d %H:%M:%S')
            plan_date = date(plan_datetime.year, plan_datetime.month, plan_datetime.day)
            self.plan_selection_combo_box.addItem("{0} ({1})".format(
                event['name'],
                plan_date.strftime("%Y-%m-%d")
            ), event['service_plan_id'])
            # if we have any date that matches today or in the future, select it
            if plan_date >= today:
                self.plan_selection_combo_box.setCurrentIndex(self.plan_selection_combo_box.count() - 1)
                self.import_as_new_button.setEnabled(True)
                self.update_existing_button.setEnabled(True)
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
        old_service_items = []
        if update:
            old_service_items = service_manager.service_items.copy()
            service_manager.new_file()
        else:
            service_manager.on_new_service_clicked()
        # we only continue here if the service_manager is now empty
        if len(service_manager.service_items) == 0:
            service_manager.application.set_busy_cursor()
            # get the plan ID for the current plan selection
            service_plan_id = self.plan_selection_combo_box.itemData(self.plan_selection_combo_box.currentIndex())
            # get the items array from Planning Center
            service_plan_items_dict = self.api.get_service_plan(service_plan_id)
            segments = service_plan_items_dict["segments"]
            service_manager.main_window.display_progress_bar(len(segments))
            # convert the planning center dict to Songs and Add them to the ServiceManager
            service_plan_id_to_openlp_id = {}
            for segment in segments:
                item_title = segment['attributes']['title']
                media_type = ''
                openlp_id = -1
                if segment['type'] == 'song':
                    arrangement_id = segment['relationships']['arrangement']['data']['id']
                    song_id = segment['relationships']['song']['data']['id']
                    if song_id not in service_plan_id_to_openlp_id:
                        # TODO: Waiting for Breeze Service Plan Songs
                        # get arrangement from "included" resources
                        arrangement_data = {}
                        song_data = {}
                        for included_item in service_plan_items_dict['included']:
                            if included_item['type'] == 'Song' and included_item['id'] == song_id:
                                song_data = included_item
                            elif included_item['type'] == 'Arrangement' and included_item['id'] == arrangement_id:
                                arrangement_data = included_item
                            # if we have both song and arrangement set, stop iterating
                            if len(song_data) and len(arrangement_data):
                                break
                        author = song_data['attributes']['author']
                        lyrics = arrangement_data['attributes']['lyrics']
                        arrangement_updated_at = datetime.strptime(arrangement_data['attributes']['updated_at'].
                                                                   rstrip("Z"), '%Y-%m-%dT%H:%M:%S')
                        # start importing the song
                        breeze_import = BreezeSongImport()
                        theme_name = self.song_theme_selection_combo_box.currentText()
                        openlp_id = breeze_import.add_song(item_title, author, lyrics,
                                                                    theme_name, arrangement_updated_at)
                        service_plan_id_to_openlp_id[song_id] = openlp_id
                    openlp_id = service_plan_id_to_openlp_id[song_id]
                    media_type = 'songs'
                    # TODO: Handle the other types (Scripture, note, general)
                # add the media to the service
                media_type_plugin = Registry().get(media_type)
                # the variable suffix names below for "songs" is "song", so change media_type to song
                media_type_suffix = media_type
                if media_type == 'songs':
                    media_type_suffix = 'song'
                # turn on remote song feature to add to service
                media_type_plugin.remote_triggered = True
                setattr(media_type_plugin, "remote_{0}".format(media_type_suffix), openlp_id)
                media_type_plugin.add_to_service(remote=openlp_id)
                # also add verse references if they are there
                if media_type == 'custom' and not html_details:
                    # check if the slide title is also a verse reference
                    # get a reference to the bible manager
                    bible_media = Registry().get('bibles')
                    bibles = bible_media.plugin.manager.get_bibles()
                    # get the current bible selected from the bibles plugin screen
                    bible = bible_media.version_combo_box.currentText()
                    if len(bible) == 0 and len(bibles) > 0:
                        # if we have no bible in the version_combo_box, but we have
                        # one or more bibles available, use one of those
                        bible = next(iter(bibles))
                    language_selection = bible_media.plugin.manager.get_language_selection(bible)
                    # replace long dashes with normal dashes -- why do these get inserted in PCO?
                    tmp_item_title = re.sub('–', '-', item_title)
                    ref_list = parse_reference(tmp_item_title, bibles[bible], language_selection)
                    if ref_list:
                        bible_media.search_results = bibles[bible].get_verses(ref_list)
                        bible_media.list_view.clear()
                        bible_media.display_results()
                        bible_media.add_to_service()
                service_manager.main_window.increment_progress_bar()
            if update:
                for old_service_item in old_service_items:
                    # see if this service_item contained within the current set of service items
                    # see if we have this same value in the new service
                    for service_index, service_item in enumerate(service_manager.service_items):
                        # we can compare songs to songs and custom to custom but not between them
                        if old_service_item['service_item'].name == 'songs' and \
                                service_item['service_item'].name == 'songs':
                            if old_service_item['service_item'].audit == service_item['service_item'].audit:
                                # get the timestamp from the xml of both the old and new and compare...
                                # modifiedDate="2018-06-30T18:44:35Z"
                                old_match = re.search('modifiedDate="(.+?)Z*"',
                                                      old_service_item['service_item'].xml_version)
                                old_datetime = datetime.strptime(old_match.group(1), '%Y-%m-%dT%H:%M:%S')
                                new_match = re.search('modifiedDate="(.+?)Z*"',
                                                      service_item['service_item'].xml_version)
                                new_datetime = datetime.strptime(new_match.group(1), '%Y-%m-%dT%H:%M:%S')
                                # if old timestamp is more recent than new, then copy old to new
                                if old_datetime > new_datetime:
                                    service_manager.service_items[service_index] = old_service_item
                                break
                        elif old_service_item['service_item'].name == 'custom' and \
                                service_item['service_item'].name == 'custom':
                            """ we don't get actual slide content from the V2 PC API, so all we create by default is a
                            single slide with matching title and content.  If the content
                            is different between the old serviceitem (previously imported
                            from PC and the new content that we are importing now, then
                            the assumption is that we updated this content and we want to
                            keep the old content after this update.  If we actually updated
                            something on the PC site in this slide, it would have a
                            different title because that is all we can get the v2API """
                            if old_service_item['service_item'].title == service_item['service_item'].title:
                                if old_service_item['service_item'].slides != service_item['service_item'].slides:
                                    service_manager.service_items[service_index] = old_service_item
                                break
            service_manager.main_window.finished_progress_bar()
            # select the first item
            segment = service_manager.service_manager_list.topLevelItem(0)
            service_manager.service_manager_list.setCurrentItem(segment)
            service_manager.repaint_service_list(-1, -1)
            service_manager.application.set_normal_cursor()
