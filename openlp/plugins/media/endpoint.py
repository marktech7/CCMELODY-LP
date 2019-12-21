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

from openlp.core.api.endpoint.pluginhelpers import live, search, service
from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http.errors import NotFound


log = logging.getLogger(__name__)

media_endpoint = Endpoint('media')
api_media_endpoint = Endpoint('api')


@media_endpoint.route('search')
def media_search(request):
    """
    Handles requests for searching the media plugin

    :param request: The http request object.
    """
    return search(request, 'media', log)


@media_endpoint.route('live')
@requires_auth
def media_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'media', log)


@media_endpoint.route('add')
@requires_auth
def media_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'media', log)


@api_media_endpoint.route('media/search')
def media_search_api(request):
    """
    Handles requests for searching the media plugin

    :param request: The http request object.
    """
    return search(request, 'media', log)


@api_media_endpoint.route('media/live')
@requires_auth
def media_live_api(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'media', log)


@api_media_endpoint.route('media/add')
@requires_auth
def media_service_api(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    try:
        return search(request, 'media', log)
    except NotFound:
        return {'results': {'items': []}}
