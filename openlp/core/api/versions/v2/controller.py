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
import logging

from openlp.core.api.lib import login_required
from openlp.core.common import ThemeLevel
from openlp.core.common.registry import Registry

from flask import jsonify, request, abort, Blueprint

controller_views = Blueprint('controller', __name__)
log = logging.getLogger(__name__)


@controller_views.route('/live-item')
def controller_text_api():
    log.debug('controller-v2-live-item')
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    live_item = {}
    if current_item:
        live_item = current_item.to_dict()
        live_item['slides'][live_controller.selected_row]['selected'] = True
    return jsonify(live_item)


@controller_views.route('/show', methods=['POST'])
@login_required
def controller_set():
    log.debug('controller-v2-show-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    num = data.get('id', -1)
    Registry().get('live_controller').slidecontroller_live_set.emit([num])
    return '', 204


@controller_views.route('/progress', methods=['POST'])
@login_required
def controller_direction():
    log.debug('controller-v2-progress-post')
    ALLOWED_ACTIONS = ['next', 'previous']
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    action = data.get('action', '').lower()
    if action not in ALLOWED_ACTIONS:
        log.error('Invalid action passed ' + action)
        abort(400)
    getattr(Registry().get('live_controller'), 'slidecontroller_live_{action}'.
            format(action=action)).emit()
    return '', 204


@controller_views.route('/theme-level', methods=['GET'])
@login_required
def get_theme_level():
    log.debug('controller-v2-theme-level-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    if theme_level == ThemeLevel.Global:
        theme_level = 'global'
    elif theme_level == ThemeLevel.Service:
        theme_level = 'service'
    elif theme_level == ThemeLevel.Song:
        theme_level = 'song'
    return jsonify(theme_level)


@controller_views.route('/theme-level', methods=['POST'])
@login_required
def set_theme_level():
    log.debug('controller-v2-theme-level-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    theme_level = ''
    try:
        theme_level = str(data.get("level"))
    except ValueError:
        log.error('Invalid data passed ' + theme_level)
        abort(400)
    if theme_level == 'global':
        Registry().get('settings').setValue('themes/theme level', 1)
        Registry().execute('theme_update_global')
    elif theme_level == 'service':
        Registry().get('settings').setValue('themes/theme level', 2)
        Registry().execute('theme_update_service')
    elif theme_level == 'song':
        Registry().get('settings').setValue('themes/theme level', 3)
        Registry().execute('theme_update_global')
    else:
        log.error('Unsupported data passed ' + theme_level)
        abort(400)
    return '', 204


@controller_views.route('/themes', methods=['GET'])
@login_required
def get_themes():
    log.debug('controller-v2-themes-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    theme_list = []
    current_theme = ''
    if theme_level == ThemeLevel.Global:
        current_theme = Registry().get('theme_manager').global_theme
    if theme_level == ThemeLevel.Service:
        current_theme = Registry().get('service_manager').service_theme
    # Gets and appends theme list
    themes = Registry().execute('get_theme_names')
    try:
        for theme in themes[0]:
            theme_list.append({
                'name': theme,
                'selected': False
            })
        for i in theme_list:
            if i["name"] == current_theme:
                i["selected"] = True
    except IndexError:
        log.error('Missing theme passed ' + str(themes))
        pass
    return jsonify(theme_list)


@controller_views.route('/theme', methods=['GET'])
@login_required
def get_theme():
    """
    Get the current theme
    """
    log.debug('controller-v2-theme-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    if theme_level == ThemeLevel.Service:
        theme = Registry().get('settings').value('servicemanager/service theme')
    else:
        theme = Registry().get('settings').value('themes/global theme')
    return jsonify(theme)


@controller_views.route('/theme', methods=['POST'])
@login_required
def set_theme():
    log.debug('controller-v2-themes-post')
    data = request.json
    theme = ''
    theme_level = Registry().get('settings').value('themes/theme level')
    if not data:
        log.error('Missing request data')
        abort(400)
    try:
        theme = str(data.get('theme'))
    except ValueError:
        log.error('Invalid data passed ' + theme)
        abort(400)
    if theme_level == ThemeLevel.Global:
        Registry().get('settings').setValue('themes/global theme', theme)
        Registry().execute('theme_update_global')
    elif theme_level == ThemeLevel.Service:
        Registry().get('settings').setValue('servicemanager/service theme', theme)
        Registry().execute('theme_update_service')
    elif theme_level == ThemeLevel.Song:
        log.error('Unimplemented method')
        return '', 501
    return '', 204


@controller_views.route('/clear/<controller>', methods=['POST'])
@login_required
def controller_clear(controller):
    """
    Clears the slide controller display
    :param controller: the Live or Preview controller
    :return: HTTP return code
    """
    log.debug(f'controller-v2-clear-get {controller}')
    if controller in ['live', 'preview']:
        getattr(Registry().get(f'{controller}_controller'), f'slidecontroller_{controller}_clear').emit()
        return '', 204
    else:
        return '', 404
