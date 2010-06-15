# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

import os
import zipfile
import shutil
import logging

from xml.etree.ElementTree import ElementTree, XML
from PyQt4 import QtCore, QtGui

from openlp.core.ui import AmendThemeForm
from openlp.core.theme import Theme
from openlp.core.lib import OpenLPToolbar, context_menu_action, \
    ThemeXML, str_to_bool, get_text_file_string, build_icon, Receiver, \
    context_menu_separator, SettingsManager, translate
from openlp.core.utils import AppLocation, get_filesystem_encoding

log = logging.getLogger(__name__)

class ThemeManager(QtGui.QWidget):
    """
    Manages the orders of Theme.
    """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.settingsSection = u'themes'
        self.Layout = QtGui.QVBoxLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setMargin(0)
        self.amendThemeForm = AmendThemeForm(self)
        self.Toolbar = OpenLPToolbar(self)
        self.Toolbar.addToolbarButton(
            translate(u'ThemeManager', u'New Theme'), u':/themes/theme_new.png',
            translate(u'ThemeManager', u'Create a new theme'), self.onAddTheme)
        self.Toolbar.addToolbarButton(
            translate(u'ThemeManager', u'Edit Theme'),
            u':/themes/theme_edit.png',
            translate(u'ThemeManager', u'Edit a theme'), self.onEditTheme)
        self.Toolbar.addToolbarButton(
            translate(u'ThemeManager', u'Delete Theme'),
            u':/general/general_delete.png',
            translate(u'ThemeManager', u'Delete a theme'), self.onDeleteTheme)
        self.Toolbar.addSeparator()
        self.Toolbar.addToolbarButton(
            translate(u'ThemeManager', u'Import Theme'), 
            u':/general/general_import.png',
            translate(u'ThemeManager', u'Import a theme'), self.onImportTheme)
        self.Toolbar.addToolbarButton(
            translate(u'ThemeManager', u'Export Theme'),
            u':/general/general_export.png',
            translate(u'ThemeManager', u'Export a theme'), self.onExportTheme)
        self.ThemeWidget = QtGui.QWidgetAction(self.Toolbar)
        self.Layout.addWidget(self.Toolbar)
        self.ThemeListWidget = QtGui.QListWidget(self)
        self.ThemeListWidget.setAlternatingRowColors(True)
        self.ThemeListWidget.setIconSize(QtCore.QSize(88, 50))
        self.Layout.addWidget(self.ThemeListWidget)
        self.ThemeListWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.ThemeListWidget.addAction(
            context_menu_action(self.ThemeListWidget,
            u':/themes/theme_edit.png',
            translate(u'ThemeManager', u'Edit a theme'), self.onEditTheme))
        self.ThemeListWidget.addAction(
            context_menu_separator(self.ThemeListWidget))
        self.ThemeListWidget.addAction(
            context_menu_action(self.ThemeListWidget,
                u':/general/general_delete.png',
                translate(u'ThemeManager', u'Delete theme'),
            self.onDeleteTheme))
        self.ThemeListWidget.addAction(
            context_menu_action(self.ThemeListWidget,
                u':/general/general_export.png',
                translate(u'ThemeManager', u'Make Global'),
            self.changeGlobalFromScreen))
        self.ThemeListWidget.addAction(
            context_menu_action(self.ThemeListWidget,
                u':/general/general_export.png',
                translate(u'ThemeManager', u'Export theme'),
                self.onExportTheme))
        self.ThemeListWidget.addAction(
            context_menu_separator(self.ThemeListWidget))
        #Signals
        QtCore.QObject.connect(self.ThemeListWidget,
            QtCore.SIGNAL(u'doubleClicked(QModelIndex)'),
            self.changeGlobalFromScreen)
        QtCore.QObject.connect(Receiver.get_receiver(),
            QtCore.SIGNAL(u'theme_update_global'), self.changeGlobalFromTab)
        #Variables
        self.themelist = []
        self.path = AppLocation.get_section_data_path(self.settingsSection)
        self.checkThemesExists(self.path)
        self.thumbPath = os.path.join(self.path, u'thumbnails')
        self.checkThemesExists(self.thumbPath)
        self.amendThemeForm.path = self.path
        # Last little bits of setting up
        self.global_theme = unicode(QtCore.QSettings().value(
            self.settingsSection + u'/global theme',
            QtCore.QVariant(u'')).toString())

    def changeGlobalFromTab(self, themeName):
        """
        Change the global theme when it is changed through the Themes settings
        tab
        """
        log.debug(u'changeGlobalFromTab %s', themeName)
        for count in range (0, self.ThemeListWidget.count()):
            #reset the old name
            item = self.ThemeListWidget.item(count)
            oldName = item.text()
            newName = unicode(item.data(QtCore.Qt.UserRole).toString())
            if oldName != newName:
                self.ThemeListWidget.item(count).setText(newName)
            #Set the new name
            if themeName == newName:
                name = unicode(translate(u'ThemeManager', u'%s (default)')) % \
                    newName
                self.ThemeListWidget.item(count).setText(name)

    def changeGlobalFromScreen(self, index = -1):
        """
        Change the global theme when a theme is double clicked upon in the
        Theme Manager list
        """
        log.debug(u'changeGlobalFromScreen %s', index)
        selected_row = self.ThemeListWidget.currentRow()
        for count in range (0, self.ThemeListWidget.count()):
            item = self.ThemeListWidget.item(count)
            oldName = item.text()
            #reset the old name
            if oldName != unicode(item.data(QtCore.Qt.UserRole).toString()):
                self.ThemeListWidget.item(count).setText(
                    unicode(item.data(QtCore.Qt.UserRole).toString()))
            #Set the new name
            if count == selected_row:
                self.global_theme = unicode(
                    self.ThemeListWidget.item(count).text())
                name = unicode(translate(u'ThemeManager', u'%s (default)')) % \
                    self.global_theme
                self.ThemeListWidget.item(count).setText(name)
                QtCore.QSettings().setValue(
                    self.settingsSection + u'/global theme',
                    QtCore.QVariant(self.global_theme))
                Receiver.send_message(u'theme_update_global', self.global_theme)
                self.pushThemes()

    def onAddTheme(self):
        """
        Loads a new theme with the default settings and then launches the theme
        editing form for the user to make their customisations.
        """
        theme = self.createThemeFromXml(self.baseTheme(), self.path)
        self.amendThemeForm.loadTheme(theme)
        self.saveThemeName = u''
        self.amendThemeForm.exec_()

    def onEditTheme(self):
        """
        Loads the settings for the theme that is to be edited and launches the
        theme editing form so the user can make their changes.
        """
        item = self.ThemeListWidget.currentItem()
        if item:
            theme = self.getThemeData(
                unicode(item.data(QtCore.Qt.UserRole).toString()))
            self.amendThemeForm.loadTheme(theme)
            self.saveThemeName = unicode(
                item.data(QtCore.Qt.UserRole).toString())
            self.amendThemeForm.exec_()

    def onDeleteTheme(self):
        """
        Delete a theme
        """
        self.global_theme = unicode(QtCore.QSettings().value(
            self.settingsSection + u'/global theme',
            QtCore.QVariant(u'')).toString())
        item = self.ThemeListWidget.currentItem()
        if item:
            theme = unicode(item.text())
            # should be the same unless default
            if theme != unicode(item.data(QtCore.Qt.UserRole).toString()):
                QtGui.QMessageBox.critical(
                    self, translate(u'ThemeManager', u'Error'),
                    translate(u'ThemeManager',
                        u'You are unable to delete the default theme.'),
                    QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok))
            else:
                for plugin in self.parent.plugin_manager.plugins:
                    if not plugin.can_delete_theme(theme):
                        QtGui.QMessageBox.critical(self, 
                            translate(u'ThemeManager', u'Error'),
                            translate(u'ThemeManager',  
                                u'Theme %s is use in %s plugin' % (theme,
                            plugin.name)))
                        return
                if unicode(self.parent.ServiceManagerContents.ThemeComboBox \
                    .currentText()) == theme:
                    QtGui.QMessageBox.critical(self,
                        translate(u'ThemeManager', u'Error'),
                        translate(u'ThemeManager',
                            u'Theme %s is use by Service Manager' % theme))
                    return
                self.themelist.remove(theme)
                th = theme + u'.png'
                row = self.ThemeListWidget.row(item)
                self.ThemeListWidget.takeItem(row)
                try:
                    os.remove(os.path.join(self.path, th))
                    os.remove(os.path.join(self.thumbPath, th))
                    encoding = get_filesystem_encoding()
                    shutil.rmtree(
                        os.path.join(self.path, theme).encode(encoding))
                except OSError:
                    #if not present do not worry
                    pass
                # As we do not reload the themes push out the change
                # Reaload the list as the internal lists and events need
                # to be triggered
                self.pushThemes()

    def onExportTheme(self):
        """
        Save the theme in a zip file
        """
        item = self.ThemeListWidget.currentItem()
        if item is None:
            QtGui.QMessageBox.critical(self, 
                translate(u'ThemeManager', u'Error'),
                translate(u'ThemeManager', u'You have not selected a theme.'))
            return
        theme = unicode(item.data(QtCore.Qt.UserRole).toString())
        path = QtGui.QFileDialog.getExistingDirectory(self,
            unicode(translate(u'ThemeManager', u'Save Theme - (%s)')) %  theme,
            SettingsManager.get_last_dir(self.settingsSection, 1))
        path = unicode(path)
        if path:
            SettingsManager.set_last_dir(self.settingsSection, path, 1)
            themePath = os.path.join(path, theme + u'.theme')
            zip = None
            try:
                zip = zipfile.ZipFile(themePath, u'w')
                source = os.path.join(self.path, theme)
                for files in os.walk(source):
                    for name in files[2]:
                        zip.write(
                            os.path.join(source, name).encode(u'utf-8'),
                            os.path.join(theme, name).encode(u'utf-8'))
                QtGui.QMessageBox.information(self,
                    translate(u'ThemeManager', u'Theme Exported'),
                    translate(u'ThemeManager',
                        u'Your theme has been successfully exported.'))
            except (IOError, OSError):
                log.exception(u'Export Theme Failed')
                QtGui.QMessageBox.critical(self,
                    translate(u'ThemeManager', u'Theme Export Failed'),
                    translate(u'ThemeManager',
                        u'Your theme could not be exported due to an error.'))
            finally:
                if zip:
                    zip.close()

    def onImportTheme(self):
        """
        Opens a file dialog to select the theme file(s) to import before
        attempting to extract OpenLP themes from those files.  This process
        will load both OpenLP version 1 and version 2 themes.
        """
        files = QtGui.QFileDialog.getOpenFileNames(
            self, translate(u'ThemeManager', u'Select Theme Import File'),
            SettingsManager.get_last_dir(self.settingsSection), u'Theme (*.*)')
        log.info(u'New Themes %s', unicode(files))
        if files:
            for file in files:
                SettingsManager.set_last_dir(
                    self.settingsSection, unicode(file))
                self.unzipTheme(file, self.path)
        self.loadThemes()

    def loadThemes(self):
        """
        Loads the theme lists and triggers updates accross the whole system
        using direct calls or core functions and events for the plugins.
        The plugins will call back in to get the real list if they want it.
        """
        log.debug(u'Load themes from dir')
        self.themelist = []
        self.ThemeListWidget.clear()
        #root, dirs, files = os.walk(self.path)
        dirList = os.listdir(self.path)
        for name in dirList:
            if name.endswith(u'.png'):
                #check to see file is in theme root directory
                theme = os.path.join(self.path, name)
                if os.path.exists(theme):
                    textName = os.path.splitext(name)[0]
                    if textName == self.global_theme:
                        name = unicode(translate(u'ThemeManager',
                            u'%s (default)')) % textName
                    else:
                        name = textName
                    thumb = os.path.join(self.thumbPath, u'%s.png' % textName)
                    item_name = QtGui.QListWidgetItem(name)
                    if os.path.exists(thumb):
                        icon = build_icon(thumb)
                    else:
                        icon = build_icon(theme)
                        pixmap = icon.pixmap(QtCore.QSize(88, 50))
                        pixmap.save(thumb, u'png')
                    item_name.setIcon(icon)
                    item_name.setData(QtCore.Qt.UserRole,
                        QtCore.QVariant(textName))
                    self.ThemeListWidget.addItem(item_name)
                    self.themelist.append(textName)
        self.pushThemes()

    def pushThemes(self):
        """
        Notify listeners that the theme list has been updated
        """
        Receiver.send_message(u'theme_update_list', self.getThemes())

    def getThemes(self):
        """
        Return the list of loaded themes
        """
        return self.themelist

    def getThemeData(self, themename):
        """
        Returns a theme object from an XML file

        ``themename``
            Name of the theme to load from file
        """
        log.debug(u'getthemedata for theme %s', themename)
        xml_file = os.path.join(self.path, unicode(themename),
            unicode(themename) + u'.xml')
        xml = get_text_file_string(xml_file)
        if not xml:
            xml = self.baseTheme()
        return self.createThemeFromXml(xml, self.path)

    def checkThemesExists(self, dir):
        """
        Check a theme directory exists and if not create it

        ``dir``
            Theme directory to make sure exists
        """
        log.debug(u'check themes')
        if not os.path.exists(dir):
            os.mkdir(dir)

    def unzipTheme(self, filename, dir):
        """
        Unzip the theme, remove the preview file if stored
        Generate a new preview fileCheck the XML theme version and upgrade if
        necessary.
        """
        log.debug(u'Unzipping theme %s', filename)
        filename = unicode(filename)
        zip = None
        outfile = None
        try:
            zip = zipfile.ZipFile(filename)
            filexml = None
            themename = None
            for file in zip.namelist():
                try:
                    ucsfile = file.decode(u'utf-8')
                except UnicodeDecodeError:
                    QtGui.QMessageBox.critical(
                        self, translate(u'ThemeManager', u'Error'),
                        translate(u'ThemeManager', u'File is not a valid '
                            u'theme.\nThe content encoding is not UTF-8.'))
                    log.exception(u'Filename "%s" is not valid UTF-8' % \
                        file.decode(u'utf-8', u'replace'))
                    continue
                osfile = unicode(QtCore.QDir.toNativeSeparators(ucsfile))
                theme_dir = None
                if osfile.endswith(os.path.sep):
                    theme_dir = os.path.join(dir, osfile)
                    if not os.path.exists(theme_dir):
                        os.mkdir(os.path.join(dir, osfile))
                else:
                    fullpath = os.path.join(dir, osfile)
                    names = osfile.split(os.path.sep)
                    if len(names) > 1:
                        # not preview file
                        if themename is None:
                            themename = names[0]
                        if theme_dir is None:
                            theme_dir = os.path.join(dir, names[0])
                            if not os.path.exists(theme_dir):
                                os.mkdir(os.path.join(dir, names[0]))
                        xml_data = zip.read(file)
                        if os.path.splitext(ucsfile)[1].lower() in [u'.xml']:
                            if self.checkVersion1(xml_data):
                                # upgrade theme xml
                                filexml = self.migrateVersion122(xml_data)
                            else:
                                filexml = xml_data
                            outfile = open(fullpath, u'w')
                            outfile.write(filexml)
                        else:
                            outfile = open(fullpath, u'wb')
                            outfile.write(zip.read(file))
            if filexml:
                self.generateAndSaveImage(dir, themename, filexml)
            else:
                QtGui.QMessageBox.critical(
                    self, translate(u'ThemeManager', u'Error'),
                    translate(u'ThemeManager', u'File is not a valid theme.'))
                log.exception(u'Theme file dosen\'t contain XML data %s' % filename)
        except (IOError, NameError):
            QtGui.QMessageBox.critical(
                self, translate(u'ThemeManager', u'Error'),
                translate(u'ThemeManager', u'File is not a valid theme.'))
            log.exception(u'Importing theme from zip file failed %s' % filename)
        finally:
            if zip:
                zip.close()
            if outfile:
                outfile.close()

    def checkVersion1(self, xmlfile):
        """
        Check if a theme is from OpenLP version 1

        ``xmlfile``
            Theme XML to check the version of
        """
        log.debug(u'checkVersion1 ')
        theme = xmlfile
        tree = ElementTree(element=XML(theme)).getroot()
        if tree.find(u'BackgroundType') is None:
            return False
        else:
            return True

    def migrateVersion122(self, xml_data):
        """
        Convert the xml data from version 1 format to the current format.

        New fields are loaded with defaults to provide a complete, working
        theme containing all compatible customisations from the old theme.

        ``xml_data``
            Version 1 theme to convert
        """
        theme = Theme(xml_data)
        newtheme = ThemeXML()
        newtheme.new_document(theme.Name)
        if theme.BackgroundType == 0:
            newtheme.add_background_solid(unicode(
                theme.BackgroundParameter1.name()))
        elif theme.BackgroundType == 1:
            direction = u'vertical'
            if theme.BackgroundParameter3.name() == 1:
                direction = u'horizontal'
            newtheme.add_background_gradient(
                unicode(theme.BackgroundParameter1.name()),
                unicode(theme.BackgroundParameter2.name()), direction)
        else:
            newtheme.add_background_image(unicode(theme.BackgroundParameter1))
        newtheme.add_font(unicode(theme.FontName),
            unicode(theme.FontColor.name()),
            unicode(theme.FontProportion * 3), u'False')
        newtheme.add_font(unicode(theme.FontName),
            unicode(theme.FontColor.name()),
            unicode(12), u'False', u'footer')
        outline = False
        shadow = False
        if theme.Shadow == 1:
            shadow = True
        if theme.Outline == 1:
            outline = True
        vAlignCorrection = 0
        if theme.VerticalAlign == 2:
            vAlignCorrection = 1
        elif theme.VerticalAlign == 1:
            vAlignCorrection = 2
        newtheme.add_display(unicode(shadow), unicode(theme.ShadowColor.name()),
            unicode(outline), unicode(theme.OutlineColor.name()),
            unicode(theme.HorizontalAlign), unicode(vAlignCorrection),
            unicode(theme.WrapStyle), unicode(0))
        return newtheme.extract_xml()

    def saveTheme(self, name, theme_xml, theme_pretty_xml, image_from,
        image_to):
        """
        Called by thememaintenance Dialog to save the theme
        and to trigger the reload of the theme list
        """
        log.debug(u'saveTheme %s %s', name, theme_xml)
        theme_dir = os.path.join(self.path, name)
        if not os.path.exists(theme_dir):
            os.mkdir(os.path.join(self.path, name))
        theme_file = os.path.join(theme_dir, name + u'.xml')
        log.debug(theme_file)
        result = QtGui.QMessageBox.Yes
        if self.saveThemeName != name:
            if os.path.exists(theme_file):
                result = QtGui.QMessageBox.question(
                    self, translate(u'ThemeManager', u'Theme Exists'),
                    translate(u'ThemeManager',
                        u'A theme with this name already exists, '
                        u'would you like to overwrite it?'),
                    (QtGui.QMessageBox.Yes | QtGui.QMessageBox.No),
                    QtGui.QMessageBox.No)
        if result == QtGui.QMessageBox.Yes:
            # Save the theme, overwriting the existing theme if necessary.
            outfile = None
            try:
                outfile = open(theme_file, u'w')
                outfile.write(theme_pretty_xml)
            except IOError:
                log.exception(u'Saving theme to file failed')
            finally:
                if outfile:
                    outfile.close()
            if image_from and image_from != image_to:
                try:
                    encoding = get_filesystem_encoding()
                    shutil.copyfile(
                        unicode(image_from).encode(encoding),
                        unicode(image_to).encode(encoding))
                except IOError:
                    log.exception(u'Failed to save theme image')
            self.generateAndSaveImage(self.path, name, theme_xml)
            self.loadThemes()
        else:
            # Don't close the dialog - allow the user to change the name of
            # the theme or to cancel the theme dialog completely.
            return False

    def generateAndSaveImage(self, dir, name, theme_xml):
        log.debug(u'generateAndSaveImage %s %s %s', dir, name, theme_xml)
        theme = self.createThemeFromXml(theme_xml, dir)
        frame = self.generateImage(theme)
        samplepathname = os.path.join(self.path, name + u'.png')
        if os.path.exists(samplepathname):
            os.unlink(samplepathname)
        frame.save(samplepathname, u'png')
        thumb = os.path.join(self.thumbPath, u'%s.png' % name)
        icon = build_icon(frame)
        pixmap = icon.pixmap(QtCore.QSize(88, 50))
        pixmap.save(thumb, u'png')
        log.debug(u'Theme image written to %s', samplepathname)

    def generateImage(self, themedata):
        """
        Call the RenderManager to build a Sample Image
        """
        log.debug(u'generateImage %s ', themedata)
        frame = self.parent.RenderManager.generate_preview(themedata)
        return frame

    def getPreviewImage(self, theme):
        """
        Return an image representing the look of the theme

        ``theme``
            The theme to return the image for
        """
        log.debug(u'getPreviewImage %s ', theme)
        image = os.path.join(self.path, theme + u'.png')
        return image

    def baseTheme(self):
        """
        Provide a base theme with sensible defaults
        """
        log.debug(u'base theme created')
        newtheme = ThemeXML()
        newtheme.new_document(unicode(translate(u'ThemeManager', u'New Theme')))
        newtheme.add_background_solid(unicode(u'#000000'))
        newtheme.add_font(unicode(QtGui.QFont().family()), unicode(u'#FFFFFF'),
            unicode(30), u'False')
        newtheme.add_font(unicode(QtGui.QFont().family()), unicode(u'#FFFFFF'),
            unicode(12), u'False', u'footer')
        newtheme.add_display(u'False', unicode(u'#FFFFFF'), u'False',
            unicode(u'#FFFFFF'), unicode(0), unicode(0), unicode(0), u'False')
        return newtheme.extract_xml()

    def createThemeFromXml(self, theme_xml, path):
        """
        Return a theme object using information parsed from XML

        ``theme_xml``
            The XML data to load into the theme
        """
        theme = ThemeXML()
        theme.parse(theme_xml)
        self.cleanTheme(theme)
        theme.extend_image_filename(path)
        return theme

    def cleanTheme(self, theme):
        """
        Clean a theme loaded from an XML file by removing stray whitespace and
        making sure parameters are the correct type for the theme object
        attributes
        """
        theme.background_color = theme.background_color.strip()
        theme.background_direction = theme.background_direction.strip()
        theme.background_endColor = theme.background_endColor.strip()
        if theme.background_filename:
            theme.background_filename = theme.background_filename.strip()
        #theme.background_mode
        theme.background_startColor = theme.background_startColor.strip()
        #theme.background_type
        if theme.display_display:
            theme.display_display = theme.display_display.strip()
        theme.display_horizontalAlign = \
            int(theme.display_horizontalAlign.strip())
        theme.display_outline = str_to_bool(theme.display_outline)
        #theme.display_outline_color
        theme.display_shadow = str_to_bool(theme.display_shadow)
        #theme.display_shadow_color
        theme.display_verticalAlign = int(theme.display_verticalAlign.strip())
        theme.display_wrapStyle = theme.display_wrapStyle.strip()
        theme.display_slideTransition = theme.display_slideTransition
        theme.font_footer_color = theme.font_footer_color.strip()
        theme.font_footer_height = int(theme.font_footer_height.strip())
        theme.font_footer_indentation = \
            int(theme.font_footer_indentation.strip())
        theme.font_footer_italics = str_to_bool(theme.font_footer_italics)
        theme.font_footer_name = theme.font_footer_name.strip()
        #theme.font_footer_override
        theme.font_footer_proportion = \
            int(theme.font_footer_proportion.strip())
        theme.font_footer_weight = theme.font_footer_weight.strip()
        theme.font_footer_width = int(theme.font_footer_width.strip())
        theme.font_footer_x = int(theme.font_footer_x.strip())
        theme.font_footer_y = int(theme.font_footer_y.strip())
        theme.font_main_color = theme.font_main_color.strip()
        theme.font_main_height = int(theme.font_main_height.strip())
        theme.font_main_italics = str_to_bool(theme.font_main_italics)
        theme.font_main_indentation = int(theme.font_main_indentation)
        theme.font_main_name = theme.font_main_name.strip()
        #theme.font_main_override
        theme.font_main_proportion = int(theme.font_main_proportion.strip())
        theme.font_main_weight = theme.font_main_weight.strip()
        theme.font_main_width = int(theme.font_main_width.strip())
        theme.font_main_x = int(theme.font_main_x.strip())
        theme.font_main_y = int(theme.font_main_y.strip())
        #theme.theme_mode
        theme.theme_name = theme.theme_name.strip()
        #theme.theme_version

