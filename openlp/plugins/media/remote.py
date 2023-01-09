# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
import logging

from flask import abort, request, Blueprint, jsonify

from openlp.core.api import app
from openlp.core.api.lib import login_required, extract_request, old_auth
from openlp.core.lib.plugin import PluginStatus
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


v1_media = Blueprint('v1-media-plugin', __name__)
v2_media = Blueprint('v2-media-plugin', __name__)


def search(text):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('media')
    if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
        results = plugin.media_item.search(text, False)
        return results
    return None


def live(id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('media')
    if plugin.status == PluginStatus.Active and plugin.media_item:
        plugin.media_item.media_go_live.emit([id, True])


def add(id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('media')
    if plugin.status == PluginStatus.Active and plugin.media_item:
        item_id = plugin.media_item.create_item_from_id(id)
        plugin.media_item.media_add_to_service.emit([item_id, True])


@v2_media.route('/search')
@login_required
def search_view():
    text = request.args.get('text', '')
    result = search(text)
    return jsonify(result)


@v2_media.route('/add', methods=['POST'])
@login_required
def add_view():
    data = request.json
    if not data:
        abort(400)
    id = data.get('id', -1)
    add(id)
    return '', 204


@v2_media.route('/live', methods=['POST'])
@login_required
def live_view():
    data = request.json
    if not data:
        abort(400)
    id = data.get('id', -1)
    live(id)
    return '', 204


# ----------------- DEPRECATED --------------
@v1_media.route('/search')
@old_auth
def old_search():
    text = extract_request(request.args.get('data', ''), 'text')
    return jsonify({'results': {'items': search(text)}})


@v1_media.route('/add')
@old_auth
def old_add():
    id = extract_request(request.args.get('data', ''), 'id')
    add(id)
    return '', 204


@v1_media.route('/live')
@old_auth
def old_live():
    id = extract_request(request.args.get('data', ''), 'id')
    live(id)
    return '', 204
# ---------------- END DEPRECATED ----------------


def register_views():
    app.register_blueprint(v2_media, url_prefix='/api/v2/plugins/media/')
    app.register_blueprint(v1_media, url_prefix='/api/media/')
