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

"""Parse Python source files and verify dependencies are met

:author: Ken Roberts <alisonken1_#_gmail_dot_com>
:copyright: OpenLP
"""
import json
import logging
import pkgutil
import re
import sys

from copy import copy, deepcopy
# from importlib.machinery import PathFinder
from pathlib import Path

if __name__ != '__main__':
    log = logging.getLogger(__name__)


CHECK_MARKERS = {'built-in': '###-BUILTIN-###',
                 'check': '###-CHECK-###',
                 'ignore': '###-IGNORE-###',
                 'lib-dynload': '###-STD-LIB-###',
                 'module': '###-3RD-PARTY-###',  # alias for 'site-packages'
                 'site-packages': '###-3RD-PARTY-###',
                 'std': '###-STD-LIB-###',
                 'unk': '###-UNKNOWN-###',
                 'sysunk': None,  # _check_module adds actual marker for specific module
                 # During actual checks, these can be ignored since they are built-in or part of stdlib
                 # unless otherwise specified in module checks
                 '###-BUILTIN-###': 'built-in',
                 '###-STD-LIB-###': 'std',
                 }
# Exclude directories from project
EXCLDIR = ['__pycache__', 'resources', 'documentation', 'docs', 'js']
# Exclude files
EXCLFILE = ['resources.py']
# Include file extensions
INCLEXT = ['.py']
IS_WIN = sys.platform.startswith('win')
IS_LIN = sys.platform.startswith('lin')
IS_MAC = sys.platform.startswith('dar')
JSON_File = 'project-deps.json'
# Get the python installation directory.
# Used to assist debugging possible module import issues.
PYTHON_BASE = Path(pkgutil.__spec__.origin).parent
RE_Docstring = re.compile(r'''['"]{3}''')


