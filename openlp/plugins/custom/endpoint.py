# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
import logging

from openlp.core.api.endpoint.pluginhelpers import live, search, service
from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http.errors import NotFound


log = logging.getLogger(__name__)

custom_endpoint = Endpoint('custom')
api_custom_endpoint = Endpoint('api')


@custom_endpoint.route('search')
def custom_search(request):
    """
    Handles requests for searching the custom plugin

    :param request: The http request object.
    """
    return search(request, 'custom', log)


@custom_endpoint.route('live')
@requires_auth
def custom_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'custom', log)


@custom_endpoint.route('add')
@requires_auth
def custom_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'custom', log)


@api_custom_endpoint.route('custom/search')
def custom_search_api(request):
    """
    Handles requests for searching the custom plugin

    :param request: The http request object.
    """
    return search(request, 'custom', log)


@api_custom_endpoint.route('custom/live')
@requires_auth
def custom_live_api(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'custom', log)


@api_custom_endpoint.route('custom/add')
@requires_auth
def custom_service_api(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    try:
        return search(request, 'custom', log)
    except NotFound:
        return {'results': {'items': []}}
