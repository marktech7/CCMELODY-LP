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
import os
import urllib.request
from pathlib import Path

from openlp.core.api.lib import login_required
from openlp.core.common import ThemeLevel
from openlp.core.common.registry import Registry
from openlp.core.common.applocation import AppLocation
from openlp.core.lib import create_thumb
from openlp.core.lib.serviceitem import ItemCapabilities

from flask import jsonify, request, abort, Blueprint

controller_views = Blueprint('controller', __name__)


@controller_views.route('/live-item')
def controller_text_api():
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    data = []
    if current_item:
        for index, frame in enumerate(current_item.get_frames()):
            item = {}
            item['tag'] = index + 1
            item['selected'] = live_controller.selected_row == index
            item['title'] = current_item.title
            if current_item.is_text():
                if frame['verse']:
                    item['tag'] = str(frame['verse'])
                item['chords_text'] = str(frame.get('chords_text', ''))
                item['text'] = frame['text']
                item['html'] = current_item.get_rendered_frame(index)
            elif current_item.is_image() and not frame.get('image', '') and \
                    Registry().get('settings_thread').value('api/thumbnails'):
                thumbnail_path = os.path.join('images', 'thumbnails', frame['title'])
                print('AAA')
                print(current_item.name)
                print(frame['title'])
                full_thumbnail_path = AppLocation.get_data_path() / thumbnail_path
                if not full_thumbnail_path.exists():
                    create_thumb(Path(current_item.get_frame_path(index)), full_thumbnail_path, False)
                # Registry().get('image_manager').add_image(str(full_thumbnail_path), frame['title'], None, 88, 88)
                item['img'] = urllib.request.pathname2url(os.path.sep + str(thumbnail_path))
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            else:
                # presentations and other things
                if current_item.is_capable(ItemCapabilities.HasDisplayTitle):
                    item['title'] = str(frame['display_title'])
                if current_item.is_capable(ItemCapabilities.HasNotes):
                    item['slide_notes'] = str(frame['notes'])
                if current_item.is_capable(ItemCapabilities.HasThumbnails) and \
                        Registry().get('settings_thread').value('api/thumbnails'):
                    # If the file is under our app directory tree send the portion after the match
                    print('BBB')
                    print(current_item.name)
                    print(frame['title'])
                    data_path = str(AppLocation.get_data_path())
                    if frame['image'][0:len(data_path)] == data_path:
                        item['img'] = urllib.request.pathname2url(frame['image'][len(data_path):])
                    # Registry().get('image_manager').add_image(frame['image'], frame['title'], None, 88, 88)
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            data.append(item)
    return jsonify(data)


@controller_views.route('/show', methods=['POST'])
@login_required
def controller_set():
    data = request.json
    if not data:
        abort(400)
    num = data.get('id', -1)
    Registry().get('live_controller').slidecontroller_live_set.emit([num])
    return '', 204


@controller_views.route('/progress', methods=['POST'])
@login_required
def controller_direction():
    ALLOWED_ACTIONS = ['next', 'previous']
    data = request.json
    if not data:
        abort(400)
    action = data.get('action', '').lower()
    if action not in ALLOWED_ACTIONS:
        abort(400)
    getattr(Registry().get('live_controller'), 'slidecontroller_live_{action}'.
            format(action=action)).emit()
    return '', 204


@controller_views.route('/theme-level', methods=['GET'])
@login_required
def get_theme_level():
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
    data = request.json
    if not data:
        abort(400)

    theme_level = ''
    try:
        theme_level = str(data.get("level"))
    except ValueError:
        abort(400)

    if theme_level == 'global':
        Registry().get('settings').setValue('themes/theme level', 1)
    elif theme_level == 'service':
        Registry().get('settings').setValue('themes/theme level', 2)
    elif theme_level == 'song':
        Registry().get('settings').setValue('theme/theme level', 3)
    else:
        abort(400)

    return '', 204


@controller_views.route('/themes', methods=['GET'])
@login_required
def get_themes():
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
        pass

    return jsonify(theme_list)


@controller_views.route('/theme', methods=['POST'])
@login_required
def set_theme():
    data = request.json
    theme = ''
    theme_level = Registry().get('settings').value('themes/theme level')

    if not data:
        abort(400)
    try:
        theme = str(data.get('theme'))
    except ValueError:
        abort(400)

    if theme_level == ThemeLevel.Global:
        Registry().get('settings').setValue('themes/global theme', theme)
        Registry().execute('theme_update_global')
    elif theme_level == ThemeLevel.Service:
        Registry().get('settings').setValue('servicemanager/service theme', theme)
        Registry().execute('theme_update_service')
    elif theme_level == ThemeLevel.Song:
        return '', 501

    return '', 204