class Singleton(type):
    """
    Provide a `Singleton` metaclass https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}

    def __call__(self, *args, **kwargs):
        """
        Create a new instance if one does not already exist.
        """
        if self not in self._instances:
            self._instances[self] = super().__call__(*args, **kwargs)
        return self._instances[self]

    def __iter__(self):
        return iter(self._all)


class DataClass(metaclass=Singleton):
    # Class attributes to expose
    _all = ['project', 'dir_list', 'dir_check', 'import_list', 'check']
    _default_project = {'version': 0,
                        "name": None,
                        "proper": None,
                        "project_version": None,
                        "git_version": None,
                        "language": {"python": {'version': ">= 3.6",
                                                'base': str(PYTHON_BASE)}
                                     },
                        "modules": dict(),
                        }

    def __new__(cls, *args, **kwargs):
        cls.check = dict()  # Dependencies found need to verify against cls.project['modules']
        cls.dir_check = dict()  # Keep track of directories to parse relative to cls.dir_list['base']
        cls.dir_list = {'base': Path('.').resolve(),  # Project base directory
                        'project': Path('.'),  # Project source base directory relative to "base"
                        'test': None}  # Test scripts directory (if applicable) relative to "base"
        cls.import_list = dict()  # Keep track of import lines
        cls.INSTALLED = dict()
        cls.project = deepcopy(cls._default_project)  # JSON data

        for f in pkgutil.iter_modules(path=sys.path[1:]):
            p = Path(f.module_finder.path)
            # p is path to installed module
            # p.name is the directory in the python libs where package is installed
            if p.name in CHECK_MARKERS:
                c = CHECK_MARKERS[p.name]
            elif p.name.startswith('python'):
                c = CHECK_MARKERS['std']
            else:
                c = CHECK_MARKERS['unk']
            cls.INSTALLED[f.name] = {'path': p, 'check': c}

        return cls

    @classmethod
    def _check_module(self, module):
        """Check for module not found at initialization

        :param str module: Module name to check
        :rtype: bool
        """
        try:
            c = pkgutil.resolve_name(module)
            mod_ = dict()
            if c.__spec__.origin in CHECK_MARKERS:
                mod_['check'] = CHECK_MARKERS[c.__spec__.origin]
            else:
                mod_['check'] = f'###-UNK-{c.__spec__.origin}-###'
            mod_['path'] = None if not hasattr(c.__spec__, 'path') else c.__spec__.path
            self.INSTALLED[module] = mod_
        except ModuleNotFoundError:
            return False
        return True

    @classmethod
    def check_import_line(self, chk):
        """
        Check for import items and add to list.
        Populate self.list_imports with dependencies

        :param str chk: Import line check
        """
        def chk_import(check):
            """Check if import already in check list

            :param list check: List of imports to check
            """
            for i in check:
                if i.startswith(self.project['name']) or i.startswith('.'):
                    log.debug(f'({__my_name__}.chk_import) Skipping project import')
                    continue

                log.debug(f'({__my_name__}.chk_import) Checking "{i}"')
                dep = i.split('.', 1)[0]
                if dep not in self.import_list:
                    log.debug(f'({__my_name__}.chk_import) Adding "{dep}"')
                    self.import_list[dep] = []
                    if dep in self.INSTALLED:
                        self.import_list[dep].append(self.INSTALLED[dep]["check"])
                    elif self._check_module(dep):
                        self.import_list[dep].append(self.INSTALLED[dep]["check"])
                    else:
                        self.import_list[dep].append(CHECK_MARKERS["unk"])

                if dep == i or i in self.import_list[dep]:
                    log.debug(f'({__my_name__}.chk_import) Skipping duplicate "{i}"')
                    continue
                log.debug(f'({__my_name__}.chk_import) Adding "{i}" to import_list["{dep}"]')
                self.import_list[dep].append(i)

        __my_name__ = 'DataClass.check_import_line'
        log.debug(f'({__my_name__}) Checking "{chk}"')
        # Ignore anything after " as " since it's a rename of the import
        # Replace any comma's with space so we can split the line easier
        if 'import' not in chk or chk.split()[0] not in ('import', 'from'):
            log.debug(f'({__my_name__}) Skipping non-import line')
            return

        _arr = chk.split(' as ')[0].replace(',', ' ').split()
        # _arr[0] = "import"
        #       _arr[1:] single | multiple dependencies
        # _arr[0] == "from"
        #       _arr[1] = dependency
        #       _arr[2] == "import"
        #       _arr[3:] = single | multiple attributes

        if _arr[0] == 'import':
            chk_import(_arr[1:])

        elif _arr[0] == 'from':
            # Keep it as an array for later checks
            chk = []
            for i in _arr[3:]:
                chk.append('.'.join([_arr[1], i]))
            chk_import(chk)
        else:
            log.debug(f'({__my_name__}) Skipping non-import line')
        return

    @staticmethod
    def check_json(itm):
        """JSON serialize an object

        :param itm: Object to serialize
        :rtype: string | list | dict
        """
        if issubclass(itm.__class__, Path):
            return str(itm)
        return itm

    @classmethod
    def load_json(self, f=JSON_File):
        """
        Populate DataClass.project from JSON file.

        :param Path f: Name of file to load JSON from relative to base directory
        """
        __my_name__ = 'DataClass.load_json'
        src = self.dir_list['base'].joinpath(f)
        ret = None
        try:
            log.info(f'({__my_name__}) Parsing {src}')
            with src.open('r') as fp:
                ret = json.load(fp)
                log.info(f'({__my_name__}) Loaded JSON file')
                self.project = ret
                return
        except FileNotFoundError:
            log.warning(f'({__my_name__}) Source {src} is missing - using defaults')
            self.project = deepcopy(self._default_project)
        except json.JSONDecodeError:
            log.warning(f'({__my_name__}) Source {src} appears to be corrupted')

    @classmethod
    def log(self, lvl, installed=False):
        """Send DataClass items to logger

        :param funct lvl: Logger instance to log with
        """
        _all = copy(self._all)
        if installed:
            _all.extend(['INSTALLED'])
        chk = json.dumps({k: getattr(self, k) for k in _all}, indent=4, default=self.check_json, sort_keys=True)
        chk = chk.split('\n')
        lvl(f'{self.__name__} {{')
        for k in chk[1:]:
            lvl(k)

    @classmethod
    def save_json(self, f=JSON_File):
        """Save DataClass.project to project-deps.json

        :param Path f: File to save to
        """
        __my_name__ = 'DataClass.save_json'
        src = self.dir_list['base'].joinpath(f)
        try:
            with open(src, 'w') as fp:
                # Skipkeys=True should only skip the ModSpec key
                # since importlib.machinery.ModuleSpec is non-serializable at this time
                json.dump(self.project, fp, indent=4)

        except Exception as err:
            log.warning(f'({__my_name__}) Error saving data: ({err=}')
            return False

        log.info(f'({__my_name__}) Data saved to {src}')
        return True

    @classmethod
    def set_name(self, name):
        """Set Data attributes that rely on project name

        :param str name: Project name to set
        """
        self.project['name'] = name
        self.dir_list['project'] = self.dir_list['project'].joinpath(name)


# Initialize DataClass
Data = DataClass()

###########################################################
#                                                         #
#                Private Functions                        #
#                                                         #
###########################################################


def find_all_imports(src=Data.dir_list['project']):
    """Search project for all imports

    Updates Data.import_list

    :param Path src: Directory of project source relative to Data.dir_list['base']
    """
    __my_name__ = 'find_all_imports'
    log.info(f'({__my_name__}) Starting project scan')
    if not Data.dir_check:
        Data.dir_check[Data.dir_list['project']] = None
    while Data.dir_check:
        chkdir, chkfiles = Data.dir_check.popitem()
        log.debug(f'({__my_name__}) Checking {chkdir}')
        dirs = None
        chk = chkfiles
        if chkfiles is None or not chkfiles:
            dirs, chk = parse_dir(chkdir)
        if dirs is not None:
            log.debug(f'({__my_name__}) Updating directory check list')
            Data.dir_check.update(dirs)
        if chk is None:
            # No files to parse
            log.debug(f'({__my_name__}) No files to parse, continuing')
            continue
        for itm in chk:
            parse_source(chkdir.joinpath(itm))


def parse_source(srcfile):
    """Loads the source file (as list) and strip all non-import lines

    Calls DataClass.check_import() to add dependency to DataClass.imports_list.

    :param Path srcfile: Source file to parse
    """
    __my_name__ = "parse_source"
    log.info(f'({__my_name__}) Starting source file checks {srcfile}')

    def check_docstring(s, _l):
        """ Helper to check if docstring in line

        Since a docstring does not contain imports we can use,
        just remove docstring from src list and return.

        Initial string 's' is used to select
        single- or double-quoted docstring to check.

        :param str s: Initial docstring to check
        :param list _l: Source list to continue checks
        """
        log.debug(f'({__my_name__}.check_docstring) {s}')
        m = RE_Docstring.search(s)
        if not m or len(re.findall(m.group(), s)) == 2:
            # len() == 2 means single-line docstring
            return
        # Don't need to keep calling m.group(), so just
        # retrieve the group
        m = m.group()
        while _l:
            s = _l.pop(0).strip()
            log.debug(f'({__my_name__}.check_docstring) {s}')
            # At this point, there should only be the closing docstring
            if re.findall(m, s):
                break
        return

    with srcfile.open() as fp:
        src = fp.readlines()

    chk_cont = None  # Used for multi-line continuations

    while src:
        line = src.pop(0).strip()
        if not line:
            log.debug(f'({__my_name__}) Skipping blank line')
            continue

        if RE_Docstring.search(line):
            log.debug(f'({__my_name__}) Checking docstrings')
            check_docstring(line, src)
            continue

        if '#' in line:
            if line.startswith('#'):
                log.debug(f'({__my_name__}) Skipping comment')
                continue
            # Not a full-line comment, so strip out the inline comment part
            # and continue with checks
            line = line.split('#', 1)[0]

        if chk_cont or line.endswith('\\'):
            if chk_cont:
                chk_cont = f'{chk_cont} {line}'
            else:
                chk_cont = line
            if chk_cont.endswith('\\'):
                log.debug(f'({__my_name__}) Continue check "{line}"')
                chk_cont = chk_cont.rstrip('\\').strip()
                continue
            line = chk_cont
            chk_cont = None
            log.debug(f'({__my_name__}) Finished "{line}"')

        # Passed checks, so time to check for imports
        if 'import' in line:
            DataClass.check_import_line(line)
            continue
        log.debug(f'({__my_name__}) skipping non-import line')


def parse_dir(srcdir, e_dir=EXCLDIR, e_file=EXCLFILE, i_ext=INCLEXT):
    """Parse directory and retrieve valid entries

    Parse srcdir and return valid (directories, files) tuple

    :param Path srcdir: Directory relative to Data.dir_list['base']
    :param list e_dir: List of directory names to exclude
    :param list e_file: List of files to exclude
    :param list i_ext: List of file extensions to include

    :return: ( {directory: None} or None, [list_of_files] | None )
    :rtype: tuple
    """
    __my_name__ = "parse_dir"
    log.info(f'({__my_name__}) Scanning {srcdir}')
    if not srcdir.is_dir():
        log.debug(f'({__my_name__}) {srcdir} not a directory - returning')
        return None
    dirs = dict()
    files = []

    for chk in srcdir.iterdir():
        if chk.is_dir() and chk.name not in e_dir and chk not in dirs:
            log.debug(f'({__my_name__}) Adding {chk} to directory list')
            dirs[chk] = None
            continue
        elif chk.is_file() and chk.suffix in i_ext and chk.name not in e_file:
            log.debug(f'({__my_name__}) Adding {chk.name} to file list')
            files.append(chk.name)
            continue
        log.debug(f'({__my_name__}) Skipping entry {chk}')

    if not files:
        files = None
    if not dirs:
        dirs = None
    return (dirs, files)


if __name__ == "__main__":
    import argparse

    __help__ = """
    check_deps.py [options]

    Positional parameters:
    If -f/--full specified or "project-deps.json" does not exist, search for all dependencies
    before testing.

    """
    parser = argparse.ArgumentParser(usage=__help__, description='Find module dependencies in a Python package')
    parser.add_argument('-f', '--full', help='Search for dependencies prior to checking', action='store_true')
    parser.add_argument('-j', '--json', help='JSON-format dependency file')
    parser.add_argument('-l', '--log', help='Log save file')
    parser.add_argument('-p', '--project', help='Project Name', default=None, action='store')
    parser.add_argument('-t', '--test', help='Include test directory (default False)', action='store_true')
    parser.add_argument('-s', '--saved', help='JSON ifle to load (default project-deps.json)',
                        default='project-deps.json')
    parser.add_argument('-v', help='Increase debuging level for each -v', action='count', default=0)
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(filename=args.log, filemode='w', format='%(levelname)-10s :  %(message)s')
        print(f'Saving log output to {args.log}')
    else:
        logging.basicConfig(format='%(levelname)-10s :  %(message)s')
    log = logging.getLogger()

    _levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    debug = min(len(_levels), args.v + 1) - 1
    debug = max(0, debug)
    log.setLevel(level=logging.getLevelName(_levels[debug]))
    print(f'Settng log level to {logging.getLevelName(_levels[debug])}')

    if args.saved:
        Data.load_json(f=args.saved)
    else:
        Data.load_json()

    if Data.project['name'] is None:
        if args.project is None:
            Data.save_json()
            print(f'\n\nEdit {JSON_File} and set "name" to name of project and try again\n')
            print('Or add -p <project> option')
            sys.exit()
        Data.set_name(args.project)

    Data.log(lvl=log.debug)
    if args.full or not Data.project.modules:
        find_all_imports()
    Data.log(lvl=log.debug)
