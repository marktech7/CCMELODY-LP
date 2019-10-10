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
Package to test the openlp.core.common.path package.
"""
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openlp.core.common.path import create_paths, files_to_paths, path_to_str, replace_params, str_to_path, which


class TestShutil(TestCase):
    """
    Tests for the :mod:`openlp.core.common.path` module
    """
    def test_replace_params_no_params(self):
        """
        Test replace_params when called with and empty tuple instead of parameters to replace
        """
        # GIVEN: Some test data
        test_args = (1, 2)
        test_kwargs = {'arg3': 3, 'arg4': 4}
        test_params = tuple()

        # WHEN: Calling replace_params
        result_args, result_kwargs = replace_params(test_args, test_kwargs, test_params)

        # THEN: The positional and keyword args should not have changed
        assert test_args == result_args
        assert test_kwargs == result_kwargs

    def test_replace_params_params(self):
        """
        Test replace_params when given a positional and a keyword argument to change
        """
        # GIVEN: Some test data
        test_args = (1, 2)
        test_kwargs = {'arg3': 3, 'arg4': 4}
        test_params = ((1, 'arg2', str), (2, 'arg3', str))

        # WHEN: Calling replace_params
        result_args, result_kwargs = replace_params(test_args, test_kwargs, test_params)

        # THEN: The positional and keyword args should have have changed
        assert result_args == (1, '2')
        assert result_kwargs == {'arg3': '3', 'arg4': 4}

    def test_which_no_command(self):
        """
        Test :func:`openlp.core.common.path.which` when the command is not found.
        """
        # GIVEN: A mocked :func:`shutil.which` when the command is not found.
        with patch('openlp.core.common.path.shutil.which', return_value=None) as mocked_shutil_which:

            # WHEN: Calling :func:`openlp.core.common.path.which` with a command that does not exist.
            result = which('no_command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return None.
            mocked_shutil_which.assert_called_once_with('no_command')
        assert result is None

    def test_which_command(self):
        """
        Test :func:`openlp.core.common.path.which` when a command has been found.
        """
        # GIVEN: A mocked :func:`shutil.which` when the command is found.
        with patch('openlp.core.common.path.shutil.which',
                   return_value=os.path.join('path', 'to', 'command')) as mocked_shutil_which:

            # WHEN: Calling :func:`openlp.core.common.path.which` with a command that exists.
            result = which('command')

            # THEN: :func:`shutil.which` should have been called with the command, and :func:`which` should return a
            #       Path object equivalent of the command path.
            mocked_shutil_which.assert_called_once_with('command')
            assert result == Path('path', 'to', 'command')


class TestPath(TestCase):
    """
    Tests for the :mod:`openlp.core.common.path` module
    """

    def test_path_to_str_type_error(self):
        """
        Test that `path_to_str` raises a type error when called with an invalid type
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling `path_to_str` with an invalid Type
        # THEN: A TypeError should have been raised
        with self.assertRaises(TypeError):
            path_to_str(57)

    def test_path_to_str_wth_str(self):
        """
        Test that `path_to_str` just returns a str when given a str
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling `path_to_str` with a str
        result = path_to_str('/usr/bin')

        # THEN: The string should be returned
        assert result == '/usr/bin'

    def test_path_to_str_none(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed with None
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with None
        result = path_to_str(None)

        # THEN: `path_to_str` should return an empty string
        assert result == ''

    def test_path_to_str_path_object(self):
        """
        Test that `path_to_str` correctly converts the path parameter when passed a Path object
        """
        # GIVEN: The `path_to_str` function
        # WHEN: Calling the `path_to_str` function with a Path object
        result = path_to_str(Path('test/path'))

        # THEN: `path_to_str` should return a string representation of the Path object
        assert result == os.path.join('test', 'path')

    def test_str_to_path_type_error(self):
        """
        Test that `str_to_path` returns None if called with invalid information
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling `str_to_path` with an invalid Type
        # THEN: None is returned
        assert str_to_path(Path()) is None

    def test_str_to_path_empty_str(self):
        """
        Test that `str_to_path` correctly converts the string parameter when passed with and empty string
        """
        # GIVEN: The `str_to_path` function
        # WHEN: Calling the `str_to_path` function with None
        result = str_to_path('')

        # THEN: `path_to_str` should return None
        assert result is None

    def test_create_paths_dir_exists(self):
        """
        Test the create_paths() function when the path already exists
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.return_value = True

        # WHEN: `create_paths` is called and the path exists
        create_paths(mocked_path)

        # THEN: The function should not attempt to create the directory
        mocked_path.exists.assert_called_once_with()
        assert mocked_path.mkdir.call_count == 0, 'mkdir should not have been called'

    def test_create_paths_dir_doesnt_exists(self):
        """
        Test the create_paths() function when the path does not already exist
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.return_value = False

        # WHEN: `create_paths` is called and the path does not exist
        create_paths(mocked_path)

        # THEN: The directory should have been created
        mocked_path.exists.assert_called_once_with()
        mocked_path.mkdir.assert_called_once_with(parents=True)

    @patch('openlp.core.common.path.log')
    def test_create_paths_dir_io_error(self, mocked_logger):
        """
        Test the create_paths() when an OSError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.side_effect = OSError('Cannot make directory')

        # WHEN: An OSError is raised when checking the if the path exists.
        create_paths(mocked_path)

        # THEN: The Error should have been logged
        mocked_logger.exception.assert_called_once_with('failed to check if directory exists or create directory')

    def test_create_paths_dir_value_error(self):
        """
        Test the create_paths() when an error other than OSError is raised
        """
        # GIVEN: A `Path` to check with patched out mkdir and exists methods
        mocked_path = MagicMock()
        mocked_path.exists.side_effect = ValueError('Some other error')

        # WHEN: Some other exception is raised
        try:
            create_paths(mocked_path)
            assert False, 'create_paths should have thrown an exception'
        except Exception:
            # THEN: `create_paths` raises an exception
            pass

    def test_files_to_paths(self):
        """
        Test the files_to_paths() method
        """
        # GIVEN: A list of string filenames
        test_files = ['/tmp/openlp/file1.txt', '/tmp/openlp/file2.txt']

        # WHEN: files_to_paths is called
        result = files_to_paths(test_files)

        # THEN: The result should be a list of Paths
        assert result == [Path('/tmp/openlp/file1.txt'), Path('/tmp/openlp/file2.txt')]
