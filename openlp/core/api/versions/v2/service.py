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

from openlp.core.api.lib import login_required

from flask import jsonify, request, abort, Blueprint

from openlp.core.common.registry import Registry


service_views = Blueprint('service', __name__)


@service_views.route('/items')
def service_items():
    live_controller = Registry().get('live_controller')
    service_items = []
    if live_controller.service_item:
        current_unique_identifier = live_controller.service_item.unique_identifier
    else:
        current_unique_identifier = None
    for item in Registry().get('service_manager').service_items:
        service_item = item['service_item']
        if 'ccli_number' in service_item.data_string:
            ccli_number = service_item.data_string['ccli_number']
        else:
            ccli_number = ''
        service_items.append({
            'id': str(service_item.unique_identifier),
            'title': str(service_item.get_display_title()),
            'plugin': str(service_item.name),
            'ccli_number': str(ccli_number),
            'notes': str(service_item.notes),
            'selected': (service_item.unique_identifier == current_unique_identifier)
        })
    return jsonify(service_items)


@service_views.route('/show', methods=['POST'])
@login_required
def service_set():
    data = request.json
    if not data:
        abort(400)
    try:
        id = int(data.get('id', -1))
    except ValueError:
        abort(400)
    Registry().get('service_manager').set_item(id)
    return '', 204


@service_views.route('/progress', methods=['POST'])
@login_required
def service_direction():
    ALLOWED_ACTIONS = ['next', 'previous']
    data = request.json
    if not data:
        abort(400)
    action = data.get('action', '').lower()
    if action not in ALLOWED_ACTIONS:
        abort(400)
    getattr(Registry().get('service_manager'), 'servicemanager_{action}_item'.format(action=action)).emit()
    return '', 204
