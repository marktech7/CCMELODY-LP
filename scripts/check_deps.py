#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2022 OpenLP Developers                              #
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

"""Parse Python source files and check dependencies are available

Must be run in the base directory of your project.
ex: base = current_directory
    project = base/name

This script goes through a project and builds a dependency
list. It only searches for "import" or "from ... import" to validate
dependencies.

This script does NOT install missing dependencies. Modules listed
as dependencies may be updated in the resulting json file to
include the package that the module may be located as well as
the repository where the package may be found (ex. PyPI or a fedora repo).

After building a dependency list, project managers can then
assign "required | optional | dev" status to the dependencies.

project.json format:

{
    "project"        : Project directory name
    "name"           : Proper project name
    "version"[1]     : Project version this file refers to
    "git_version"[1] : Git repo version

    module : {
                "status"[1]  : "required" | "optional" | "dev" | "new" | "ignore",  # "required" if not defined
                "os"[1]      : os.name,  # O/S Agnostic if not defined
                "version"[1] : min [, max],
                repo[2]      : [ repo_pacakge_name, repo_package_name, ... ],
                "parent"[2]  : module,
                "notes"[1]   : "Module notes"
             }
    }
}

    Note: Entry in "quotes" is exact item. Entry not in quotes is pointer to item use.
        ex "version" indicates exact attribute
        ex. repo indicates pointer to item use. ex: "pypi", "fedora", ...

    Note: If "status" is "new", dependency was found and has not been classified yet.
          If "status" is "ignore", then don't check

    [1] Optional.
    [2] Optional. Typical usage is "module" name does not match repository name
        ex:     repo: Name of distribution for package manager with package name as value
                          ex. repo="pip": "<PyPI package name>"
                          ex. repo="fedora": "<fedora package name>"
                "parent": <Name of parent module>
                       ex. module="QtWebEngineWidgets": { "parent": "PyQt5 }
                       Note: "parent" points to another "module" entry

:author: Ken Roberts <alisonken1_#_gmail_dot_com>
:copyright: OpenLP
"""
import json
import logging
import os
import re

from importlib.machinery import PathFinder
from pathlib import Path

__all__ = ['check_deps']

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)-10s :  %(message)s')
    log = logging.getLogger()
    _log_width, _ = os.get_terminal_size()
else:
    log = logging.getLogger(__name__)
    _log_width = 110


class DataClass(object):
    """
    Class to hold global defines
    """
    def __init__(self, *args, **kwargs):
        """
        base_dir is fully-qualified path
        All other directory references will be relative to base_dir
        """
        super().__init__()
        # All directories in here are relative to base_dir
        self.base_dir = Path('.').resolve()  # Project base directory (current directory)
        self.dep_list = None  # (dict() of JSON file contents
        # All files in file_list will be relative to the directory they're found in
        # file_list.keys() are directories relative to base_dir
        self.file_list = None  # Keep track of files to check
        self.git_version = None  # Git version
        self.helpers = []  # Director(ies) that contain helper scripts
        # proj_dir will be relative to base_dir
        self.proj_dir = None  # Subdirectory of base_dir where source files are located
        self.project = 'openlp'  # Directory name
        self.project_name = 'OpenLP'  # Proper name
        # save_file is just the name of the file, not a Path()
        self.save_file = None  # JSON file
        self.setup = None  # Options from setup.py
        self.setup_py = None
        self.start_py = None  # Hopefully the name of the script that starts the program
        # test_dir is relative to base_dir
        self.test_dir = None  # Directory where tests are located
        self.version = None  # Project version
        self.version_file = '.version'  # Name of version file

    def __repr__(self):
        return f'<DataClass: ' \
            f'base_dir={self.base_dir},' \
            f' dep_list={self.dep_list},' \
            f' file_list={self.file_list},' \
            f' git_version={self.git_version},' \
            f' helpers={self.helpers},' \
            f' proj_dir={self.proj_dir},' \
            f' project={self.project},' \
            f' project_name={self.project_name},' \
            f' save_file={self.save_file},' \
            f' setup={self.setup},' \
            f' setup_py={self.setup_py},' \
            f' start_py={self.start_py},' \
            f' test_dir={self.test_dir},' \
            f' version={self.version},' \
            f' version_file={self.version_file}' \
            '>'

    def __str__(self):
        return f'base_dir={self.base_dir},' \
            f' dep_list={self.dep_list},' \
            f' file_list={self.file_list},' \
            f' git_version={self.git_version},' \
            f' helpers={self.helpers},' \
            f' proj_dir={self.proj_dir},' \
            f' project={self.project},' \
            f' project_name={self.project_name},' \
            f' save_file={self.save_file},' \
            f' setup={self.setup},' \
            f' setup_py={self.setup_py},' \
            f' start_py={self.start_py},' \
            f' test_dir={self.test_dir},' \
            f' version={self.version},' \
            f' version_file={self.version_file}'


