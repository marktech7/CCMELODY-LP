# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Meinert Jordan, Andreas Preikschat, Christian      #
# Richter, Philip Ridout, Maikel Stuivenberg, Martin Thompson, Jon Tibble,    #
# Carsten Tinggaard, Frode Woldsund                                           #
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

import logging

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Plugin, StringContent, build_icon, translate
from openlp.plugins.bibles.lib import BibleManager, BiblesTab, BibleMediaItem

log = logging.getLogger(__name__)

class BiblePlugin(Plugin):
    log.info(u'Bible Plugin loaded')

    def __init__(self, plugin_helpers):
        Plugin.__init__(self, u'Bibles', u'1.9.3', plugin_helpers)
        self.weight = -9
        self.icon_path = u':/plugins/plugin_bibles.png'
        self.icon = build_icon(self.icon_path)
        self.manager = None

    def initialise(self):
        log.info(u'bibles Initialising')
        if self.manager is None:
            self.manager = BibleManager(self)
        Plugin.initialise(self)
        self.importBibleItem.setVisible(True)
        self.exportBibleItem.setVisible(True)

    def finalise(self):
        log.info(u'Plugin Finalise')
        Plugin.finalise(self)
        self.importBibleItem.setVisible(False)
        self.exportBibleItem.setVisible(False)

    def getSettingsTab(self):
        visible_name = self.getString(StringContent.VisibleName)
        return BiblesTab(self.name, visible_name[u'title'])

    def getMediaManagerItem(self):
        # Create the BibleManagerItem object.
        return BibleMediaItem(self, self, self.icon)

    def addImportMenuItem(self, import_menu):
        self.importBibleItem = QtGui.QAction(import_menu)
        self.importBibleItem.setObjectName(u'importBibleItem')
        import_menu.addAction(self.importBibleItem)
        self.importBibleItem.setText(
            translate('BiblesPlugin', '&Bible'))
        # signals and slots
        QtCore.QObject.connect(self.importBibleItem,
            QtCore.SIGNAL(u'triggered()'), self.onBibleImportClick)
        self.importBibleItem.setVisible(False)

    def addExportMenuItem(self, export_menu):
        self.exportBibleItem = QtGui.QAction(export_menu)
        self.exportBibleItem.setObjectName(u'exportBibleItem')
        export_menu.addAction(self.exportBibleItem)
        self.exportBibleItem.setText(translate(
            'BiblesPlugin', '&Bible'))
        self.exportBibleItem.setVisible(False)

    def onBibleImportClick(self):
        if self.mediaItem:
            self.mediaItem.onImportClick()

    def about(self):
        about_text = translate('BiblesPlugin', '<strong>Bible Plugin</strong>'
            '<br />The Bible plugin provides the ability to display bible '
            'verses from different sources during the service.')
        return about_text

    def usesTheme(self, theme):
        """
        Called to find out if the bible plugin is currently using a theme.

        Returns True if the theme is being used, otherwise returns False.
        """
        if self.settings_tab.bible_theme == theme:
            return True
        return False

    def renameTheme(self, oldTheme, newTheme):
        """
        Rename the theme the bible plugin is using making the plugin use the
        new name.

        ``oldTheme``
            The name of the theme the plugin should stop using. Unused for
            this particular plugin.

        ``newTheme``
            The new name the plugin should now use.
        """
        self.settings_tab.bible_theme = newTheme

    def setPluginTextStrings(self):
        """
        Called to define all translatable texts of the plugin
        """
        ## Name PluginList ##
        self.text_strings[StringContent.Name] = {
            u'singular': translate('BiblesPlugin', 'Bible'),
            u'plural': translate('BiblesPlugin', 'Bibles')
        }
        ## Name for MediaDockManager, SettingsManager ##
        self.text_strings[StringContent.VisibleName] = {
            u'title': translate('BiblesPlugin', 'Bibles')
        }
        # Middle Header Bar
        ## Import Button ##
        self.text_strings[StringContent.Import] = {
            u'title': translate('BiblesPlugin', 'Import'),
            u'tooltip': translate('BiblesPlugin', 'Import a Bible')
        }
        ## New Button ##
        self.text_strings[StringContent.New] = {
            u'title': translate('BiblesPlugin', 'Add'),
            u'tooltip': translate('BiblesPlugin', 'Add a new Bible')
        }
        ## Edit Button ##
        self.text_strings[StringContent.Edit] = {
            u'title': translate('BiblesPlugin', 'Edit'),
            u'tooltip': translate('BiblesPlugin', 'Edit the selected Bible')
        }
        ## Delete Button ##
        self.text_strings[StringContent.Delete] = {
            u'title': translate('BiblesPlugin', 'Delete'),
            u'tooltip': translate('BiblesPlugin', 'Delete the selected Bible')
        }
        ## Preview ##
        self.text_strings[StringContent.Preview] = {
            u'title': translate('BiblesPlugin', 'Preview'),
            u'tooltip': translate('BiblesPlugin', 'Preview the selected Bible')
        }
        ## Live  Button ##
        self.text_strings[StringContent.Live] = {
            u'title': translate('BiblesPlugin', 'Live'),
            u'tooltip': translate('BiblesPlugin', 'Send the selected Bible live')
        }
        ## Add to service Button ##
        self.text_strings[StringContent.Service] = {
            u'title': translate('BiblesPlugin', 'Service'),
            u'tooltip': translate('BiblesPlugin', 'Add the selected Bible to the service')
        }