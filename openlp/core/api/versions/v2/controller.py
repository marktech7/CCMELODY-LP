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
                    Registry().get('settings').value('api/thumbnails'):
                thumbnail_path = os.path.join('images', 'thumbnails', frame['title'])
                full_thumbnail_path = AppLocation.get_data_path() / thumbnail_path
                if not full_thumbnail_path.exists():
                    create_thumb(Path(current_item.get_frame_path(index)), full_thumbnail_path, False)
                Registry().get('image_manager').add_image(str(full_thumbnail_path), frame['title'], None, 88, 88)
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
                        Registry().get('settings').value('api/thumbnails'):
                    # If the file is under our app directory tree send the portion after the match
                    data_path = str(AppLocation.get_data_path())
                    if frame['image'][0:len(data_path)] == data_path:
                        item['img'] = urllib.request.pathname2url(frame['image'][len(data_path):])
                    Registry().get('image_manager').add_image(frame['image'], frame['title'], None, 88, 88)
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
