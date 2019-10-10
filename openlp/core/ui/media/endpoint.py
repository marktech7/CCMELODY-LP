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
"""
The :mod:`~openlp.core.api.endpoint` module contains various API endpoints
"""
import logging

from openlp.core.api.http import requires_auth
from openlp.core.api.http.endpoint import Endpoint
from openlp.core.common.registry import Registry


log = logging.getLogger(__name__)
media_endpoint = Endpoint('media')


@media_endpoint.route('play')
@requires_auth
def media_play(request):
    """
    Handles requests for playing media

    :param request: The http request object.
    """
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_play(live, False)
    return {'results': {'success': status}}


@media_endpoint.route('pause')
@requires_auth
def media_pause(request):
    """
    Handles requests for pausing media

    :param request: The http request object.
    """
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_pause(live)
    return {'results': {'success': status}}


@media_endpoint.route('stop')
@requires_auth
def media_stop(request):
    """
    Handles requests for stopping

    :param request: The http request object.
    """
    event = getattr(Registry().get('live_controller'), 'mediacontroller_live_stop')
    event.emit()
    return {'results': {'success': True}}
