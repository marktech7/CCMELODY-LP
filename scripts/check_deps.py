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
    project : {
                "version"* : Project version this file refers to
                module : {
                            "status"[1] : "optional" | "dev" | "new" | "ignore",  # "required" if not defined
                            "os"[1] : "linux" | "windows" | "darwin",  # O/S Agnostic if not defined
                            "version"[1] : min [, max],
                            repo[2] : [ repo_pacakge_name, repo_package_name, ... ],
                            "parent"[2] : module,
                            "notes"[1] : "Module notes"
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
from pathlib import Path

if __name__ == '__main__':
    log = logging.getLogger()
else:
    log = logging.getLogger(__name__)


class DataClass(object):
    """
    Class to hold module-level defines
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_dir = None  # Project base directory
        self.proj_dir = None  # Subdirectory of base_dir where source files are located
        self.test_dir = None  # Directory where tests are located
        self.file_list = None  # Keep track of files to check
        self.dep_list = None  # (dict() of JSON file contents
        self.save_file = None  # JSON file


data = DataClass()
ExclDir = ['js', 'resources']
ExclFile = ['resources.py']


def _get_deps(chk, builtin=False, stdlib=False, testing=False):
    """Helper function to scan file and search for dependencies.

    :param Path chk: File to scan. Must already exist and be a regular file
    :param bool builtin: Include built-in dependency
    :param bool stdlib: Include standard lib dependency
    :param bool testing: Include test dependencies except builtins

    :return: ( [direct imports], [from imports] )
    :rtype: tuple ([direct imports or None], [from imports or None])
    """

    _deplist = []  # Direct import "import xxx"
    _fromlist = []  # From import "from xxx import ..."

    log.debug(f'(_get_deps) Scanning {chk}')
    try:
        with chk.open('r') as fp:
            _bigstring = False
            _docscring = False
            for _line in fp:
                _line = _line.strip()
                if _line.startswith("'''"):
                    if not _line.endswith("'''"):
                        _bigstring = not _bigstring
                        continue
                elif _line.startswith('"""'):
                    if not _line.endswith('"""'):
                        _docstring = not _docscring
                    continue
                elif _bigstring or _docscring:
                    continue
                elif _line.startswith('#') or len(_line) < 5:
                    continue

                # log.debug(f'(_get_deps) Checking "{_line}"')
                if 'import' in _line:
                    _line = _line.strip()
                    log.debug(f'(_get_deps) Found import "{_line}"')
                    # Check for continuation line
                    if _line.endswith('\\'):
                        log.debug('(_get_deps) Found continuation line mark')
                        while True:
                            _l = fp.readline()
                            _l = _l.strip()
                            _line = f'{_line} {_l}'

                            # Check for another continuation line
                            if not _l.strip().endswith('\\'):
                                break
                    if _line.startswith('import '):
                        _deplist.append(_line)
                    elif _line.startswith('from '):
                        _fromlist.append(_line)

    # Until we find out what exceptions to exclude, reraise
    except Exception as e:
        raise

    if not _deplist:
        _deplist = None
    if not _fromlist:
        _fromlist = None

    log.debug(f'(_get_deps) Returning direct: {_deplist}')
    log.debug(f'(_get_deps) Returning from  : {_fromlist}')

    return (_deplist, _fromlist)


def get_deps(proj, chk=None):
    """Process dependency list and verify status of installed dependencies

    Print to stdout status of dependency.
    Does not include standard lib or built-in packages

    :param str proj: Project name
    :param Path chk: File to check. use data.file_list if None
    :return: Tuple of bool (required, optional, developer) dependency status
    :rtype: tuple
    """
    log.info('(get_deps) Starting dependency checks')

    _req = _opt = _dev = True

    _count = 10
    for _k in data.file_list:
        _count -= 1
        _p = Path(_k)
        if data.file_list[_k] != 'NOFILES':
            for _f in data.file_list[_k]:
                if 'NOFILES' in _f:
                    continue
                _c = _p.joinpath(_f)
                if _c.exists() and _c.is_file():
                    pkg, mod = _get_deps(_c)

        if _count < 1:
            break

    print(f'\nRequired  dependencies {"good" if _req else "not fully met"}')
    print(f'Optional  dependencies {"good" if _opt else "not fully met"}')
    print(f'Developer dependencies {"good" if _dev else "not fully met"}\n')

    return


def _find_files(_dir, e_dir, e_file, i_ext=('.py')):
    """Helper to list files in (dir)

    :param Path dir_: Directory to search
    :param list e_dir: List of directory names to exclude
    :param list e_file: List of file names to exclude
    :param list i_ext: List of valid filename extensions to look for

    :return: (Directory list, File list)
    :rtype: tuple
    """
    _e_dir = [] if e_dir is None else e_dir
    _e_file = [] if e_file is None else e_file
    _dirs = []
    _files = []

    for _f in _dir.iterdir():
        if _f:
            if _f.is_dir() and \
                    _f.name not in _e_dir and \
                    not _f.name.startswith('.') and \
                    _f not in _dirs:
                _dirs.append(_f)

            elif _f.is_file() and \
                    _f.name not in _e_file and \
                    not _f.name.startswith('.') and \
                    _f.suffix in i_ext and \
                    _f.name not in _files:
                _files.append(_f.name)

    if len(_dirs) < 1:
        _dirs = None
    if len(_files) < 1:
        _files = None

    return (_dirs, _files)


def find_files(base, excl_dir=ExclDir, excl_file=ExclFile):
    """Search through (base) for source files to check

    :param Path base: Base directory of project
    :param DataClass data: Class with required data
    :param list excl_dir: List of directory names to exclude
    :param list excl_file: List of file names to exclude

    :return: dict of {base: [files]}
    :rtype: dict
    """

    _excl_dir = excl_dir
    _excl_file = excl_file

    if '__pycache__' not in _excl_dir:
        _excl_dir.append('__pycache__')

    if base in _excl_dir:
        log.debug(f'(find_files) {base} in exclusion list - skipping')

    _excl_file = [] if excl_file is None else excl_file
    log.info(f'(find_files) base={base} excl_dir={_excl_dir}, excl_file={_excl_file}')

    if base not in data.file_list:
        data.file_list[base] = None

    log.debug(f'(find_files) Starting file search at base {base}')
    _dirs, _f = _find_files(base, e_dir=_excl_dir, e_file=_excl_file)

    if _dirs is None and _f is None:
        print(f'(find_files) Removing {base} from list')
        _ = data.file_list.pop(base)
        return

    if _dirs is not None:
        for _d in _dirs:
            if _d not in data.file_list:
                data.file_list[_d] = None

    if _f is None:
        data.file_list[base] = "NOFILES"
    else:
        data.file_list[base] = _f

    log.debug(f'(find_files) Returning {data.file_list[base]}')

    return


def save_json_file(src, deps):
    """Save dependency list to file. Return None on error.

    :param Path src: File to save to
    :param dict deps: Dependency dictionary

    :return: Path or None
    """
    log.info(f'(save_json_file) Saving data to {src}')
    if type(deps) is not dict:
        log.warning('(save_json_file) Cannot save data - wrong type (not dict)')
        return None

    try:
        with open(src, 'w') as fp:
            log.debug(f'(save_json_file) Saving data to {src}')
            json.dump(deps, fp, indent=4, sort_keys=True)

    except Exception as err:
        log.warning(f'(save_json_file) Error saving data: ({err=}')
        return None

    log.info(f'(save_json_file) Data saved to {src}')
    return src


def get_json_file(src):
    """Initialize the dep_list{}

    If json_file exists, populate from previously saved list.
    base_dir() must already be checked before calling this function.

    :param Path src: Fully qualified file path/name
    :rtype: dict or None
    """
    log.info(f'(get_json_file) Checking for previous {src} dependency list')

    if src.exists():
        log.info(f'(get_json_file) Parsing {src}')
        try:
            with open(src, 'r') as fp:
                _ret = json.load(fp)
                log.info('(get_json_file) Loaded JSON file')
                log.debug(_ret)
                return _ret
        except json.JSONDecodeError:
            log.warning(f'(get_json_file) {src} appears to be corrupted - returning new dictionary')
    else:
        log.info(f'(get_json_file) Source {src} does not exists, returning new dictionary')

    return dict()


def get_base_dirs(proj, base=None):
    """Process source files in 'project' for dependencies.

    :author: Ken Roberts <alisonken1_#_gmail_dot_com>
    :copyright: OpenLP

    :param str proj: Project name
    :param str base: Base directory where 'project' is located

    :returns: tuple(base_dir, project_dir)
    :raises: FileNotFoundError
    """
    log.info('(get_base_dirs) Getting project base')
    _base = Path(__name__).absolute() if base is None else Path(base).absolute()
    if __name__ in _base.parts:
        # No base directory given, derive base directory from this file
        log.debug(f'(get_base_dirs) Starting from {_base}')
        _base = Path(*_base.parts[:-1])

    log.debug(f'(get_base_dirs) Initial base: {_base}')
    # Get the project base directory
    for i in range(3):
        log.debug(f'(get_base_dirs) Checking "{_base}"')
        _c = _base.joinpath(proj)
        if _c.exists() and _c.is_dir() and _c.name == proj:
            _base = _c
            log.debug(f'(get_base_dirs) Found {_base}')
            break
        else:
            _base = _base.parent

    if _base.exists() and _base.is_dir() and _base.name == proj:
        log.debug(f'(get_base_dirs) Resolving {_base}')
        _base.resolve()
    else:
        log.error(f'(get_base_dirs) Could not find "{proj}" sources')
        raise FileNotFoundError(f'(get_base_dirs) Could not find "{proj}" sources')

    log.info(f'(get_base_dirs) Base direcotory: {_base.parent}')
    log.info(f'(get_base_dirs) Project directory: {_base}')
    return (_base.parent, _base)


def check_deps(proj, base=None, full=False, start=None, jfile=None, testdir=None, excl_dir=ExclDir, excl_file=ExclFile):
    """Entry point for dependency checks

    :param str proj: Project name
    :param base: Base directory that contains project - default use __name__ as starting point
    :type base: str or None
    :param start: Script to run for starting project
    :type start: str or None
    :param jfile: Name of JSON file
    :type jfile: str or None
    :param bool full: Force full dependency check if True
    :param testdir: Name of test directory
    :type testdir: str or None

    :return: Path or None
    """
    _first_run = True
    _recurse = full

    log.info('(check_deps) Starting dependency search')
    log.info(f'(check_deps) initial file list: {data.file_list}')

    # Get base directory and project directory
    data.base_dir, data.proj_dir = get_base_dirs(proj=proj, base=base)

    # Save dependency file
    _jfile = f'{proj}-deps.json' if jfile is None else jfile
    data.save_file = Path(data.base_dir, _jfile)

    if not data.save_file.exists():
        _recurse = True

    data.dep_list = get_json_file(data.save_file)

    if proj not in data.dep_list:
        data.dep_list[proj] = []

    if not _recurse and proj in data.dep_list:
        log.info('(check_deps) Dependency check only')

    else:
        log.info('(check_deps) Full scan check starting')
        _recurse = True
        data.file_list = dict()
        data.file_list[data.proj_dir] = None

        if start is not None:
            log.debug(f'(check_deps) Checking for start file {start}')
            _f = Path(data.base_dir, start)
            if _f.is_file():
                log.debug(f'(check_deps) Start file: {_f}')
                data.file_list[data.base_dir] = [_f.name]

        if testdir:
            log.debug('(check_deps) Checking for test directory')
            _d, _ = _find_files(data.base_dir, [], [])
            if _d is not None:
                for _f in _d:
                    if 'test' in _f.name:
                        log.debug(f'(check_deps) Adding "{testdir}" directory to check')
                        data.test_dir = _f
                        data.file_list[_f] = None

        while _first_run or _recurse:
            _first_run = False
            _check = None
            while _check is None:
                for _d in data.file_list:
                    # log.debug(f'(check_deps:_check) Checking {_d}')
                    if not data.file_list[_d]:
                        _check = _d
                        break
                # No more checks to run
                break

            if _check is None:
                _recurse = False
                break
            log.debug(f'(check_deps) Getting files from {_check}')
            find_files(base=_check, excl_dir=excl_dir, excl_file=excl_file)

        # Finished dependency checks - save results to JSON file
        _chk = save_json_file(data.save_file, data.dep_list)
        if _chk is None:
            log.error(f'(check_deps) Problem saving data to {data.save_file}')

    # Files found - time to check dependencies
    get_deps(proj, data.dep_list[proj])

    '''
    print(f'\ndata.base_dir: {data.base_dir}')
    print(f'data.proj_dir: {data.proj_dir}')
    print(f'data.test_dir: {data.test_dir}')
    print(f'data.save_file: {data.save_file}\n')

    if data.file_list is not None:
        print('data.file_list:')
        for k in data.file_list:
            # print(f'    {k}: {data.file_list[k]}')
            print(f'    {k}')
    print(f'\ndata.dep_list: {data.dep_list}')
    '''

    # Return data.save_file if successful
    return data.save_file


if __name__ == "__main__":

    import argparse

    logging.basicConfig(format='%(levelname)-10s :  %(message)s')

    __help__ = """
    check_deps.py project [options]

    Positional parameters:
        project  : (Required) Project name
        start    : Program file that runs your package (if available)
        base_dir : Base directory where project is located
                   If not given, will search starting with the directory this
                   script is in and go up the tree (up to 2 levels) to find
                   "project" directory

    If -f/--full specified or "{project}-deps.json" does not exist, search for all dependencies
    before testing.

    """
    parser = argparse.ArgumentParser(usage=__help__, description='Find module dependencies in a Python package')
    parser.add_argument('project', nargs='+')
    parser.add_argument('-b', '--base_dir', help='Base directory of project', default=None)
    parser.add_argument('-s', '--start', help='File that runs the program from CLI', default=None)
    parser.add_argument('-t', '--test', help='Include test directory (default False)', action='store_true')
    parser.add_argument('-f', '--full', help='Search for dependencies prior to checking', action='store_true')
    parser.add_argument('-v', help='Increase debuging level for each -v', action='count', default=0)
    args = parser.parse_args()

    _levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    debug = min(len(_levels), args.v + 1) - 1
    debug = max(0, debug)
    log.setLevel(logging.getLevelName(_levels[debug]))
    print(f'Settng log level to {logging.getLevelName(_levels[debug])}')

    _proj = args.project[0]
    _start = args.start
    _base = args.base_dir
    _full = args.full
    _test = args.test
    print(f'Setting project to "{_proj}"')

    # Override named options in case they were defined as positional parameters
    if len(args.project) > 1:
        _start = args.project[1]
    if len(args.project) > 2:
        _base = args.project[2]

    '''
    print('args   : ', args)
    print('_proj  : ', _proj)
    print('_start : ', _start)
    print('_base  : ', _base)
    print('_full  : ', _full)
    print('_test  : ', _test)
    '''

    print(f'Starting dependency checks for "{_proj}"')
    _jsave = check_deps(proj=_proj, base=_base, start=_start, full=_full, testdir=_test)
    if _jsave is None:
        print(f'WARNING: Error saving list to {_jsave}')
    else:
        print(f'Dependency list saved to {_jsave}')
