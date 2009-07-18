# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4
"""
OpenLP - Open Source Lyrics Projection
Copyright (c) 2008 Raoul Snyman
Portions copyright (c) 2008-2009 Martin Thompson, Tim Bentley,

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
from openlp.core.lib import  translate
from PyQt4 import QtCore, QtGui

class Ui_EditSongDialog(object):
    def setupUi(self, EditSongDialog):
        EditSongDialog.setObjectName(u'EditSongDialog')
        EditSongDialog.resize(786, 704)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/icon/openlp-logo-16x16.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EditSongDialog.setWindowIcon(icon)
        EditSongDialog.setModal(True)
        self.EditSongLayout = QtGui.QVBoxLayout(EditSongDialog)
        self.EditSongLayout.setSpacing(8)
        self.EditSongLayout.setMargin(8)
        self.EditSongLayout.setObjectName(u'EditSongLayout')
        self.TopWidget = QtGui.QWidget(EditSongDialog)
        self.TopWidget.setObjectName(u'TopWidget')
        self.TopLayout = QtGui.QHBoxLayout(self.TopWidget)
        self.TopLayout.setSpacing(8)
        self.TopLayout.setMargin(0)
        self.TopLayout.setObjectName(u'TopLayout')
        self.TextWidget = QtGui.QWidget(self.TopWidget)
        self.TextWidget.setObjectName(u'TextWidget')
        self.DetailsLayout = QtGui.QVBoxLayout(self.TextWidget)
        self.DetailsLayout.setSpacing(8)
        self.DetailsLayout.setMargin(0)
        self.DetailsLayout.setObjectName(u'DetailsLayout')
        self.TitleLabel = QtGui.QLabel(self.TextWidget)
        self.TitleLabel.setObjectName(u'TitleLabel')
        self.DetailsLayout.addWidget(self.TitleLabel)
        self.TitleEditItem = QtGui.QLineEdit(self.TextWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TitleEditItem.sizePolicy().hasHeightForWidth())
        self.TitleEditItem.setSizePolicy(sizePolicy)
        self.TitleEditItem.setObjectName(u'TitleEditItem')
        self.DetailsLayout.addWidget(self.TitleEditItem)
        self.AlternativeTitleLabel = QtGui.QLabel(self.TextWidget)
        self.AlternativeTitleLabel.setObjectName(u'AlternativeTitleLabel')
        self.DetailsLayout.addWidget(self.AlternativeTitleLabel)
        self.AlternativeEdit = QtGui.QLineEdit(self.TextWidget)
        self.AlternativeEdit.setObjectName(u'AlternativeEdit')
        self.DetailsLayout.addWidget(self.AlternativeEdit)
        self.LyricsLabel = QtGui.QLabel(self.TextWidget)
        self.LyricsLabel.setObjectName(u'LyricsLabel')
        self.DetailsLayout.addWidget(self.LyricsLabel)
        self.VerseEditWidget = QtGui.QWidget(self.TextWidget)
        self.VerseEditWidget.setObjectName(u'VerseEditWidget')
        self.VerseEditLayout = QtGui.QVBoxLayout(self.VerseEditWidget)
        self.VerseEditLayout.setSpacing(8)
        self.VerseEditLayout.setMargin(0)
        self.VerseEditLayout.setObjectName(u'VerseEditLayout')
        self.VerseListWidget = QtGui.QListWidget(self.VerseEditWidget)
        self.VerseListWidget.setObjectName(u'VerseListWidget')
        self.VerseListWidget.setAlternatingRowColors(True)
        self.VerseEditLayout.addWidget(self.VerseListWidget)
        self.VerseButtonWidget = QtGui.QWidget(self.VerseEditWidget)
        self.VerseButtonWidget.setObjectName(u'VerseButtonWidget')
        self.VerseButtonLayout = QtGui.QHBoxLayout(self.VerseButtonWidget)
        self.VerseButtonLayout.setSpacing(8)
        self.VerseButtonLayout.setMargin(0)
        self.VerseButtonLayout.setObjectName(u'VerseButtonLayout')
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.VerseButtonLayout.addItem(spacerItem)
        self.AddButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.AddButton.setObjectName(u'AddButton')
        self.VerseButtonLayout.addWidget(self.AddButton)
        self.EditButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.EditButton.setObjectName(u'EditButton')
        self.VerseButtonLayout.addWidget(self.EditButton)
        self.DeleteButton = QtGui.QPushButton(self.VerseButtonWidget)
        self.DeleteButton.setObjectName(u'DeleteButton')
        self.VerseButtonLayout.addWidget(self.DeleteButton)
        self.VerseEditLayout.addWidget(self.VerseButtonWidget)
        self.DetailsLayout.addWidget(self.VerseEditWidget)
        self.VerseOrderLabel = QtGui.QLabel(self.TextWidget)
        self.VerseOrderLabel.setObjectName(u'VerseOrderLabel')
        self.DetailsLayout.addWidget(self.VerseOrderLabel)
        self.VerseOrderEdit = QtGui.QLineEdit(self.TextWidget)
        self.VerseOrderEdit.setObjectName(u'VerseOrderEdit')
        self.DetailsLayout.addWidget(self.VerseOrderEdit)
        self.CommentsLabel = QtGui.QLabel(self.TextWidget)
        self.CommentsLabel.setObjectName(u'CommentsLabel')
        self.DetailsLayout.addWidget(self.CommentsLabel)
        self.CommentsEdit = QtGui.QTextEdit(self.TextWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CommentsEdit.sizePolicy().hasHeightForWidth())
        self.CommentsEdit.setSizePolicy(sizePolicy)
        self.CommentsEdit.setMaximumSize(QtCore.QSize(16777215, 84))
        self.CommentsEdit.setObjectName(u'CommentsEdit')
        self.DetailsLayout.addWidget(self.CommentsEdit)
        self.ThemeGroupBox = QtGui.QGroupBox(self.TextWidget)
        self.ThemeGroupBox.setObjectName(u'ThemeGroupBox')
        self.ThemeLayout = QtGui.QHBoxLayout(self.ThemeGroupBox)
        self.ThemeLayout.setSpacing(8)
        self.ThemeLayout.setMargin(8)
        self.ThemeLayout.setObjectName(u'ThemeLayout')
        self.ThemeSelectionComboItem = QtGui.QComboBox(self.ThemeGroupBox)
        self.ThemeSelectionComboItem.setObjectName(u'ThemeSelectionComboItem')
        self.ThemeLayout.addWidget(self.ThemeSelectionComboItem)
        self.DetailsLayout.addWidget(self.ThemeGroupBox)
        self.TopLayout.addWidget(self.TextWidget)
        self.AdditionalWidget = QtGui.QWidget(self.TopWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AdditionalWidget.sizePolicy().hasHeightForWidth())
        self.AdditionalWidget.setSizePolicy(sizePolicy)
        self.AdditionalWidget.setMinimumSize(QtCore.QSize(100, 0))
        self.AdditionalWidget.setObjectName(u'AdditionalWidget')
        self.AdditionalLayout = QtGui.QVBoxLayout(self.AdditionalWidget)
        self.AdditionalLayout.setSpacing(8)
        self.AdditionalLayout.setMargin(0)
        self.AdditionalLayout.setObjectName(u'AdditionalLayout')
        self.AuthorsGroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        self.AuthorsGroupBox.setObjectName(u'AuthorsGroupBox')
        self.AuthorsLayout = QtGui.QVBoxLayout(self.AuthorsGroupBox)
        self.AuthorsLayout.setSpacing(8)
        self.AuthorsLayout.setMargin(8)
        self.AuthorsLayout.setObjectName(u'AuthorsLayout')
        self.AuthorAddWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorAddWidget.setObjectName(u'AuthorAddWidget')
        self.AddAuthorLayout = QtGui.QHBoxLayout(self.AuthorAddWidget)
        self.AddAuthorLayout.setSpacing(8)
        self.AddAuthorLayout.setMargin(0)
        self.AddAuthorLayout.setObjectName(u'AddAuthorLayout')
        self.AuthorsSelectionComboItem = QtGui.QComboBox(self.AuthorAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AuthorsSelectionComboItem.sizePolicy().hasHeightForWidth())
        self.AuthorsSelectionComboItem.setSizePolicy(sizePolicy)
        self.AuthorsSelectionComboItem.setEditable(False)
        self.AuthorsSelectionComboItem.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.AuthorsSelectionComboItem.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.AuthorsSelectionComboItem.setMinimumContentsLength(8)
        self.AuthorsSelectionComboItem.setObjectName(u'AuthorsSelectionComboItem')
        self.AddAuthorLayout.addWidget(self.AuthorsSelectionComboItem)
        self.AuthorAddtoSongItem = QtGui.QPushButton(self.AuthorAddWidget)
        self.AuthorAddtoSongItem.setMaximumSize(QtCore.QSize(110, 16777215))
        self.AuthorAddtoSongItem.setObjectName(u'AuthorAddtoSongItem')
        self.AddAuthorLayout.addWidget(self.AuthorAddtoSongItem)
        self.AuthorsLayout.addWidget(self.AuthorAddWidget)
        self.AuthorsListView = QtGui.QListWidget(self.AuthorsGroupBox)
        self.AuthorsListView.setAlternatingRowColors(True)
        self.AuthorsListView.setObjectName(u'AuthorsListView')
        self.AuthorsLayout.addWidget(self.AuthorsListView)
        self.AuthorRemoveWidget = QtGui.QWidget(self.AuthorsGroupBox)
        self.AuthorRemoveWidget.setObjectName(u'AuthorRemoveWidget')
        self.AuthorRemoveLayout = QtGui.QHBoxLayout(self.AuthorRemoveWidget)
        self.AuthorRemoveLayout.setSpacing(8)
        self.AuthorRemoveLayout.setMargin(0)
        self.AuthorRemoveLayout.setObjectName(u'AuthorRemoveLayout')
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.AuthorRemoveLayout.addItem(spacerItem1)
        self.AuthorRemoveItem = QtGui.QPushButton(self.AuthorRemoveWidget)
        self.AuthorRemoveItem.setObjectName(u'AuthorRemoveItem')
        self.AuthorRemoveLayout.addWidget(self.AuthorRemoveItem)
#        self.AddAuthorsButton = QtGui.QPushButton(self.AuthorRemoveWidget)
#        self.AddAuthorsButton.setObjectName(u'AddAuthorsButton')
#        self.AuthorRemoveLayout.addWidget(self.AddAuthorsButton)
        self.AuthorsLayout.addWidget(self.AuthorRemoveWidget)
        self.AdditionalLayout.addWidget(self.AuthorsGroupBox)
        self.SongBookGroup = QtGui.QGroupBox(self.AdditionalWidget)
        self.SongBookGroup.setObjectName(u'SongBookGroup')
        self.SongbookLayout = QtGui.QGridLayout(self.SongBookGroup)
        self.SongbookLayout.setMargin(8)
        self.SongbookLayout.setSpacing(8)
        self.SongbookLayout.setObjectName(u'SongbookLayout')
        self.SongbookCombo = QtGui.QComboBox(self.SongBookGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SongbookCombo.sizePolicy().hasHeightForWidth())
        self.SongbookCombo.setSizePolicy(sizePolicy)
        self.SongbookCombo.setObjectName(u'SongbookCombo')
        self.SongbookLayout.addWidget(self.SongbookCombo, 0, 0, 1, 1)
#        self.AddSongBookButton = QtGui.QPushButton(self.SongBookGroup)
#        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
#        sizePolicy.setHorizontalStretch(0)
#        sizePolicy.setVerticalStretch(0)
#        sizePolicy.setHeightForWidth(self.AddSongBookButton.sizePolicy().hasHeightForWidth())
#        self.AddSongBookButton.setSizePolicy(sizePolicy)
#        self.AddSongBookButton.setObjectName(u'AddSongBookButton')
#        self.SongbookLayout.addWidget(self.AddSongBookButton, 0, 1, 1, 1)
        self.AdditionalLayout.addWidget(self.SongBookGroup)
        self.TopicGroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TopicGroupBox.sizePolicy().hasHeightForWidth())
        self.TopicGroupBox.setSizePolicy(sizePolicy)
        self.TopicGroupBox.setObjectName(u'TopicGroupBox')
        self.TopicLayout = QtGui.QVBoxLayout(self.TopicGroupBox)
        self.TopicLayout.setSpacing(8)
        self.TopicLayout.setMargin(8)
        self.TopicLayout.setObjectName(u'TopicLayout')
        self.TopicAddWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicAddWidget.setObjectName(u'TopicAddWidget')
        self.TopicAddLayout = QtGui.QHBoxLayout(self.TopicAddWidget)
        self.TopicAddLayout.setSpacing(8)
        self.TopicAddLayout.setMargin(0)
        self.TopicAddLayout.setObjectName(u'TopicAddLayout')
        self.SongTopicCombo = QtGui.QComboBox(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SongTopicCombo.sizePolicy().hasHeightForWidth())
        self.SongTopicCombo.setSizePolicy(sizePolicy)
        self.SongTopicCombo.setObjectName(u'SongTopicCombo')
        self.TopicAddLayout.addWidget(self.SongTopicCombo)
        self.AddTopicsToSongButton = QtGui.QPushButton(self.TopicAddWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AddTopicsToSongButton.sizePolicy().hasHeightForWidth())
        self.AddTopicsToSongButton.setSizePolicy(sizePolicy)
        self.AddTopicsToSongButton.setObjectName(u'AddTopicsToSongButton')
        self.TopicAddLayout.addWidget(self.AddTopicsToSongButton)
        self.TopicLayout.addWidget(self.TopicAddWidget)
        self.TopicsListView = QtGui.QListWidget(self.TopicGroupBox)
        self.TopicsListView.setAlternatingRowColors(True)
        self.TopicsListView.setObjectName(u'TopicsListView')
        self.TopicLayout.addWidget(self.TopicsListView)
        self.TopicRemoveWidget = QtGui.QWidget(self.TopicGroupBox)
        self.TopicRemoveWidget.setObjectName(u'TopicRemoveWidget')
        self.TopicRemoveLayout = QtGui.QHBoxLayout(self.TopicRemoveWidget)
        self.TopicRemoveLayout.setSpacing(8)
        self.TopicRemoveLayout.setMargin(0)
        self.TopicRemoveLayout.setObjectName(u'TopicRemoveLayout')
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.TopicRemoveLayout.addItem(spacerItem2)
        self.TopicRemoveItem = QtGui.QPushButton(self.TopicRemoveWidget)
        self.TopicRemoveItem.setObjectName(u'TopicRemoveItem')
        self.TopicRemoveLayout.addWidget(self.TopicRemoveItem)
#        self.AddTopicButton = QtGui.QPushButton(self.TopicRemoveWidget)
#        self.AddTopicButton.setObjectName(u'AddTopicButton')
#        self.TopicRemoveLayout.addWidget(self.AddTopicButton)
        self.TopicLayout.addWidget(self.TopicRemoveWidget)
        self.AdditionalLayout.addWidget(self.TopicGroupBox)
        self.CopyrightgroupBox = QtGui.QGroupBox(self.AdditionalWidget)
        self.CopyrightgroupBox.setObjectName(u'CopyrightgroupBox')
        self.CopyrightLayout = QtGui.QVBoxLayout(self.CopyrightgroupBox)
        self.CopyrightLayout.setSpacing(8)
        self.CopyrightLayout.setMargin(8)
        self.CopyrightLayout.setObjectName(u'CopyrightLayout')
        self.CopyrightWidget = QtGui.QWidget(self.CopyrightgroupBox)
        self.CopyrightWidget.setObjectName(u'CopyrightWidget')
        self.CopyLayout = QtGui.QHBoxLayout(self.CopyrightWidget)
        self.CopyLayout.setSpacing(8)
        self.CopyLayout.setMargin(0)
        self.CopyLayout.setObjectName(u'CopyLayout')
        self.CopyrightEditItem = QtGui.QLineEdit(self.CopyrightWidget)
        self.CopyrightEditItem.setObjectName(u'CopyrightEditItem')
        self.CopyLayout.addWidget(self.CopyrightEditItem)
        self.CopyrightInsertItem = QtGui.QPushButton(self.CopyrightWidget)
        self.CopyrightInsertItem.setMaximumSize(QtCore.QSize(29, 16777215))
        self.CopyrightInsertItem.setObjectName(u'CopyrightInsertItem')
        self.CopyLayout.addWidget(self.CopyrightInsertItem)
        self.CopyrightLayout.addWidget(self.CopyrightWidget)
        self.CcliWidget = QtGui.QWidget(self.CopyrightgroupBox)
        self.CcliWidget.setObjectName(u'CcliWidget')
        self.CCLILayout = QtGui.QHBoxLayout(self.CcliWidget)
        self.CCLILayout.setSpacing(8)
        self.CCLILayout.setMargin(0)
        self.CCLILayout.setObjectName(u'CCLILayout')
        self.CCLILabel = QtGui.QLabel(self.CcliWidget)
        self.CCLILabel.setObjectName(u'CCLILabel')
        self.CCLILayout.addWidget(self.CCLILabel)
        self.CCLNumberEdit = QtGui.QLineEdit(self.CcliWidget)
        self.CCLNumberEdit.setObjectName(u'CCLNumberEdit')
        self.CCLILayout.addWidget(self.CCLNumberEdit)
        self.CopyrightLayout.addWidget(self.CcliWidget)
        self.AdditionalLayout.addWidget(self.CopyrightgroupBox)
        self.TopLayout.addWidget(self.AdditionalWidget)
        self.EditSongLayout.addWidget(self.TopWidget)
        self.ButtonBox = QtGui.QDialogButtonBox(EditSongDialog)
        self.ButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.ButtonBox.setObjectName(u'ButtonBox')
        self.EditSongLayout.addWidget(self.ButtonBox)

        self.retranslateUi(EditSongDialog)
        QtCore.QObject.connect(self.ButtonBox, QtCore.SIGNAL(u'rejected()'), EditSongDialog.close)
        QtCore.QObject.connect(self.ButtonBox, QtCore.SIGNAL(u'accepted()'), self.onAccept)
        QtCore.QMetaObject.connectSlotsByName(EditSongDialog)
        EditSongDialog.setTabOrder(self.TitleEditItem, self.AlternativeEdit)
        EditSongDialog.setTabOrder(self.AlternativeEdit, self.VerseOrderEdit)
        EditSongDialog.setTabOrder(self.VerseOrderEdit, self.CommentsEdit)
        EditSongDialog.setTabOrder(self.CommentsEdit, self.ThemeSelectionComboItem)
        EditSongDialog.setTabOrder(self.ThemeSelectionComboItem, self.AuthorAddtoSongItem)
        EditSongDialog.setTabOrder(self.AuthorAddtoSongItem, self.AuthorsListView)
        EditSongDialog.setTabOrder(self.AuthorsListView, self.AuthorRemoveItem)
        EditSongDialog.setTabOrder(self.AuthorRemoveItem, self.SongbookCombo)
        #EditSongDialog.setTabOrder(self.SongbookCombo, self.AddSongBookButton)
        #EditSongDialog.setTabOrder(self.AddSongBookButton, self.SongTopicCombo)
        EditSongDialog.setTabOrder(self.SongbookCombo, self.SongTopicCombo)
        EditSongDialog.setTabOrder(self.SongTopicCombo, self.TopicsListView)
        EditSongDialog.setTabOrder(self.TopicsListView, self.TopicRemoveItem)
        EditSongDialog.setTabOrder(self.TopicRemoveItem, self.CopyrightEditItem)
        EditSongDialog.setTabOrder(self.CopyrightEditItem, self.CopyrightInsertItem)
        EditSongDialog.setTabOrder(self.CopyrightInsertItem, self.CCLNumberEdit)
        EditSongDialog.setTabOrder(self.CCLNumberEdit, self.ButtonBox)

    def retranslateUi(self, EditSongDialog):
        EditSongDialog.setWindowTitle(translate(u'EditSongDialog', u'Song Editor'))
        self.TitleLabel.setText(translate(u'EditSongDialog', u'Title:'))
        self.AlternativeTitleLabel.setText(translate(u'EditSongDialog', u'Alternative Title:'))
        self.LyricsLabel.setText(translate(u'EditSongDialog', u'Lyrics:'))
        self.AddButton.setText(translate(u'EditSongDialog', u'Add'))
        self.EditButton.setText(translate(u'EditSongDialog', u'Edit'))
        self.DeleteButton.setText(translate(u'EditSongDialog', u'Delete'))
        self.VerseOrderLabel.setText(translate(u'EditSongDialog', u'Verse Order:'))
        self.CommentsLabel.setText(translate(u'EditSongDialog', u'Comments:'))
        self.ThemeGroupBox.setTitle(translate(u'EditSongDialog', u'Theme'))
        self.AuthorsGroupBox.setTitle(translate(u'EditSongDialog', u'Authors'))
        self.AuthorAddtoSongItem.setText(translate(u'EditSongDialog', u'Add to Song'))
        self.AuthorRemoveItem.setText(translate(u'EditSongDialog', u'Remove'))
        #self.AddAuthorsButton.setText(translate(u'EditSongDialog', u'Manage Authors'))
        self.SongBookGroup.setTitle(translate(u'EditSongDialog', u'Song Book'))
        #self.AddSongBookButton.setText(translate(u'EditSongDialog', u'Manage Song Books'))
        self.TopicGroupBox.setTitle(translate(u'EditSongDialog', u'Topic'))
        self.AddTopicsToSongButton.setText(translate(u'EditSongDialog', u'Add to Song'))
        self.TopicRemoveItem.setText(translate(u'EditSongDialog', u'Remove'))
        #self.AddTopicButton.setText(translate(u'EditSongDialog', u'Manage Topics'))
        self.CopyrightgroupBox.setTitle(translate(u'EditSongDialog', u'Copyright Infomaton'))
        self.CopyrightInsertItem.setText(translate(u'EditSongDialog', u'(c)'))
        self.CCLILabel.setText(translate(u'EditSongDialog', u'CCLI Number:'))
