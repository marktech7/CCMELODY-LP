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
"""
The song import functions for OpenLP.
"""
import codecs
import logging
import os

from PyQt4 import QtCore, QtGui

from openlp.core.lib import Receiver, SettingsManager, translate
from openlp.core.lib.ui import UiStrings, critical_error_message_box
from openlp.core.ui.wizard import OpenLPWizard, WizardStrings
from openlp.plugins.songs.lib.importer import (SongFormat, SongFormatAttr,
    SongFormatSelect)

log = logging.getLogger(__name__)

class SongImportForm(OpenLPWizard):
    """
    This is the Song Import Wizard, which allows easy importing of Songs
    into OpenLP from other formats like OpenLyrics, OpenSong and CCLI.
    """
    log.info(u'SongImportForm loaded')

    def __init__(self, parent, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        ``parent``
            The QWidget-derived parent of the wizard.

        ``plugin``
            The songs plugin.
        """
        self.clipboard = plugin.formParent.clipboard
        self.activeFormat = None
        self.formatWidgets = dict([(f, {}) for f in SongFormat.get_format_list()])
        OpenLPWizard.__init__(self, parent, plugin, u'songImportWizard',
            u':/wizards/wizard_importsong.bmp')

    def setupUi(self, image):
        """
        Set up the song wizard UI.
        """
        OpenLPWizard.setupUi(self, image)
        self.activeFormat = SongFormat.OpenLyrics
        self.formatStack.setCurrentIndex(self.activeFormat)
        QtCore.QObject.connect(self.formatComboBox,
            QtCore.SIGNAL(u'currentIndexChanged(int)'),
            self.onCurrentIndexChanged)

    def onCurrentIndexChanged(self, index):
        """
        Called when the format combo box's index changed. We have to check if
        the import is available and accordingly to disable or enable the next
        button.
        """
        self.activeFormat = index
        self.formatStack.setCurrentIndex(self.activeFormat)
        next_button = self.button(QtGui.QWizard.NextButton)
        next_button.setEnabled(SongFormatAttr.get(self.activeFormat,
            SongFormatAttr.availability))

    def customInit(self):
        """
        Song wizard specific initialisation.
        """
        for format in SongFormat.get_format_list():
            if not SongFormatAttr.get(format,
                SongFormatAttr.availability):
                self.formatWidgets[format][u'disabledWidget'].setVisible(True)
                self.formatWidgets[format][u'importWidget'].setVisible(False)

    def customSignals(self):
        """
        Song wizard specific signals.
        """
        for format in SongFormat.get_format_list():
            select_mode = SongFormatAttr.get(format,
                SongFormatAttr.select_mode)
            if select_mode == SongFormatSelect.MultipleFiles:
                QtCore.QObject.connect(self.formatWidgets[format][u'addButton'],
                    QtCore.SIGNAL(u'clicked()'), self.onAddButtonClicked)
                QtCore.QObject.connect(
                    self.formatWidgets[format][u'removeButton'],
                    QtCore.SIGNAL(u'clicked()'), self.onRemoveButtonClicked)
            else:
                QtCore.QObject.connect(
                    self.formatWidgets[format][u'browseButton'],
                    QtCore.SIGNAL(u'clicked()'), self.onBrowseButtonClicked)

    def addCustomPages(self):
        """
        Add song wizard specific pages.
        """
        # Source Page
        self.sourcePage = QtGui.QWizardPage()
        self.sourcePage.setObjectName(u'SourcePage')
        self.sourceLayout = QtGui.QVBoxLayout(self.sourcePage)
        self.sourceLayout.setObjectName(u'SourceLayout')
        self.formatLayout = QtGui.QFormLayout()
        self.formatLayout.setObjectName(u'FormatLayout')
        self.formatLabel = QtGui.QLabel(self.sourcePage)
        self.formatLabel.setObjectName(u'FormatLabel')
        self.formatComboBox = QtGui.QComboBox(self.sourcePage)
        self.formatComboBox.setObjectName(u'FormatComboBox')
        self.formatLayout.addRow(self.formatLabel, self.formatComboBox)
        self.formatSpacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Minimum)
        self.formatLayout.setItem(1, QtGui.QFormLayout.LabelRole,
            self.formatSpacer)
        self.sourceLayout.addLayout(self.formatLayout)
        self.stackSpacer = QtGui.QSpacerItem(10, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Expanding)
        self.formatStack = QtGui.QStackedLayout()
        self.formatStack.setObjectName(u'FormatStack')
        self.disablableFormats = []
        for self.activeFormat in SongFormat.get_format_list():
            self.addFileSelectItem()
        self.sourceLayout.addLayout(self.formatStack)
        self.addPage(self.sourcePage)

    def retranslateUi(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(
            translate('SongsPlugin.ImportWizardForm', 'Song Import Wizard'))
        self.titleLabel.setText(WizardStrings.HeaderStyle %
            translate('OpenLP.Ui', 'Welcome to the Song Import Wizard'))
        self.informationLabel.setText(
            translate('SongsPlugin.ImportWizardForm',
                'This wizard will help you to import songs from a variety of '
                'formats. Click the next button below to start the process by '
                'selecting a format to import from.'))
        self.sourcePage.setTitle(WizardStrings.ImportSelect)
        self.sourcePage.setSubTitle(WizardStrings.ImportSelectLong)
        self.formatLabel.setText(WizardStrings.FormatLabel)

        for format in SongFormat.get_format_list():
            format_name, custom_combo_text, select_mode = SongFormatAttr.get(
                format, SongFormatAttr.name, SongFormatAttr.combo_box_text,
                SongFormatAttr.select_mode)
            combo_box_text = custom_combo_text if custom_combo_text \
                else format_name
            self.formatComboBox.setItemText(format, combo_box_text)
            if select_mode == SongFormatSelect.MultipleFiles:
                self.formatWidgets[format][u'addButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
                self.formatWidgets[format][u'removeButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
            else:
                if select_mode == SongFormatSelect.SingleFile:
                    f_label = 'Filename:'
                elif select_mode == SongFormatSelect.SingleFolder:
                    f_label = 'Folder:'
                self.formatWidgets[format][u'browseButton'].setText(
                    UiStrings().Browse)
                self.formatWidgets[format][u'filepathLabel'].setText(
                        translate('SongsPlugin.ImportWizardForm', f_label))
        for format in self.disablableFormats:
            self.formatWidgets[format][u'disabledLabel'].setText(
                SongFormatAttr.get(format,
                SongFormatAttr.disabled_label_text))

        self.progressPage.setTitle(WizardStrings.Importing)
        self.progressPage.setSubTitle(
            translate('SongsPlugin.ImportWizardForm',
                'Please wait while your songs are imported.'))
        self.progressLabel.setText(WizardStrings.Ready)
        self.progressBar.setFormat(WizardStrings.PercentSymbolFormat)
        self.errorCopyToButton.setText(translate('SongsPlugin.ImportWizardForm',
            'Copy'))
        self.errorSaveToButton.setText(translate('SongsPlugin.ImportWizardForm',
            'Save to File'))
        # Align all QFormLayouts towards each other.
        width = max(self.formatLabel.minimumSizeHint().width(),
            self.openLP2FilenameLabel.minimumSizeHint().width())
        self.formatSpacer.changeSize(width, 0, QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)

    def customPageChanged(self, pageId):
        """
        Called when changing to a page other than the progress page
        """
        if self.page(pageId) == self.sourcePage:
            self.onCurrentIndexChanged(self.formatStack.currentIndex())

    def validateCurrentPage(self):
        """
        Validate the current page before moving on to the next page.
        """
        if self.currentPage() == self.welcomePage:
            return True
        elif self.currentPage() == self.sourcePage:
            #source_format = self.formatComboBox.currentIndex()
            format = self.activeFormat
            QtCore.QSettings().setValue(u'songs/last import type',
                format)
            select_mode, class_, format_name, custom_error = \
                SongFormatAttr.get(format, SongFormatAttr.select_mode,
                SongFormatAttr.class_, SongFormatAttr.name,
                SongFormatAttr.invalid_source_msg)
            error_msg = lambda str: (custom_error if custom_error
                 else str % format_name)
            if select_mode == SongFormatSelect.MultipleFiles:
                fileListWidget = self.formatWidgets[format][u'fileListWidget']
                if fileListWidget.count() == 0 or not class_.isValidSource(
                    filenames=self.getListOfFiles(fileListWidget)):
                    error_msg = error_msg if error_msg else WizardStrings.YouSpecifyFiles % format_name
                    critical_error_message_box(UiStrings().NFSp,
                        error_msg(WizardStrings.YouSpecifyFiles))
                    self.formatWidgets[format][u'addButton'].setFocus()
                    return False
            elif select_mode == SongFormatSelect.SingleFile:
                filepathEdit = self.formatWidgets[format][u'filepathEdit']
                if filepathEdit.text().isEmpty() or not class_.isValidSource(
                    filename=filepathEdit.text()):
                    critical_error_message_box(UiStrings().NFSs,
                        error_msg(WizardStrings.YouSpecifyFile))
                    self.formatWidgets[format][u'browseButton'].setFocus()
                    return False
            elif select_mode == SongFormatSelect.SingleFolder:
                filepathEdit = self.formatWidgets[format][u'filepathEdit']
                if filepathEdit.text().isEmpty() or not class_.isValidSource(
                    folder=filepathEdit.text()):
                    critical_error_message_box(UiStrings().NFdSs,
                        error_msg(WizardStrings.YouSpecifyFolder))
                    self.formatWidgets[format][u'browseButton'].setFocus()
                    return False
            return True
        elif self.currentPage() == self.progressPage:
            return True

    def getFiles(self, title, listbox, filters=u''):
        """
        Opens a QFileDialog and writes the filenames to the given listbox.

        ``title``
            The title of the dialog (unicode).

        ``listbox``
            A listbox (QListWidget).

        ``filters``
            The file extension filters. It should contain the file descriptions
            as well as the file extensions. For example::

                u'SongBeamer Files (*.sng)'
        """
        if filters:
            filters += u';;'
        filters += u'%s (*)' % UiStrings().AllFiles
        filenames = QtGui.QFileDialog.getOpenFileNames(self, title,
            SettingsManager.get_last_dir(self.plugin.settingsSection, 1),
            filters)
        if filenames:
            listbox.addItems(filenames)
            SettingsManager.set_last_dir(self.plugin.settingsSection,
                os.path.split(unicode(filenames[0]))[0], 1)

    def getListOfFiles(self, listbox):
        """
        Return a list of file from the listbox
        """
        return [unicode(listbox.item(i).text()) for i in range(listbox.count())]

    def removeSelectedItems(self, listbox):
        """
        Remove selected listbox items
        """
        for item in listbox.selectedItems():
            item = listbox.takeItem(listbox.row(item))
            del item

    def onBrowseButtonClicked(self):
        format = self.activeFormat
        select_mode = SongFormatAttr.get(format,
            SongFormatAttr.select_mode)
        name = SongFormatAttr.get(format,
            SongFormatAttr.name)
        filter = SongFormatAttr.get(format,
            SongFormatAttr.filter)
        filepathEdit = self.formatWidgets[format][u'filepathEdit']
        if select_mode == SongFormatSelect.SingleFile:
            self.getFileName(WizardStrings.OpenTypeFile % name, filepathEdit,
                filter)
        elif select_mode == SongFormatSelect.SingleFolder:
            self.getFolder(WizardStrings.OpenTypeFile % name, filepathEdit)

    def onAddButtonClicked(self):
        format = self.activeFormat
        select_mode, format_name, filter, custom_title = \
        SongFormatAttr.get(format, SongFormatAttr.select_mode,
            SongFormatAttr.name, SongFormatAttr.filter,
            SongFormatAttr.get_files_title)
        title = custom_title if custom_title \
            else WizardStrings.OpenTypeFile % format_name
        if select_mode == SongFormatSelect.MultipleFiles:
            self.getFiles(title, self.formatWidgets[format][u'FileListWidget'],
                filter)

    def onRemoveButtonClicked(self):
        self.removeSelectedItems(
            self.formatWidgets[self.activeFormat][u'FileListWidget'])

    def setDefaults(self):
        """
        Set default form values for the song import wizard.
        """
        self.restart()
        self.finishButton.setVisible(False)
        self.cancelButton.setVisible(True)
        last_import_type = QtCore.QSettings().value(
            u'songs/last import type').toInt()[0]
        if last_import_type < 0 or \
            last_import_type >= self.formatComboBox.count():
            last_import_type = 0
        self.formatComboBox.setCurrentIndex(last_import_type)
        for format in SongFormat.get_format_list():
            select_mode = SongFormatAttr.get(format,
                SongFormatAttr.select_mode)
            if select_mode == SongFormatSelect.MultipleFiles:
                self.formatWidgets[format][u'fileListWidget'].clear()
            else:
                self.formatWidgets[format][u'filepathEdit'].setText(u'')
        self.errorReportTextEdit.clear()
        self.errorReportTextEdit.setHidden(True)
        self.errorCopyToButton.setHidden(True)
        self.errorSaveToButton.setHidden(True)

    def preWizard(self):
        """
        Perform pre import tasks
        """
        OpenLPWizard.preWizard(self)
        self.progressLabel.setText(WizardStrings.StartingImport)
        Receiver.send_message(u'openlp_process_events')

    def performWizard(self):
        """
        Perform the actual import. This method pulls in the correct importer
        class, and then runs the ``doImport`` method of the importer to do
        the actual importing.
        """
        source_format = self.activeFormat
        select_mode = SongFormatAttr.get(source_format,
            SongFormatAttr.select_mode)
        if select_mode == SongFormatSelect.SingleFile:
            importer = self.plugin.importSongs(source_format,
                filename=unicode(
                self.formatWidgets[source_format][u'filepathEdit'].text()))
        elif select_mode == SongFormatSelect.MultipleFiles:
            importer = self.plugin.importSongs(source_format,
                filenames=self.getListOfFiles(
                    self.formatWidgets[source_format][u'fileListWidget']))
        elif select_mode == SongFormatSelect.SingleFolder:
            importer = self.plugin.importSongs(source_format,
                folder=unicode(
                self.formatWidgets[source_format][u'filepathEdit'].text()))
        importer.doImport()
        self.progressLabel.setText(WizardStrings.FinishedImport)

    def onErrorCopyToButtonClicked(self):
        """
        Copy the error report to the clipboard.
        """
        self.clipboard.setText(self.errorReportTextEdit.toPlainText())

    def onErrorSaveToButtonClicked(self):
        """
        Save the error report to a file.
        """
        filename = QtGui.QFileDialog.getSaveFileName(self,
            SettingsManager.get_last_dir(self.plugin.settingsSection, 1))
        if not filename:
            return
        report_file = codecs.open(filename, u'w', u'utf-8')
        report_file.write(self.errorReportTextEdit.toPlainText())
        report_file.close()

    def addFileSelectItem(self):
        format = self.activeFormat
        prefix = SongFormatAttr.get(format, SongFormatAttr.prefix)
        obj_prefix = SongFormatAttr.get(format,
            SongFormatAttr.obj_prefix)
        can_disable = SongFormatAttr.get(format,
            SongFormatAttr.can_disable)
        select_mode = SongFormatAttr.get(format,
            SongFormatAttr.select_mode)
        if not obj_prefix:
            obj_prefix = prefix
        page = QtGui.QWidget()
        page.setObjectName(obj_prefix + u'Page')
        if can_disable:
            importWidget = self.disablableWidget(page, obj_prefix)
        else:
            importWidget = page
        importLayout = QtGui.QVBoxLayout(importWidget)
        importLayout.setMargin(0)
        importLayout.setObjectName(obj_prefix + u'ImportLayout')
        if select_mode == SongFormatSelect.SingleFile or \
            select_mode == SongFormatSelect.SingleFolder:
            filepathLayout = QtGui.QHBoxLayout()
            filepathLayout.setObjectName(obj_prefix + u'FilepathLayout')
            filepathLabel = QtGui.QLabel(importWidget)
            filepathLabel.setObjectName(obj_prefix + u'FilepathLabel')
            filepathLayout.addWidget(filepathLabel)
            filepathEdit = QtGui.QLineEdit(importWidget)
            filepathEdit.setObjectName(obj_prefix + u'FilepathEdit')
            filepathLayout.addWidget(filepathEdit)
            browseButton = QtGui.QToolButton(importWidget)
            browseButton.setIcon(self.openIcon)
            browseButton.setObjectName(obj_prefix + u'BrowseButton')
            filepathLayout.addWidget(browseButton)
            importLayout.addLayout(filepathLayout)
            importLayout.addSpacerItem(self.stackSpacer)
            self.formatWidgets[format][u'filepathLabel'] = filepathLabel
            self.formatWidgets[format][u'filepathLayout'] = filepathLayout
            self.formatWidgets[format][u'filepathEdit'] = filepathEdit
            self.formatWidgets[format][u'browseButton'] = browseButton
        elif select_mode == SongFormatSelect.MultipleFiles:
            fileListWidget = QtGui.QListWidget(importWidget)
            fileListWidget.setSelectionMode(
                QtGui.QAbstractItemView.ExtendedSelection)
            fileListWidget.setObjectName(obj_prefix + u'FileListWidget')
            importLayout.addWidget(fileListWidget)
            buttonLayout = QtGui.QHBoxLayout()
            buttonLayout.setObjectName(obj_prefix + u'ButtonLayout')
            addButton = QtGui.QPushButton(importWidget)
            addButton.setIcon(self.openIcon)
            addButton.setObjectName(obj_prefix + u'AddButton')
            buttonLayout.addWidget(addButton)
            buttonLayout.addStretch()
            removeButton = QtGui.QPushButton(importWidget)
            removeButton.setIcon(self.deleteIcon)
            removeButton.setObjectName(obj_prefix + u'RemoveButton')
            buttonLayout.addWidget(removeButton)
            importLayout.addLayout(buttonLayout)
            self.formatWidgets[format][u'fileListWidget'] = fileListWidget
            self.formatWidgets[format][u'buttonLayout'] = buttonLayout
            self.formatWidgets[format][u'addButton'] = addButton
            self.formatWidgets[format][u'removeButton'] = removeButton
        self.formatStack.addWidget(page)
        self.formatWidgets[format][u'page'] = page
        self.formatWidgets[format][u'importLayout'] = importLayout
        self.formatComboBox.addItem(u'')

    def disablableWidget(self, page, obj_prefix):
        format = self.activeFormat
        self.disablableFormats.append(format)
        layout = QtGui.QVBoxLayout(page)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.setObjectName(obj_prefix + u'Layout')
        disabledWidget = QtGui.QWidget(page)
        disabledWidget.setVisible(False)
        disabledWidget.setObjectName(obj_prefix + u'DisabledWidget')
        disabledLayout = QtGui.QVBoxLayout(disabledWidget)
        disabledLayout.setMargin(0)
        disabledLayout.setObjectName(obj_prefix + u'DisabledLayout')
        disabledLabel = QtGui.QLabel(disabledWidget)
        disabledLabel.setWordWrap(True)
        disabledLabel.setObjectName(obj_prefix + u'DisabledLabel')
        disabledLayout.addWidget(disabledLabel)
        disabledLayout.addSpacerItem(self.stackSpacer)
        layout.addWidget(disabledWidget)
        importWidget = QtGui.QWidget(page)
        importWidget.setObjectName(obj_prefix + u'ImportWidget')
        layout.addWidget(importWidget)
        self.formatWidgets[format][u'layout'] = layout
        self.formatWidgets[format][u'disabledWidget'] = disabledWidget
        self.formatWidgets[format][u'disabledLayout'] = disabledLayout
        self.formatWidgets[format][u'disabledLabel'] = disabledLabel
        self.formatWidgets[format][u'importWidget'] = importWidget
        return importWidget