data = DataClass()

# Exclude directories from project
ExclDir = ['__pycache__', 'resources', 'documentation', 'docs']
# Exclude directories in tests
ExclDirTest = ['js']
# Exclude files
ExclFile = ['resources.py']
InclExt = ['.py']

# Indicates there are no files in a directory list
No_Files_Marker = '###-NOFILES-###'

###########################################################
#                                                         #
#                Private Functions                        #
#                                                         #
###########################################################


def _check_comments(fp, check):
    """Checks for blank lines and lines starting with #

    :param obj fp: Open file object
    :param str check: Initial string to check
    :return: str
    """
    _line = check.strip()
    if _line and not _line.startswith('#'):
        return _line

    # Already checked current line, continue with following lines
    for _line in fp:
        if not _line and fp.closed():
            return _line
        _line = _line.strip()
        if _line and not _line.startswith('#'):
            break
    return _line


def _check_continues(fp, check):
    """Check for '\' continuation mark

    :param obj fp: Open file object
    :param str check: Initial string to check
    :return: Full line
    :rtype: str
    """
    _line = check.strip()
    if not _line.endswith('\\'):
        return _line

    _line = _line.rstrip('\\').strip()
    for _l in fp:
        if not _l and fp.closed():
            return _line
        _l = _l.strip()
        _line = ' '.join([_line, _l])

        if not _line.endswith('\\'):
            break
        _line = _line.rstrip('\\').strip()

    return _line


def _check_docstrings(fp, check, skip=True):
    """Check for docstring and skip if found

    :param obj fp: File object to scan
    :param str check: Initial tring to check
    :param bool skip: If False, return docstring as a single string
    :return: str
    """
    _line = check.strip()
    if "'" * 3 in _line:
        # Get around possible issues with using triplets string and parsing this file
        _chk = "'" * 3
    elif '"' * 3 in _line:
        # Get around possible issues with using triplets string and parsing this file
        _chk = '"' * 3
    else:
        return _line

    _c = _line.split(_chk)
    if len(_c) == 3 and not f'{_c[0]}{_c[-1]}':
        # Single-line docstring
        if skip:
            return ''
        return _line

    for _l in fp:
        if not _l and fp.closed():
            break
        _l = _l.strip()
        _line = ' '.join([_line, _l])
        if _chk in _l:
            break

    if skip:
        return ''
    return _line


