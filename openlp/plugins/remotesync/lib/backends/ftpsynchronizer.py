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

import fnmatch
from ftplib import FTP
from io import TextIOBase

from openlp.plugins.remotesync.lib.backends.foldersynchronizer import FolderSynchronizer


class FtpSynchronizer(FolderSynchronizer):

    def __init__(self, manager, base_folder_path, pc_id):
        super(FtpSynchronizer, self).__init__(manager, base_folder_path, pc_id)
        self.ftp = None

    def check_configuration(self):
        return True

    def check_connection(self):
        self.connect()
        base_folder_content = self._get_file_list(self.base_folder_path, '*')
        self.disconnect()

    def initialize_remote(self):
        self.connect()
        self.ftp.mkd(self.song_history_folder_path)
        self.ftp.mkd(self.custom_folder_path)
        self.ftp.mkd(self.service_folder_path)
        self.disconnect()

    def connect(self):
        # TODO: Also support FTP_TLS
        self.ftp = FTP('123.server.ip', 'username', 'password')

    def disconnect(self):
        self.ftp.close()
        self.ftp = None

    def _get_file_list(self, path, mask):
        file_list = self.ftp.nlst(path)
        filtered_list = fnmatch.filter(file_list, mask)
        return filtered_list

    def _remove_lock_file(self, lock_filename):
        self.ftp.remove(lock_filename)

    def _move_file(self, src, dst):
        self.ftp.move(src, dst)

    def _create_file(self, filename, file_content):
        text_stream = TextIOBase()
        text_stream.write(file_content)
        self.ftp.storbinary('STOR ' + filename, text_stream)

    def _read_file(self, filename):
        text_stream = TextIOBase()
        self.ftp.retrbinary('RETR ' + filename, text_stream, 1024)
        return text_stream.read()
