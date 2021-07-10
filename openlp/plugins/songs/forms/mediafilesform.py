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

import logging

# for temporary fix in populate_files below
from pathlib import Path
from openlp.core.common.path import str_to_path
# end

from PyQt5 import QtCore, QtWidgets

from .mediafilesdialog import Ui_MediaFilesDialog


log = logging.getLogger(__name__)


class MediaFilesForm(QtWidgets.QDialog, Ui_MediaFilesDialog):
    """
    Class to show a list of files from the
    """
    log.info('{name} MediaFilesForm loaded'.format(name=__name__))

    def __init__(self, parent):
        super(MediaFilesForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                             QtCore.Qt.WindowCloseButtonHint)
        self.setup_ui(self)

    def populate_files(self, file_paths):
        """
        :param list[pathlib.Path] file_paths:
        :return:
        """
        self.file_list_widget.clear()
        for file_path in file_paths:
            # temporary fix for issue 582
            if not isinstance(file_path, Path):
                file_path = str_to_path(file_path)
            # end of temporary fix
            item = QtWidgets.QListWidgetItem(file_path.name)
            item.setData(QtCore.Qt.UserRole, file_path)
            self.file_list_widget.addItem(item)

    def get_selected_files(self):
        """
        :rtype: list[pathlib.Path]
        """
        return [item.data(QtCore.Qt.UserRole) for item in self.file_list_widget.selectedItems()]
