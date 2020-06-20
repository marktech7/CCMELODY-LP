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
from flask import Blueprint, request, abort

from openlp.core.api import app
from openlp.core.api.lib import login_required, extract_request, old_success_response, old_auth
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus


v1_views = Blueprint('v1-alert-plugin', __name__)
v2_views = Blueprint('v2-alert-plugin', __name__)


@v2_views.route('', methods=['POST'])
@login_required
def alert():
    data = request.json
    if not data:
        abort(400)
    alert = data.get('text', '')
    if alert:
        if Registry().get('plugin_manager').get_plugin_by_name('alerts').status == PluginStatus.Active:
            Registry().get('alerts_manager').alerts_text.emit([alert])
            return '', 204
    abort(400)


@v1_views.route('')
@old_auth
def old_alert():
    alert = extract_request(request.args.get('data', ''), 'text')
    if alert:
        if Registry().get('plugin_manager').get_plugin_by_name('alerts').status == PluginStatus.Active:
            Registry().get('alerts_manager').alerts_text.emit([alert])
    return old_success_response()


def register_views():
    app.register_blueprint(v2_views, url_prefix='/api/v2/plugins/alerts')
    app.register_blueprint(v1_views, url_prefix='/api/alert')
