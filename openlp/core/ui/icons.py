# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
The :mod:`languages` module provides a list of icons.
"""
import logging

import qtawesome as qta
from PyQt5 import QtGui, QtWidgets

from openlp.core.common import Singleton
from openlp.core.common.applocation import AppLocation
from openlp.core.lib import build_icon


log = logging.getLogger(__name__)


class UiIcons(metaclass=Singleton):
    """
    Provide standard icons for objects to use.
    """
    def __init__(self):
        """
        These are the font icons used in the code.
        """
        font_path = AppLocation.get_directory(AppLocation.AppDir) / 'core' / 'ui' / 'fonts' / 'OpenLP.ttf'
        charmap_path = AppLocation.get_directory(AppLocation.AppDir) / 'core' / 'ui' / 'fonts' / 'openlp-charmap.json'
        qta.load_font('op', font_path, charmap_path)
        palette = QtWidgets.QApplication.palette()
        qta.set_defaults(color=palette.color(QtGui.QPalette.Active,
                                             QtGui.QPalette.ButtonText),
                         color_disabled=palette.color(QtGui.QPalette.Disabled,
                                                      QtGui.QPalette.ButtonText))
        icon_list = {
            'active': {'icon': 'fa.child'},
            'add': {'icon': 'fa.plus-circle'},
            'alert': {'icon': 'fa.exclamation-triangle'},
            'arrow_down': {'icon': 'fa.arrow-down'},
            'arrow_left': {'icon': 'fa.arrow-left'},
            'arrow_right': {'icon': 'fa.arrow-right'},
            'arrow_up': {'icon': 'fa.arrow-up'},
            'audio': {'icon': 'fa.file-sound-o'},
            'authentication': {'icon': 'fa.exclamation-triangle', 'attr': 'red'},
            'address': {'icon': 'fa.book'},
            'back': {'icon': 'fa.step-backward'},
            'backspace': {'icon': 'mdi.backspace-outline'},
            'bible': {'icon': 'fa.book'},
            'blank': {'icon': 'fa.times-circle'},
            'blank_theme': {'icon': 'fa.file-image-o'},
            'bold': {'icon': 'fa.bold'},
            'book': {'icon': 'fa.book'},
            'bottom': {'icon': 'fa.angle-double-down'},
            'box': {'icon': 'fa.briefcase'},
            'clapperboard': {'icon': 'fa.film'},
            'clock': {'icon': 'fa.clock-o'},
            'clone': {'icon': 'fa.clone'},
            'close': {'icon': 'fa.times-circle-o'},
            'copy': {'icon': 'fa.copy'},
            'copyright': {'icon': 'fa.copyright'},
            'database': {'icon': 'fa.database'},
            'default': {'icon': 'fa.info-circle'},
            'desktop': {'icon': 'fa.desktop'},
            'delete': {'icon': 'fa.trash'},
            'download': {'icon': 'fa.download'},
            'edit': {'icon': 'fa.edit'},
            'email': {'icon': 'fa.envelope'},
            'error': {'icon': 'fa.exclamation', 'attr': 'red'},
            'exception': {'icon': 'fa.times-circle'},
            'exit': {'icon': 'fa.sign-out'},
            'group': {'icon': 'fa.object-group'},
            'inactive': {'icon': 'fa.child', 'attr': 'lightGray'},
            'info': {'icon': 'fa.info'},
            'italic': {'icon': 'fa.italic'},
            'light_bulb': {'icon': 'fa.lightbulb-o'},
            'live': {'icon': 'fa.eye'},
            'manual': {'icon': 'fa.graduation-cap'},
            'media': {'icon': 'fa.fax'},
            'minus': {'icon': 'fa.minus'},
            'music': {'icon': 'fa.music'},
            'new': {'icon': 'fa.file'},
            'new_group': {'icon': 'fa.folder'},
            'notes': {'icon': 'fa.sticky-note'},
            'open': {'icon': 'fa.folder-open'},
            'optical': {'icon': 'fa.file-video-o'},
            'pause': {'icon': 'fa.pause'},
            'planning_center': {'icon': 'fa.cloud-download'},
            'play': {'icon': 'fa.play'},
            'player': {'icon': 'fa.tablet'},
            'plugin_list': {'icon': 'fa.puzzle-piece'},
            'plus': {'icon': 'fa.plus'},
            'presentation': {'icon': 'fa.bar-chart'},
            'preview': {'icon': 'fa.laptop'},
            'projector': {'icon': 'op.video'},
            'projector_connect': {'icon': 'fa.plug'},  # Projector connect
            'projector_cooldown': {'icon': 'fa.video-camera', 'attr': 'blue'},
            'projector_disconnect': {'icon': 'fa.plug', 'attr': 'lightGray'},  # Projector disconnect
            'projector_error': {'icon': 'fa.video-camera', 'attr': 'red'},
            'projector_hdmi': {'icon': 'op.hdmi'},
            'projector_power_off': {'icon': 'fa.video-camera', 'attr': 'red'},  # Toolbar power off
            'projector_power_on': {'icon': 'fa.video-camera', 'attr': 'green'},  # Toolbar power on
            'projector_off': {'icon': 'fa.video-camera', 'attr': 'black'},  # Projector off
            'projector_on': {'icon': 'fa.video-camera', 'attr': 'green'},  # Projector on
            'projector_select_connect': {'icon': 'fa.plug', 'attr': 'green'},  # Toolbar connect
            'projector_select_disconnect': {'icon': 'fa.plug', 'attr': 'red'},  # Toolbar disconnect
            'projector_warmup': {'icon': 'fa.video-camera', 'attr': 'yellow'},
            'picture': {'icon': 'fa.picture-o'},
            'print': {'icon': 'fa.print'},
            'remote': {'icon': 'fa.rss'},
            'repeat': {'icon': 'fa.repeat'},
            'save': {'icon': 'fa.save'},
            'search': {'icon': 'fa.search'},
            'search_ccli': {'icon': 'op.search-CCLI'},
            'search_comb': {'icon': 'fa.columns'},
            'search_lyrcs': {'icon': 'op.search-lyrcs'},
            'search_minus': {'icon': 'fa.search-minus'},
            'search_plus': {'icon': 'fa.search-plus'},
            'search_ref': {'icon': 'fa.institution'},
            'search_text': {'icon': 'op.search-text'},
            'select_all': {'icon': 'fa.check-square-o'},
            'select_none': {'icon': 'fa.square-o'},
            'settings': {'icon': 'fa.cogs'},
            'shortcuts': {'icon': 'fa.wrench'},
            'song_usage': {'icon': 'fa.line-chart'},
            'song_usage_active': {'icon': 'op.plus_sign'},
            'song_usage_inactive': {'icon': 'op.minus_sign'},
            'sort': {'icon': 'fa.sort'},
            'stop': {'icon': 'fa.stop'},
            'square': {'icon': 'fa.square'},
            'text': {'icon': 'op.file-text'},
            'time': {'icon': 'fa.history'},
            'theme': {'icon': 'fa.paint-brush'},
            'top': {'icon': 'fa.angle-double-up'},
            'undo': {'icon': 'fa.undo'},
            'upload': {'icon': 'fa.upload'},
            'user': {'icon': 'fa.user'},
            'usermo': {'icon': 'op.users'},
            'users': {'icon': 'fa.users'},
            'video': {'icon': 'fa.file-video-o'},
            'volunteer': {'icon': 'fa.group'}
        }
        self.load_icons(icon_list)
        self.main_icon = build_icon(':/icon/openlp-logo.svg')

    def load_icons(self, icon_list):
        """
        Load the list of icons to be processed
        """
        for key in icon_list:
            try:
                icon = icon_list[key]['icon']
                try:
                    attr = icon_list[key]['attr']
                    setattr(self, key, qta.icon(icon, color=attr))
                except KeyError:
                    setattr(self, key, qta.icon(icon))
                except Exception:
                    import sys
                    log.error('Unexpected error: %s' % sys.exc_info())
                    setattr(self, key, qta.icon('fa.plus-circle', color='red'))
            except Exception:
                setattr(self, key, qta.icon('fa.plus-circle', color='red'))

    @staticmethod
    def _print_icons():
        """
        Have ability to dump icons to see what is actually available.  Can only run within an application
        :return:
        """
        ico = qta._resource['iconic']
        fa = ico.charmap['fa']
        for ky in fa.keys():
            print(ky, fa[ky])
