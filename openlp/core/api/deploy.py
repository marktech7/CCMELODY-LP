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
"""
Download and "install" the remote web client
"""
from zipfile import ZipFile
from PyQt5 import QtWidgets

from openlp.core.common.applocation import AppLocation
from openlp.core.common.httputils import download_file, get_url_file_size, get_web_page


def deploy_zipfile(app_root_path, zip_name):
    """
    Process the downloaded zip file and add to the correct directory

    :param str zip_name: the zip file name to be processed
    :param pathlib.Path app_root_path: The directory to expand the zip to

    :return: None
    """
    zip_path = app_root_path / zip_name
    web_zip = ZipFile(zip_path)
    web_zip.extractall(app_root_path)


def download_sha256():
    """
    Download the config file to extract the sha256 and version number
    """
    user_agent = 'OpenLP/' + QtWidgets.QApplication.applicationVersion()
    try:
        web_config = get_web_page('https://get.openlp.org/webclient/download.cfg', headers={'User-Agent': user_agent})
    except ConnectionError:
        return False
    if not web_config:
        return None
    file_bits = web_config.split()
    return file_bits[0], file_bits[2]


def download_and_check(callback=None):
    """
    Download the web site and deploy it.
    """
    sha256, version = download_sha256()
    file_size = get_url_file_size('https://get.openlp.org/webclient/site.zip')
    callback.setRange(0, file_size)
    if download_file(callback, 'https://get.openlp.org/webclient/site.zip',
                     AppLocation.get_section_data_path('remotes') / 'site.zip',
                     sha256=sha256):
        deploy_zipfile(AppLocation.get_section_data_path('remotes'), 'site.zip')
