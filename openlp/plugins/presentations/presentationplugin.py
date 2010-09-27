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
"""
The :mod:`presentationplugin` module provides the ability for OpenLP to display
presentations from a variety of document formats.
"""
import os
import logging

from openlp.core.lib import Plugin, StringContent, build_icon, translate
from openlp.core.utils import AppLocation
from openlp.plugins.presentations.lib import PresentationController, \
    PresentationMediaItem, PresentationTab

log = logging.getLogger(__name__)

class PresentationPlugin(Plugin):
    """
    This plugin allowed a Presentation to be opened, controlled and displayed
    on the output display. The plugin controls third party applications such
    as OpenOffice.org Impress, Microsoft PowerPoint and the PowerPoint viewer
    """
    log = logging.getLogger(u'PresentationPlugin')

    def __init__(self, plugin_helpers):
        """
        PluginPresentation constructor.
        """
        log.debug(u'Initialised')
        self.controllers = {}
        Plugin.__init__(self, u'Presentations', u'1.9.3', plugin_helpers)
        self.weight = -8
        self.icon_path = u':/plugins/plugin_presentations.png'
        self.icon = build_icon(self.icon_path)

    def getSettingsTab(self):
        """
        Create the settings Tab
        """
        visible_name = self.getString(StringContent.VisibleName)
        return PresentationTab(self.name, visible_name[u'title'], self.controllers)

    def initialise(self):
        """
        Initialise the plugin. Determine which controllers are enabled
        are start their processes.
        """
        log.info(u'Presentations Initialising')
        Plugin.initialise(self)
        self.insertToolboxItem()
        for controller in self.controllers:
            if self.controllers[controller].enabled():
                self.controllers[controller].start_process()
        self.mediaItem.buildFileMaskString()

    def finalise(self):
        """
        Finalise the plugin. Ask all the enabled presentation applications
        to close down their applications and release resources.
        """
        log.info(u'Plugin Finalise')
        #Ask each controller to tidy up
        for key in self.controllers:
            controller = self.controllers[key]
            if controller.enabled():
                controller.kill()
        Plugin.finalise(self)

    def getMediaManagerItem(self):
        """
        Create the Media Manager List
        """
        return PresentationMediaItem(
            self, self.icon, self.name, self.controllers)

    def registerControllers(self, controller):
        """
        Register each presentation controller (Impress, PPT etc) and
        store for later use
        """
        self.controllers[controller.name] = controller

    def checkPreConditions(self):
        """
        Check to see if we have any presentation software available
        If Not do not install the plugin.
        """
        log.debug(u'checkPreConditions')
        controller_dir = os.path.join(
            AppLocation.get_directory(AppLocation.PluginsDir),
            u'presentations', u'lib')
        for filename in os.listdir(controller_dir):
            if filename.endswith(u'controller.py') and \
                not filename == 'presentationcontroller.py':
                path = os.path.join(controller_dir, filename)
                if os.path.isfile(path):
                    modulename = u'openlp.plugins.presentations.lib.' + \
                        os.path.splitext(filename)[0]
                    log.debug(u'Importing controller %s', modulename)
                    try:
                        __import__(modulename, globals(), locals(), [])
                    except ImportError:
                        log.exception(u'Failed to import %s on path %s',
                            modulename, path)
        controller_classes = PresentationController.__subclasses__()
        for controller_class in controller_classes:
            controller = controller_class(self)
            self.registerControllers(controller)
        if self.controllers:
            return True
        else:
            return False

    def about(self):
        """
        Return information about this plugin
        """
        about_text = translate('PresentationPlugin', '<strong>Presentation '
            'Plugin</strong><br />The presentation plugin provides the '
            'ability to show presentations using a number of different '
            'programs. The choice of available presentation programs is '
            'available to the user in a drop down box.')
        return about_text

    def setPluginTextStrings(self):
        """
        Called to define all translatable texts of the plugin
        """
        ## Name PluginList ##
        self.text_strings[StringContent.Name] = {
            u'singular': translate('PresentationPlugin', 'Presentation'),
            u'plural': translate('PresentationPlugin', 'Presentations')
        }
        ## Name for MediaDockManager, SettingsManager ##
        self.text_strings[StringContent.VisibleName] = {
            u'title': translate('PresentationPlugin', 'Presentations')
        }
        # Middle Header Bar
        ## Load Button ##
        self.text_strings[StringContent.Load] = {
            u'title': translate('PresentationPlugin', 'Load'),
            u'tooltip': translate('PresentationPlugin', 'Load a new Presentation')
        }
        ## Delete Button ##
        self.text_strings[StringContent.Delete] = {
            u'title': translate('PresentationPlugin', 'Delete'),
            u'tooltip': translate('PresentationPlugin', 'Delete the selected Presentation')
        }
        ## Preview ##
        self.text_strings[StringContent.Preview] = {
            u'title': translate('PresentationPlugin', 'Preview'),
            u'tooltip': translate('PresentationPlugin', 'Preview the selected Presentation')
        }
        ## Live  Button ##
        self.text_strings[StringContent.Live] = {
            u'title': translate('PresentationPlugin', 'Live'),
            u'tooltip': translate('PresentationPlugin', 'Send the selected Presentation live')
        }
        ## Add to service Button ##
        self.text_strings[StringContent.Service] = {
            u'title': translate('PresentationPlugin', 'Service'),
            u'tooltip': translate('PresentationPlugin', 'Add the selected Presentation to the service')
        }