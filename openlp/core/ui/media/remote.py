# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
"""
The :mod:`~openlp.core.api.endpoint` module contains various API endpoints
"""
import logging
from flask import abort, jsonify, Blueprint

from openlp.core.api import app
from openlp.core.api.lib import login_required, old_auth
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)

v1_media = Blueprint('v1-media-controller', __name__)
v2_media = Blueprint('v2-media-controller', __name__)


@v2_media.route('/play', methods=['POST'])
@login_required
def media_play():
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    try:
        status = media.media_play(live, True)
    except Exception:
        # The current item probably isn't a media item
        abort(400)
    if status:
        return '', 204
    abort(400)


@v2_media.route('/pause', methods=['POST'])
@login_required
def media_pause():
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    media.media_pause(live)
    return '', 204


@v2_media.route('/stop', methods=['POST'])
@login_required
def media_stop():
    Registry().get('live_controller').mediacontroller_live_stop.emit()
    return '', 204


# -------------- DEPRECATED ------------------------
@v1_media.route('/play')
@old_auth
def v1_media_play():
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_play(live, False)
    return jsonify({'success': status})


@v1_media.route('/pause')
@old_auth
def v1_media_pause():
    media = Registry().get('media_controller')
    live = Registry().get('live_controller')
    status = media.media_pause(live)
    return jsonify({'success': status})


@v1_media.route('/stop')
@old_auth
def v1_media_stop():
    Registry().get('live_controller').mediacontroller_live_stop.emit()
    return ''
# -------------- END OF DEPRECATED ------------------------


def register_views():
    app.register_blueprint(v2_media, url_prefix='/api/v2/media/')
    app.register_blueprint(v1_media, url_prefix='/api/media/')
