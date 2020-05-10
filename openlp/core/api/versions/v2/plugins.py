# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                                   #
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

from flask import abort, request, Blueprint, jsonify

from openlp.core.api.lib import login_required
from openlp.core.lib.plugin import PluginStatus
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


plugins = Blueprint('v2-plugins', __name__)


def search(plugin, text):
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin)
    if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
        results = plugin.media_item.search(text, False)
        return results
    return None


def live(plugin, id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin)
    if plugin.status == PluginStatus.Active and plugin.media_item:
        plugin.media_item.songs_go_live.emit([id, True])


def add(plugin, id):
    plugin = Registry().get('plugin_manager').get_plugin_by_name(plugin)
    if plugin.status == PluginStatus.Active and plugin.media_item:
        item_id = plugin.media_item.create_item_from_id(id)
        plugin.media_item.songs_add_to_service.emit([item_id, True])


@plugins.route('/<plugin>/search')
@login_required
def search_view(plugin):
    text = request.args.get('text', '')
    result = search(plugin, text)
    return jsonify(result)


@plugins.route('/<plugin>/add', methods=['POST'])
@login_required
def add_view(plugin):
    data = request.json
    if not data:
        abort(400)
    id = data.get('id', -1)
    add(plugin, id)
    return '', 204


@plugins.route('/<plugin>/live', methods=['POST'])
@login_required
def live_view(plugin):
    data = request.json
    if not data:
        abort(400)
    id = data.get('id', -1)
    live(plugin, id)
    return '', 204
