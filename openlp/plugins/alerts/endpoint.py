# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
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
import json
import logging
import urllib

from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus


log = logging.getLogger(__name__)

alerts_endpoint = Endpoint('alert')
api_alerts_endpoint = Endpoint('api')


@alerts_endpoint.route('')
@api_alerts_endpoint.route('alert')
@requires_auth
def alert(request):
    """
    Handles requests for setting service items in the service manager

    :param request: The http request object.
    """
    plugin = Registry().get('plugin_manager').get_plugin_by_name("alerts")
    if plugin.status == PluginStatus.Active:
        try:
            json_data = request.GET.get('data')
            text = json.loads(json_data)['request']['text']
        except KeyError:
            log.error("Endpoint alerts request text not found")
            text = urllib.parse.unquote(text)
        Registry().get('alerts_manager').alerts_text.emit([text])
        success = True
    else:
        success = False
    return {'results': {'success': success}}
