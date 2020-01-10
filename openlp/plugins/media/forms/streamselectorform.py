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

from PyQt5 import QtCore, QtWidgets

from openlp.plugins.media.forms.streamselectordialog import Ui_StreamSelector
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.common.i18n import translate

log = logging.getLogger(__name__)


class StreamSelectorForm(QtWidgets.QDialog, Ui_StreamSelector):
    """
    Class to manage the clip selection
    """
    log.info('{name} StreamSelectorForm loaded'.format(name=__name__))

    def __init__(self, media_item, parent, manager):
        """
        Constructor
        """
        super(StreamSelectorForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint |
                                                 QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.media_item = media_item
        self.setup_ui(self)
        # setup callbacks
        for i in range(self.stacked_modes_layout.count()):
            self.stacked_modes_layout.widget(i).set_callback(self.update_mrl_options)
        self.stacked_modes_layout.currentWidget().update_mrl()

    def exec(self):
        """
        Start dialog
        """
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Saves the current stream as a clip to the mediamanager
        """
        log.debug('in StreamSelectorForm.accept')
        # Verify that a stream name exists
        if not self.stream_name_edit.text().strip():
            critical_error_message_box(message=translate('MediaPlugin.StreamSelector', 'A Stream name is needed!'),
                                       parent=self)
            return
        # Verify that a MRL exists
        if not self.mrl_lineedit.text().strip():
            critical_error_message_box(message=translate('MediaPlugin.StreamSelector', 'A MRL is needed!'), parent=self)
            return
        stream_string = 'devicestream:{name}&&{mrl}&&{options}'.format(name=self.stream_name_edit.text().strip(),
                                                                       mrl=self.mrl_lineedit.text().strip(),
                                                                       options=self.vlc_options_lineedit.text().strip())
        self.media_item.add_device_stream(stream_string)
        return QtWidgets.QDialog.accept(self)

    def update_mrl_options(self, mrl, options):
        """
        Callback method used to fill the MRL and Options text fields
        """
        options += ' :live-caching={cache}'.format(cache=self.caching.value())
        self.mrl_lineedit.setText(mrl)
        self.vlc_options_lineedit.setText(options)

    def on_capture_mode_combo_box(self):
        self.stacked_modes_layout.setCurrentIndex(self.capture_mode_combo_box.currentIndex())
        self.stacked_modes_layout.currentWidget().update_mrl()
