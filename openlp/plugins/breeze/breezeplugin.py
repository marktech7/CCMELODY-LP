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
The :mod:`~openlp.plugins.breeze.BreezePlugin` module contains
the Plugin class for the Breeze plugin.
"""
import logging
from typing import Optional

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.lib.ui import create_action
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.breeze.forms.breezeform import BreezeForm
from openlp.plugins.breeze.lib.breezetab import BreezeTab

log = logging.getLogger(__name__)


class BreezePlugin(Plugin):
    """
    This plugin enables the user to import services from Breeze.
    """
    log.info('Breeze Plugin loaded')

    def __init__(self):
        """
        Create and set up the Breeze plugin.
        """
        super(BreezePlugin, self).__init__('breeze', settings_tab_class=BreezeTab)
        self.breeze_form = None
        self.icon = UiIcons().breeze
        self.icon_path = self.icon
        self.weight = -1
        self.username: Optional[str] = None
        self.secret: Optional[str] = None
        self.subdomain: Optional[str] = None
        State().add_service('breeze', self.weight, is_plugin=True)
        State().update_pre_conditions('breeze', self.check_pre_conditions())

    def initialise(self):
        """
        Initialise the plugin
        """
        log.info('Breeze Initialising')
        super(BreezePlugin, self).initialise()
        self.import_breeze.setVisible(True)

    def add_import_menu_item(self, import_menu):
        """
        Add "Breeze Service" to the **Import** menu.

        :param import_menu: The actual **Import** menu item, so that your
        actions can use it as their parent.
        """
        self.import_breeze = create_action(import_menu, 'import_breeze',
                                           text=translate('BreezePlugin', 'Breeze Service Plan'),
                                           visible=False,
                                           statustip=translate('BreezePlugin', 'Import Breeze Service Plan'),
                                           triggers=self.on_import_breeze_triggered
                                           )
        import_menu.addAction(self.import_breeze)

    def on_import_breeze_triggered(self):
        """
        Run the Breeze importer.
        """
        # Determine which dialog to show based on whether the auth values are set yet
        self.username = self.settings.value("breeze/username")
        # TODO: Don't save secret on shared computer
        self.secret = self.settings.value("breeze/secret")
        self.subdomain = self.settings.value("breeze/subdomain")
        if not self.username or not self.secret or not self.subdomain:
            self.breeze_form = Registry().get('settings_form')
            self.breeze_form.exec(translate('BreezePlugin', 'Breeze'))
        else:
            self.breeze_form = BreezeForm(Registry().get('main_window'), self)
            self.breeze_form.exec()

    @staticmethod
    def about():
        """
        Provides information for the plugin manager to display.

        :return: A translatable string with some basic information about the
        Breeze plugin
        """
        return translate('BreezePlugin', '<strong>Breeze Plugin</strong>'
                         '<br />The Breeze plugin provides an interface to import '
                         'service plans from Breeze.')

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('BreezePlugin', 'Breeze',
                                  'name singular'),
            'plural': translate('BreezePlugin', 'Breeze',
                                'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('BreezePlugin', 'Breeze',
                               'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': '',
            'import': translate('BreezePlugin', 'Import All Plan Items '
                                'into Current Service'),
            'new': '',
            'edit': '',
            'delete': '',
            'preview': '',
            'live': '',
            'service': '',
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Tidy up on exit
        """
        log.info('Breeze Finalising')
        self.import_breeze.setVisible(False)
        super(BreezePlugin, self).finalise()
