# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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

import os

from flask import Blueprint, send_from_directory
from openlp.core.common.applocation import AppLocation

main_views = Blueprint('main', __name__)


@main_views.route('/', defaults={'path': ''})
@main_views.route('/<path>')
def index(path):
    if os.path.isfile(AppLocation.get_section_data_path('remotes') / path):
        return send_from_directory(str(AppLocation.get_section_data_path('remotes')), path)
    else:
        return send_from_directory(str(AppLocation.get_section_data_path('remotes')), 'index.html')


@main_views.route('/assets/<path>')
def assets(path):
    return send_from_directory(str(AppLocation.get_section_data_path('remotes') / 'assets'), path)


@main_views.route('/stage/<path>/')
def stages(path):
    return send_from_directory(str(AppLocation.get_section_data_path('stages') / path), 'stage.html')


@main_views.route('/stage/<path:path>/<file>')
def stage_assets(path, file):
    if file.lower().endswith('.aac'):
        mimetype = 'audio/aac'
    elif file.lower().endswith('.abw'):
        mimetype = 'application/x-abiword'
    elif file.lower().endswith('.arc'):
        mimetype = 'application/x-freearc'
    elif file.lower().endswith('.avi'):
        mimetype = 'video/x-msvideo'
    elif file.lower().endswith('.azw'):
        mimetype = 'application/vnd.amazon.ebook'
    elif file.lower().endswith('.bin'):
        mimetype = 'application/octet-stream'
    elif file.lower().endswith('.bmp'):
        mimetype = 'image/bmp'
    elif file.lower().endswith('.bz'):
        mimetype = 'application/x-bzip'
    elif file.lower().endswith('.bz2'):
        mimetype = 'application/x-bzip2'
    elif file.lower().endswith('.cda'):
        mimetype = 'application/x-cdf'
    elif file.lower().endswith('.csh'):
        mimetype = 'application/x-csh'
    elif file.lower().endswith('.css'):
        mimetype = 'text/css'
    elif file.lower().endswith('.csv'):
        mimetype = 'text/csv'
    elif file.lower().endswith('.doc'):
        mimetype = 'application/msword'
    elif file.lower().endswith('.docx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file.lower().endswith('.eot'):
        mimetype = 'application/vnd.ms-fontobject'
    elif file.lower().endswith('.epub'):
        mimetype = 'application/epub+zip'
    elif file.lower().endswith('.gz'):
        mimetype = 'application/gzip'
    elif file.lower().endswith('.gif'):
        mimetype = 'image/gif'
    elif file.lower().endswith('.htm'):
        mimetype = 'text/html'
    elif file.lower().endswith('.html'):
        mimetype = 'text/html'
    elif file.lower().endswith('.ico'):
        mimetype = 'image/vnd.microsoft.icon'
    elif file.lower().endswith('.ics'):
        mimetype = 'text/calendar'
    elif file.lower().endswith('.jar'):
        mimetype = 'application/java-archive'
    elif file.lower().endswith('.jpeg'):
        mimetype = 'image/jpeg'
    elif file.lower().endswith('.jpg'):
        mimetype = 'image/jpeg'
    elif file.lower().endswith('.js'):
        mimetype = 'text/javascript'
    elif file.lower().endswith('.json'):
        mimetype = 'application/json'
    elif file.lower().endswith('.jsonld'):
        mimetype = 'application/ld+json'
    elif file.lower().endswith('.mid'):
        mimetype = 'audio/midi'
    elif file.lower().endswith('.midi'):
        mimetype = 'audio/x-midi'
    elif file.lower().endswith('.mjs'):
        mimetype = 'text/javascript'
    elif file.lower().endswith('.mp3'):
        mimetype = 'audio/mpeg'
    elif file.lower().endswith('.mp4'):
        mimetype = 'video/mp4'
    elif file.lower().endswith('.mpeg'):
        mimetype = 'video/mpeg'
    elif file.lower().endswith('.mpkg'):
        mimetype = 'application/vnd.apple.installer+xml'
    elif file.lower().endswith('.odp'):
        mimetype = 'application/vnd.oasis.opendocument.presentation'
    elif file.lower().endswith('.ods'):
        mimetype = 'application/vnd.oasis.opendocument.spreadsheet'
    elif file.lower().endswith('.odt'):
        mimetype = 'application/vnd.oasis.opendocument.text'
    elif file.lower().endswith('.oga'):
        mimetype = 'audio/ogg'
    elif file.lower().endswith('.ogv'):
        mimetype = 'video/ogg'
    elif file.lower().endswith('.ogx'):
        mimetype = 'application/ogg'
    elif file.lower().endswith('.opus'):
        mimetype = 'audio/opus'
    elif file.lower().endswith('.otf'):
        mimetype = 'font/otf'
    elif file.lower().endswith('.png'):
        mimetype = 'image/png'
    elif file.lower().endswith('.pdf'):
        mimetype = 'application/pdf'
    elif file.lower().endswith('.php'):
        mimetype = 'application/x-httpd-php'
    elif file.lower().endswith('.ppt'):
        mimetype = 'application/vnd.ms-powerpoint'
    elif file.lower().endswith('.pptx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif file.lower().endswith('.rar'):
        mimetype = 'application/vnd.rar'
    elif file.lower().endswith('.rtf'):
        mimetype = 'application/rtf'
    elif file.lower().endswith('.sh'):
        mimetype = 'application/x-sh'
    elif file.lower().endswith('.svg'):
        mimetype = 'image/svg+xml'
    elif file.lower().endswith('.swf'):
        mimetype = 'application/x-shockwave-flash'
    elif file.lower().endswith('.tar'):
        mimetype = 'application/x-tar'
    elif file.lower().endswith('.tif'):
        mimetype = 'image/tiff'
    elif file.lower().endswith('.tiff'):
        mimetype = 'image/tiff'
    elif file.lower().endswith('.ts'):
        mimetype = 'video/mp2t'
    elif file.lower().endswith('.ttf'):
        mimetype = 'font/ttf'
    elif file.lower().endswith('.txt'):
        mimetype = 'text/plain'
    elif file.lower().endswith('.vsd'):
        mimetype = 'application/vnd.visio'
    elif file.lower().endswith('.wav'):
        mimetype = 'audio/wav'
    elif file.lower().endswith('.weba'):
        mimetype = 'audio/webm'
    elif file.lower().endswith('.webm'):
        mimetype = 'video/webm'
    elif file.lower().endswith('.webp'):
        mimetype = 'image/webp'
    elif file.lower().endswith('.woff'):
        mimetype = 'font/woff'
    elif file.lower().endswith('.woff2'):
        mimetype = 'font/woff2'
    elif file.lower().endswith('.xhtml'):
        mimetype = 'application/xhtml+xml'
    elif file.lower().endswith('.xls'):
        mimetype = 'application/vnd.ms-excel'
    elif file.lower().endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file.lower().endswith('.xml'):
        mimetype = 'application/xml'
    elif file.lower().endswith('.xul'):
        mimetype = 'application/vnd.mozilla.xul+xml'
    elif file.lower().endswith('.zip'):
        mimetype = 'application/zip'
    elif file.lower().endswith('.7z'):
        mimetype = 'application/x-7z-compressed'
    else:
        mimetype = 'text/plain'
    return send_from_directory(str(AppLocation.get_section_data_path('stages') / path), file, mimetype=mimetype)