def _get_directory(base, recurse=True, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Process the project directory and add source files to data.file_list

    :param Path base: Initial directory to process relative to data.base_dir
    :param bool recurse: Process subdirectories
    :param list e_dir: Directory names to exclude
    :param list e_file: File names to exclude
    :param list i_ext: File name extensions to include (default ['.py']
    """
    __my_name__ = '_get_directory'

    if not base.is_dir():
        log.error(f'({__my_name__}) Base is not a directory - exiting')
        return

    log.info(f'({__my_name__}) Starting process on {base}')

    if base not in data.file_list or data.file_list[base] is None:
        data.file_list[base] = []
    _dirs, _files = _list_dir(data.base_dir.joinpath(base))

    # Process directories
    if _dirs is not None:
        for _chk in _dirs:
            if _chk not in data.file_list:
                data.file_list[_chk] = None

    if _files is None:
        # No files, so mark it as so
        data.file_list[base] = No_Files_Marker
    else:
        for _chk in _files:
            # Don't need relative path since we only scanned base
            data.file_list[base].append(_chk.name)
    # log.debug(f'({__my_name__}) Directory list: {data.file_list[base]}')
    _log_formatter(log.debug, f'({__my_name__}) Directory list:', data.file_list[base])


def _get_empty_items():
    """Find all entries in data.file_list that are set to None

    :return: dict
    """
    _ret = dict()

    for _key in data.file_list:
        if data.file_list[_key] is None:
            _ret[_key] = None
    return _ret


def _get_json_file(src):
    """Initialize data.dep_list

    If json_file exists, populate from previously saved list.
    data.base_dir must already be checked before calling this function.

    :param Path src: Fully qualified file path/name
    """
    __my_name__ = '_get_json_file'
    log.info(f'({__my_name__}) Checking for previous {src.relative_to(data.base_dir)} dependency list')

    _ret = None
    _src = data.base_dir.joinpath(src)

    if _src.exists():
        log.info(f'({__my_name__}) Parsing {src}')
        try:
            with open(_src, 'r') as fp:
                _ret = json.load(fp)
                log.info(f'({__my_name__}) Loaded JSON file')

        except json.JSONDecodeError:
            log.warning(f'({__my_name__}) {src} appears to be corrupted - returning new dictionary')
            _ret = None
    else:
        log.info(f'({__my_name__}) Source {src} does not exists, returning new dictionary')

    if _ret is None:
        if data.version is None:
            data.version, data.git_version = _get_version()

        # No previous state available, start a new one
        _ret = {'project': data.project,
                'name': data.project_name,
                'version': data.version,
                'git_version': data.git_version
                }
    data.dep_list = _ret
    return


def _get_next_line(fp, check, skip=True):
    """Finds next line that's not a comment or a docstring

    :param obj fp: File object
    :param str check: Initial string to check
    :return: str
    """
    _check = _check_comments(fp, check)
    if _check:
        _check = _check_continues(fp, _check)
        if _check:
            return _check_docstrings(fp, _check, skip=skip)

    return ''


def _get_project_dir(proj=data.project):
    """Finds the project directory

    Sets data.proj_dir to (data.base_dir)/dir.

    :param str proj: Name of project
    :return: None
    """
    __my_name__ = '_get_project_dir'
    _base = data.base_dir
    _dirs, _files = _list_dir('.')

    if _dirs is None:
        log.error(f'({__my_name__}) Unable to determine starting point - exiting')
        return

    log.info(f'({__my_name__}) Starting base checks')
    if _dirs is not None:
        _proj_chk = []
        for _checkdir in _dirs:
            log.debug(f'({__my_name__}) Checking {_checkdir}')
            if _checkdir.name == 'src':
                if data.base_dir.joinpath(_checkdir).exists():
                    # PyPI project
                    _proj_chk.append(_checkdir)
                    continue
            elif data.project is not None and _checkdir.name == data.project:
                log.debug(f'({__my_name__}) Adding "{_checkdir.name}"')
                _proj_chk.append(_checkdir)
                continue
            elif _checkdir.name.startswith('test'):
                log.debug(f'({__my_name__}) Setting data.test_dir to "{_checkdir.name}"')
                data.test_dir = _checkdir
                continue
            elif _checkdir.name.startswith('script'):
                log.debug(f'({__my_name__}) Adding "{_checkdir.name}" to helpers list')
                data.helpers.append(_checkdir)
                continue
            # Check for module spec
            _chk = '.'.join([c for c in data.base_dir.joinpath(_checkdir).parts])
            _chk = PathFinder.find_spec(_chk)
            if not _chk:
                continue
            elif _chk.origin is None:
                # Did not find spec - not a package
                continue
            elif 'site-package' in _chk.origin:
                # We're looking for source, not dpes here
                continue

            _c = Path(_chk.origin).parts
            if 'test' in _c[-2]:
                data.test_dir = _checkdir.relative_to(_base)
                continue
            elif 'script' in _c[-2]:
                # Helper scripts
                data.helpers = _checkdir.relative_to(_base)
                continue

            # Unknown directory - recheck later
            _proj_chk.append(_checkdir.relative_to(_base))

        if len(_proj_chk) == 1:
            # Hopefully found our package
            data.project = _proj_chk[0].name
            data.proj_dir = _proj_chk[0]
            _proj_chk.pop(0)

    log.debug(f'({__my_name__}) Finished processing directories')
    log.debug(f'({__my_name__}) Leftover list: {_proj_chk}')

    _proj_chk = []
    if _files is not None:
        for _file in _files:
            if data.start_py is None and _file.name.startswith('run_'):
                data.start_py = _file.name
                continue
            elif 'setup.py' == _file.name:
                data.setup_py = _file.name
                continue
            _proj_chk = _file


def _get_version(proj=data.project, vfile=data.version_file):
    """Get version information from Git, project/.version

    :param str proj: Project directory
    :param str vfile: File with single-line version number format "N.N.N"

    :returns: (version, git_version)
    :rtype: tuple
    """
    __my_name__ = '_get_version'
    log.info(f'({__my_name__}) Getting version for project "{proj}"')
    git_version = ''
    proj_version = ''

    from subprocess import run
    try:
        git_version = run(['git', 'describe', '--tags'],
                          capture_output=True,
                          check=True,
                          universal_newlines=True).stdout.strip()

    except FileNotFoundError:
        # Git not available
        pass

    try:
        vf = Path(proj, vfile)
        with vf.open() as fp:
            proj_version = [v for v in fp.readlines() if v]
            proj_version = proj_version[0].strip()
    except FileNotFoundError:
        # Version file not available
        if git_version is not None:
            # Try to get version from git_version
            proj_version = git_version.split('-', 1)[0]

    if proj_version is None:
        log.warning(f'({__my_name__}) Unable to get {proj} version')
        log.warning(f'({__my_name__}) Version file {proj}/{proj_version} missing')
    else:
        log.info(f'({__my_name__}) Project version: {proj_version} Git version: {git_version}')

    return (proj_version, git_version)


def _list_dir(base, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Scan directory and returns entries. Excludes __pycache__ directory.

    :param str base: Fully qualified Path()
    :return: (directories, files)
    :rtype: tuple
    """
    __my_name__ = '_list_dir'

    _chk = Path(base).resolve()
    if not _chk.is_dir():
        log.warning(f'({__my_name__}) "{base} not a directory - returning')
        return (None, None)

    log.info(f'({__my_name__}) Starting directory scan in {base}')
    _dirs = []
    _files = []

    for _check in _chk.iterdir():
        log.debug(f'({__my_name__}) Checking {_check}')
        if _check.is_file() \
                and _check.suffix in i_ext \
                and _check.name not in e_file \
                and not _check.name.startswith('.'):
            log.debug(f'({__my_name__}) Adding {_check.name} to files')
            _files.append(_check.relative_to(data.base_dir))

        elif _check.is_dir() \
                and _check.name not in e_dir \
                and not _check.name.startswith('.'):
            log.debug(f'({__my_name__}) Adding {_check.name} to directories')
            _dirs.append(_check.relative_to(data.base_dir))

    _dirs = None if not _dirs else _dirs
    _files = None if not _files else _files
    _log_formatter(log.debug, f'({__my_name__}) dirs  : ', _dirs)
    _log_formatter(log.debug, f'({__my_name__}) files : ', _files)
    return (_dirs, _files)


def _log_formatter(lvl, header, msg, spacer=10):
    """Log a class, dict, list, tuple with minor extra formatting

    :param func lvl: Logger method
    :param str header: Message header
    :param msg: dict, list, tuple, class to log
    :param int spacer: Indent level for message
    """
    _spacer = spacer * 3

    if len(f'{header} : {msg}') < _log_width - _spacer:
        return lvl(f'{header}{msg}')

    _spaces = ' ' * spacer
    _msg = msg.__repr__()
    _curr = 0
    _last = len(_msg)
    lvl(f'{header} :')

    while _curr < _last:
        _len = _curr + _log_width - _spacer
        if _len >= _last:
            _len = _last
        else:
            _l = [i for i in re.finditer('\s', _msg[_curr:_len])]  # noqa
            if _l:
                _len = _curr + _l[-1].span()[0]
        _line = _msg[_curr:_len]
        lvl(f'{_spaces}{_line}')
        _curr = _len


def _save_json_file(src, deps):
    """Save dependency list to file. Return None on error.

    :param Path src: Fully-qualified /path/to/file to save to
    :param dict deps: Dependency dictionary
    :return: bool
    """
    __my_name__ = '_save_json_file'

    if type(deps) is not dict:
        log.warning(f'({__my_name__}) Cannot save data - wrong type (not dict)')
        return False

    log.info(f'({__my_name__}) Saving data to {src}')
    try:
        with open(src, 'w') as fp:
            json.dump(deps, fp, indent=4, sort_keys=True)

    except Exception as err:
        log.warning(f'({__my_name__}) Error saving data: ({err=}')
        return False

    log.info(f'({__my_name__}) Data saved to {src}')
    return True


# #####################################################################################
# #####################################################################################
# #####################################################################################
# #####################################################################################


def check_deps(base=data.base_dir, full=False, jfile=None, testdir=None, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Entry point for dependency checks. Initializes required options.

    :param Path base: Base directory of project (default Path('.'))
    :param bool full: Force full dependency check (default False)
    :param str jfile: Name of JSON file (default (project-deps.json)
    :param bool testdir: Check test directory files
    :param list e_dir: Directory names to exclude
    :param list e_file: File names to exclude
    :param list i_ext: File name extensions to include (default ['.py']
    """
    __my_name__ = 'check_deps'
    log.info(f'({__my_name__}) Starting dependency checks')

    if data.proj_dir is None:
        _get_project_dir()

    if jfile is not None:
        data.save_file = jfile
    elif data.project is not None:
        data.save_file = f'{data.project}-deps.json'
    else:
        log.warning(f'({__my_name__}) Save file not specified - using "project-deps.json"')
        data.save_file = 'project-deps.json'
    log.info(f'({__my_name__}) Saving dependency list in {data.base_dir.joinpath(data.save_file)}')

    if full or data.dep_list is None or len(data.dep_list) <= 4:
        # len(data.dep_list) <= 4 indicates no dependency list found
        log.info(f'({__my_name__}) Searching for project source files')

        if not data.dep_list:
            _get_json_file(data.base_dir.joinpath(data.save_file))

        # Process directories
        if data.file_list is None:
            log.debug(f'({__my_name__}) Starting new file search')
            data.file_list = {data.proj_dir: None}
        else:
            log.debug(f'({__my_name__}) Updating file list')

        _dir_list = _get_empty_items()
        while _dir_list:
            for _key in _dir_list:
                _get_directory(_key)
            _dir_list = _get_empty_items()

    # Done/skipped finding deps, now to check them

    return


# #####################################################################################
# #####################################################################################
# #####################################################################################
# #####################################################################################


if __name__ == "__main__":
    import argparse

    __help__ = """
    check_deps.py [options]

    Positional parameters:
    If -f/--full specified or "(project)-deps.json" does not exist, search for all dependencies
    before testing.

    """
    parser = argparse.ArgumentParser(usage=__help__, description='Find module dependencies in a Python package')
    parser.add_argument('-s', '--start', help='Python script to start program')
    parser.add_argument('-t', '--test', help='Include test directory (default False)', action='store_true')
    parser.add_argument('-f', '--full', help='Search for dependencies prior to checking', action='store_true')
    parser.add_argument('-j', '--save', help='JSON-format dependency file')
    parser.add_argument('-v', help='Increase debuging level for each -v', action='count', default=0)
    args = parser.parse_args()

    _levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    debug = min(len(_levels), args.v + 1) - 1
    debug = max(0, debug)
    log.setLevel(logging.getLevelName(_levels[debug]))
    print(f'Settng log level to {logging.getLevelName(_levels[debug])}')

    if args.start is not None and args.start.endswith('.py'):
        data.start_py = args.start

    check_deps(full=args.full, testdir=args.test, jfile=args.save)
