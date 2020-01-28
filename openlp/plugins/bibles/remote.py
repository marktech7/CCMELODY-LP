# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                                   #
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
from flask import request, jsonify, Blueprint

from openlp.core.api import app
from openlp.core.api.lib import login_required, extract_request, old_auth
from openlp.core.lib.plugin import PluginStatus
from openlp.core.common.registry import Registry


log = logging.getLogger(__name__)


v1_views = Blueprint('v1-bibles-plugin', __name__)
v2_views = Blueprint('v2-bibles-plugin', __name__)


def search(text):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('bibles')
    if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
        results = plugin.media_item.search(text, False)
        return results
    return None


def live(id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('bibles')
    if plugin.status == PluginStatus.Active and plugin.media_item:
        plugin.media_item.bibles_go_live.emit([id, True])


def add(id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name('bibles')
    if plugin.status == PluginStatus.Active and plugin.media_item:
        item_id = plugin.media_item.create_item_from_id(id)
        plugin.media_item.bibles_add_to_service.emit([item_id, True])


@v2_views.route('/search')
@login_required
def search_bible():
    text = request.args.get('text', '')
    result = search(text)
    if result:
        return jsonify(result)
    return '', 400


@v2_views.route('/live', methods=['POST'])
@login_required
def send_live():
    id = request.json.get('id', -1)
    live(id)
    return '', 204


@v2_views.route('/add', methods=['POST'])
@login_required
def add_to_service():
    id = request.json.get('id', -1)
    add(id)
    return '', 204


# ---------------- DEPRECATED REMOVE AFTER RELEASE --------------
@v1_views.route('/search')
@old_auth
def old_search_bible():
    text = extract_request(request.args.get('data', ''), 'text')
    return jsonify({'results': {'items': search(text)}})


@v1_views.route('/live')
@old_auth
def old_send_live():
    id = extract_request(request.args.get('data', ''), 'id')
    live(id)
    return '', 204


@v1_views.route('/add')
@old_auth
def old_add_to_service():
    id = extract_request(request.args.get('data', ''), 'id')
    add(id)
    return '', 204
# ------------ END DEPRECATED ----------------------------------


def register_views():
    app.register_blueprint(v2_views, url_prefix='/api/v2/plugins/bibles')
    app.register_blueprint(v1_views, url_prefix='/api/bibles')
