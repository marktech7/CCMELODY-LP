# -*- coding: utf-8 -*-

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
"""
This module contains tests for the PdfController
"""
import os
import pytest
from pathlib import Path
from shutil import rmtree, which
from tempfile import mkdtemp
from unittest import TestCase, skipIf
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore, QtGui

from openlp.core.common import is_macosx, is_linux, is_win
from openlp.core.common.settings import Settings
from openlp.core.display.screens import ScreenList
from openlp.plugins.presentations.lib.pdfcontroller import PdfController, PdfDocument
from tests.helpers.testmixin import TestMixin
from tests.utils.constants import RESOURCE_PATH


__default_settings__ = {
    'presentations/enable_pdf_program': True,
    'presentations/pdf_program': None,
    'presentations/thumbnail_scheme': ''
}

SCREEN = {
    'primary': False,
    'number': 1,
    'size': QtCore.QRect(0, 0, 1024, 768)
}
IS_CI = 'GITLAB_CI' in os.environ or 'APPVEYOR' in os.environ


def get_screen_resolution():
    """
    Get the screen resolution
    """
    if is_macosx():
        from AppKit import NSScreen
        screen_size = NSScreen.mainScreen().frame().size
        return screen_size.width, screen_size.height
    elif is_win():
        from win32api import GetSystemMetrics
        return GetSystemMetrics(0), GetSystemMetrics(1)
    elif is_linux():
        from Xlib.display import Display
        resolution = Display().screen().root.get_geometry()
        return resolution.width, resolution.height
    else:
        return 1024, 768


