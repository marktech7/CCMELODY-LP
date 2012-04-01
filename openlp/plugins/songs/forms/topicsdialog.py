# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2012 Raoul Snyman                                        #
# Portions copyright (c) 2008-2012 Tim Bentley, Gerald Britton, Jonathan      #
# Corwin, Michael Gorven, Scott Guerrieri, Matthias Hub, Meinert Jordan,      #
# Armin Köhler, Joshua Miller, Stevan Pettit, Andreas Preikschat, Mattias     #
# Põldaru, Christian Richter, Philip Ridout, Simon Scudder, Jeffrey Smith,    #
# Maikel Stuivenberg, Martin Thompson, Jon Tibble, Frode Woldsund             #
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

from PyQt4 import QtCore, QtGui

from openlp.core.lib import translate
from openlp.core.lib.ui import create_button_box

class Ui_TopicsDialog(object):
    def setupUi(self, topicsDialog):
        topicsDialog.setObjectName(u'topicsDialog')
        topicsDialog.resize(300, 10)
        self.dialogLayout = QtGui.QVBoxLayout(topicsDialog)
        self.dialogLayout.setObjectName(u'dialogLayout')
        self.nameLayout = QtGui.QFormLayout()
        self.nameLayout.setObjectName(u'nameLayout')
        self.nameLabel = QtGui.QLabel(topicsDialog)
        self.nameLabel.setObjectName(u'nameLabel')
        self.nameEdit = QtGui.QLineEdit(topicsDialog)
        self.nameEdit.setObjectName(u'nameEdit')
        self.nameLabel.setBuddy(self.nameEdit)
        self.nameLayout.addRow(self.nameLabel, self.nameEdit)
        self.dialogLayout.addLayout(self.nameLayout)
        self.buttonBox = create_button_box(topicsDialog, [u'cancel', u'save'])
        self.buttonBox.setObjectName(u'buttonBox')
        self.dialogLayout.addWidget(self.buttonBox)
        self.retranslateUi(topicsDialog)
        topicsDialog.setMaximumHeight(topicsDialog.sizeHint().height())
        QtCore.QMetaObject.connectSlotsByName(topicsDialog)

    def retranslateUi(self, topicsDialog):
        topicsDialog.setWindowTitle(
            translate('SongsPlugin.TopicsForm', 'Topic Maintenance'))
        self.nameLabel.setText(
            translate('SongsPlugin.TopicsForm', 'Topic name:'))
