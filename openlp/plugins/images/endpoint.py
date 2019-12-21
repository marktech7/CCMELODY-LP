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

from openlp.core.api.endpoint.pluginhelpers import display_thumbnails, live, search, service
from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.api.http.errors import NotFound


log = logging.getLogger(__name__)

images_endpoint = Endpoint('images')
api_images_endpoint = Endpoint('api')


# images/thumbnails/320x240/1.jpg
@images_endpoint.route('thumbnails/{dimensions}/{file_name}')
def images_thumbnails(request, dimensions, file_name):
    """
    Return an image to a web page based on a URL
    :param request: Request object
    :param dimensions: the image size eg 88x88
    :param file_name: the individual image name
    :return:
    """
    return display_thumbnails(request, 'images', log, dimensions, file_name)


@images_endpoint.route('search')
def images_search(request):
    """
    Handles requests for searching the images plugin

    :param request: The http request object.
    """
    return search(request, 'images', log)


@images_endpoint.route('live')
@requires_auth
def images_live(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'images', log)


@images_endpoint.route('add')
@requires_auth
def images_service(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    return service(request, 'images', log)


@api_images_endpoint.route('images/search')
def images_search_api(request):
    """
    Handles requests for searching the images plugin

    :param request: The http request object.
    """
    return search(request, 'images', log)


@api_images_endpoint.route('images/live')
@requires_auth
def images_live_api(request):
    """
    Handles requests for making a song live

    :param request: The http request object.
    """
    return live(request, 'images', log)


@api_images_endpoint.route('images/add')
@requires_auth
def images_service_api(request):
    """
    Handles requests for adding a song to the service

    :param request: The http request object.
    """
    try:
        return search(request, 'images', log)
    except NotFound:
        return {'results': {'items': []}}