class TestPdfController(TestCase, TestMixin):
    """
    Test the PdfController.
    """
    def setUp(self):
        """
        Set up the components need for all tests.
        """
        self.setup_application()
        self.build_settings()
        # Mocked out desktop object
        self.desktop = MagicMock()
        self.desktop.primaryScreen.return_value = SCREEN['primary']
        self.desktop.screenCount.return_value = SCREEN['number']
        self.desktop.screenGeometry.return_value = SCREEN['size']
        self.screens = ScreenList.create(self.desktop)
        Settings().extend_default_settings(__default_settings__)
        self.temp_folder_path = Path(mkdtemp())
        self.thumbnail_folder_path = Path(mkdtemp())
        self.mock_plugin = MagicMock()
        self.mock_plugin.settings_section = self.temp_folder_path

    def tearDown(self):
        """
        Delete all the C++ objects at the end so that we don't have a segfault
        """
        del self.screens
        self.destroy_settings()
        rmtree(self.thumbnail_folder_path)
        rmtree(self.temp_folder_path)

    def test_constructor(self):
        """
        Test the Constructor from the PdfController
        """
        # GIVEN: No presentation controller
        controller = None

        # WHEN: The presentation controller object is created
        controller = PdfController(plugin=self.mock_plugin)

        # THEN: The name of the presentation controller should be correct
        assert 'Pdf' == controller.name, 'The name of the presentation controller should be correct'

    @skipIf(IS_CI, "This is failing on CI, skip until we can figure out what the problem is")
    def load_pdf(self, exe_path):
        """
        Test loading a Pdf using the PdfController
        """
        # GIVEN: A Pdf-file
        test_file_path = RESOURCE_PATH / 'presentations' / 'pdf_test1.pdf'

        # WHEN: The Pdf is loaded
        Settings().setValue('presentations/pdf_program', exe_path)
        controller = PdfController(plugin=self.mock_plugin)
        controller.temp_folder = self.temp_folder_path
        controller.thumbnail_folder = self.thumbnail_folder_path
        document = PdfDocument(controller, test_file_path)
        loaded = document.load_presentation()

        # THEN: The load should succeed and we should be able to get a pagecount
        assert loaded is True, 'The loading of the PDF should succeed.'
        assert 3 == document.get_slide_count(), 'The pagecount of the PDF should be 3.'

    def load_pdf_pictures(self, exe_path):
        """
        Test loading a Pdf and check the generated pictures' size
        """
        # GIVEN: A Pdf-file
        test_file_path = RESOURCE_PATH / 'presentations' / 'pdf_test1.pdf'

        # WHEN: The Pdf is loaded
        Settings().setValue('presentations/pdf_program', exe_path)
        controller = PdfController(plugin=self.mock_plugin)
        controller.temp_folder = self.temp_folder_path
        controller.thumbnail_folder = self.thumbnail_folder_path
        document = PdfDocument(controller, test_file_path)
        loaded = document.load_presentation()

        # THEN: The load should succeed and pictures should be created and have been scaled to fit the screen
        assert loaded is True, 'The loading of the PDF should succeed.'
        image = QtGui.QImage(os.path.join(str(self.temp_folder_path), 'pdf_test1.pdf', 'mainslide001.png'))
        # Based on the converter used the resolution will differ a bit
        if controller.gsbin:
            assert 1076 == image.height(), 'The height should be 1076'
            assert 760 == image.width(), 'The width should be 760'
        else:
            width, height = get_screen_resolution()
            # Calculate the width of the PDF based on the aspect ratio of the PDF
            width = int(round(height * 0.70703125, 0))
            assert image.height() == height, 'The height should be {height}'.format(height=height)
            assert image.width() == width, 'The width should be {width}'.format(width=width)

    def test_load_pdf(self):
        """
        Test loading a Pdf with each of the installed backends
        """
        for exe_name in ['gs', 'mutool', 'mudraw']:
            exe_path = which(exe_name)
            if exe_path:
                self.load_pdf(exe_path)
                self.load_pdf_pictures(exe_path)

    def test_loading_pdf_using_pymupdf(self):
        try:
            import fitz  # noqa: F401
        except ImportError:
            pytest.skip('PyMuPDF is not installed')

        self.load_pdf(None)
        self.load_pdf_pictures(None)

    @patch('openlp.plugins.presentations.lib.pdfcontroller.check_binary_exists')
    def test_process_check_binary_mudraw(self, mocked_check_binary_exists):
        """
        Test that the correct output from mudraw is detected
        """
        # GIVEN: A mocked check_binary_exists that returns mudraw output
        mudraw_output = (b'usage: mudraw [options] input [pages]\n\t-o -\toutput filename (%d for page number)n\t\tsupp'
                         b'orted formats: pgm, ppm, pam, png, pbmn\t-p -\tpasswordn\t-r -\tresolution in dpi (default: '
                         b'72)n\t-w -\twidth (in pixels) (maximum width if -r is specified)n\t-h -\theight (in pixels) '
                         b'(maximum height if -r is specified)')
        mocked_check_binary_exists.return_value = mudraw_output

        # WHEN: Calling process_check_binary
        ret = PdfController.process_check_binary('test')

        # THEN: mudraw should be detected
        assert 'mudraw' == ret, 'mudraw should have been detected'

    @patch('openlp.plugins.presentations.lib.pdfcontroller.check_binary_exists')
    def test_process_check_binary_new_motool(self, mocked_check_binary_exists):
        """
        Test that the correct output from the new mutool is detected
        """
        # GIVEN: A mocked check_binary_exists that returns new mutool output
        new_mutool_output = (b'usage: mutool <command> [options]\n\tdraw\t-- convert document\n\trun\t-- run javascript'
                             b'\n\tclean\t-- rewrite pdf file\n\textract\t-- extract font and image resources\n\tinfo\t'
                             b'-- show information about pdf resources\n\tpages\t-- show information about pdf pages\n'
                             b'\tposter\t-- split large page into many tiles\n\tshow\t-- show internal pdf objects\n\t'
                             b'create\t-- create pdf document\n\tmerge\t-- merge pages from multiple pdf sources into a'
                             b'new pdf\n')
        mocked_check_binary_exists.return_value = new_mutool_output

        # WHEN: Calling process_check_binary
        ret = PdfController.process_check_binary('test')

        # THEN: mutool should be detected
        assert 'mutool' == ret, 'mutool should have been detected'

    @patch('openlp.plugins.presentations.lib.pdfcontroller.check_binary_exists')
    def test_process_check_binary_old_motool(self, mocked_check_binary_exists):
        """
        Test that the output from the old mutool is not accepted
        """
        # GIVEN: A mocked check_binary_exists that returns old mutool output
        old_mutool_output = (b'usage: mutool <command> [options]\n\tclean\t-- rewrite pdf file\n\textract\t-- extract '
                             b'font and image resources\n\tinfo\t-- show information about pdf resources\n\tposter\t-- '
                             b'split large page into many tiles\n\tshow\t-- show internal pdf objects')
        mocked_check_binary_exists.return_value = old_mutool_output

        # WHEN: Calling process_check_binary
        ret = PdfController.process_check_binary('test')

        # THEN: mutool should be detected
        assert ret is None, 'old mutool should not be accepted!'

    @patch('openlp.plugins.presentations.lib.pdfcontroller.check_binary_exists')
    def test_process_check_binary_gs(self, mocked_check_binary_exists):
        """
        Test that the correct output from gs is detected
        """
        # GIVEN: A mocked check_binary_exists that returns gs output
        gs_output = (b'GPL Ghostscript 9.19 (2016-03-23)\nCopyright (C) 2016 Artifex Software, Inc.  All rights reserv'
                     b'ed.\nUsage: gs [switches] [file1.ps file2.ps ...]')
        mocked_check_binary_exists.return_value = gs_output

        # WHEN: Calling process_check_binary
        ret = PdfController.process_check_binary('test')

        # THEN: mutool should be detected
        assert 'gs' == ret, 'mutool should have been detected'
