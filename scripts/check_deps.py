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

NOTE: If you include this script in your project, you may want to
        adjust some of the DataClass parameters to match your project.

Should be run in the base directory of your project.
ex: base = (current_directory)
    project = base/project_name

This script goes through a project and builds a dependency
list. It only searches for "import" or "from ... import" to validate
dependencies.

Modules within project are ignored since we only want external
dependencies listed.

After building a dependency list, project managers can then
assign the appropriate status for each dependency.

"project-dep.json" format:

    {
        "project"        : string,
        "name"           : string,
        "version"[1]     : string,
        "git_version"[1] : string,
        "dep_list"        : { module : { "status"  : string,
                                         "os"      : string,
                                         "version" : string,
                                         "parent"  : string,
                                         "notes"   : string,
                                         "repo"    : { repo : list,
                                                       repo : list
                                                     }
                                         },
                              module : { ... },
                              ...
                             }
        "dep_check"      : Dict used by script for dependency checks
    }

Main Item definitions:

    "project"       : Name of project (ex. "project": "openlp"
    "name"          : Proper name of project (ex. "name" : "OpenLP"
    "version"       : Project version (ex. "version" : "2.7.4"
    "git_version"   : Git repo version (ex. "git_version" : "2.7.4-261-g624647327"
    "deplist"       : Object holding dependencies

"deplist" definitions:

    "deplist" : module { ... }

    The "deplist" object holds the dependencies.

"deplist": module object

    "module" is the name of the depdendency. Example:

        "deplist" : { "PyQt5" : { ... },
                      "sqlalchemy" : { ... }
                    }

    Format for "deplist": module object

        module : {"status"  : string,
                  "os"      : string,
                  "version" : string,
                  "parent"  : string,
                  "notes"   : string,
                  "repo"    : object
                  }

        "module"  : Dependency listed
        "os"      : If given, this module is only needed for the listed O/S
        "status"  : If given, the project status of this dependency.
                    If not given, "required" is assumed.
                    options: required | optional | new | ignore
        "version" : If given, required module version.See [1] for options.
        "parent"  : If given, the parent module of this dependency.
        "notes"   : If given, developer notes for this dependency.
        "repo"    : If given, Object holding repository package name information.

"deplist" : "module" : "repo" object

    Object for holding module repository information.

    Format for "deplist": module object

        "repo" : { reponame : list,
                   reponame : list
                 }

        "reponame"   : Name of the repository
                       ex: "pypi", "fedora", ...
        list         : List of package name(s) for this repository

"deplist" example:

        { "deplist" : {"QtWebEngineWidget" : {"status"   : "required",
                                              "os"       : "linux",
                                              "parent"   : "PyQt5",
                                              "notes"    : "developer QtWebEngineWidget notes"
                                             },
                       "QtWebEngine" : {"status" : "required",
                                        "os"     : "windows",
                                        "parent" : "PyQt5",
                                        "notes"  : "Developer QtWebEngine notes"
                                        },
                       "PyQt5" : {"status"   : "required",
                                  "version"  : ">= 5.12"
                                  "parent"   : "PyQt5",
                                  "notes"    : "developer PyQt5 notes"
                                  "repo"     : {"pypi"     : ["PyQt5"],
                                                "fedora"   : ["python3-qt5", "python3-pyqt5-sip"]
                                                }
                                 }
                       }
        }


    Note: If "status" is "new", dependency was found and has not been classified yet.
          If "status" is "ignore", then don't check

[1] https://docs.python.org/3/distutils/setupscript.html#relationships-between-distributions-and-packages

:author: Ken Roberts <alisonken1_#_gmail_dot_com>
:copyright: OpenLP
"""
# import importlib
import json
import logging
import os
import re
import sys

from copy import copy
from importlib.machinery import PathFinder, ModuleSpec
from pathlib import Path

__all__ = ['check_deps', 'json_file']

if __name__ != '__main__':
    log = logging.getLogger(__name__)


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
        if hasattr(self, '__showme__'):
            return iter(self.__showme__)

    @classmethod
    def pop_item(self, lst):
        """Pops the last item from a list"""
        if type(lst) is not list:
            log.warning(f'({self.__name__}:pop_item) Not a list - returning')
            return
        try:
            lst.pop(-1)
        except IndexError:
            log.warning(f'({self.__name__}:pop_item) Trying to pop an empty list')


class DataClass(metaclass=Singleton):
    """Class to hold module data"""
    __showme__ = ['base_dir',
                  'dep_default',
                  'dep_list_default',
                  'file_list',
                  'format_level',
                  'format_space',
                  'project',
                  'project_dirs',
                  'project_name',
                  'setup_opts',
                  'setup_py',
                  'start_file',
                  # Show last since they may be big
                  'imports_list',
                  'dep_list',
                  'dep_check',
                  ]

    def __repr__(self):
        return f'<DataClass: ' \
            f'base_dir={self.base_dir},' \
            f'dep_check={self.dep_check},' \
            f'dep_default={self.dep_default},' \
            f'dep_list={self.dep_list},' \
            f'dep_list_default={self.dep_list_default},' \
            f'file_list={self.file_list},' \
            f'format_level={self.format_level},' \
            f'format_space={self.format_space},' \
            f'imports_list={self.imports_list},' \
            f'project={self.project},' \
            f'project_dirs={self.dirs},' \
            f'project_name={self.project.name},' \
            f'setup_opts={self.setup_opts},' \
            f'setup_py={self.setup_py},' \
            f'start_file={self.start_file},' \
            '>'

    def __str__(self):
        return \
            f'base_dir={self.base_dir},' \
            f'dep_check={self.dep_check},' \
            f'dep_default={self.dep_default},' \
            f'dep_list={self.dep_list},' \
            f'dep_list_default={self.dep_list_default},' \
            f'file_list={self.file_list},' \
            f'format_level={self.format_level},' \
            f'format_space={self.format_space},' \
            f'imports_list={self.imports_list},' \
            f'project={self.project},' \
            f'project_dirs={self.dirs},' \
            f'project_name={self.project.name},' \
            f'setup_opts={self.setup_opts},' \
            f'setup_py={self.setup_py},' \
            f'start_file={self.start_file},'

    @classmethod
    def create(self):
        # Unless otherwise noted, all paths are relative to bae_dir
        # Default current directory
        self.base_dir = Path('.').resolve()
        self.project_name = None  # base_dir.name directory of project
        self.project_dirs = {'project': None,
                             'test': None,
                             'helpers': []
                             }
        # project['dir'] is where project source files are located
        #   Normal is base_dir.project_name
        #   Variant 1 is base_dir.project_name.src.project_name (ex. PyPI}
        # project['json'] is name of project json data
        #   Normal is f'{project_name}-deps.json'
        #   Variant 1 is 'project-deps.json'
        self.project = {'dir': None,
                        'name': None,  # Proper name of project - eg. 'OpenLP'
                        'version': None,
                        'git_version': None,
                        'version_file': '.version',
                        'json': None
                        }

        # The rest are used by this script for local use
        self.dep_list = None  # Contents of project['json'] file
        self.dep_list_default = {'project': self.project_name,
                                 'name': self.project['name'],
                                 'version': self.project['version'],
                                 'git_version': self.project['git_version']
                                 }
        self.dep_check = {}  # Intermediate dictionary of found dependencies
        self.file_list = None  # Keep track of files to check
        self.imports_list = []  # List of lines to check for imports
        self.setup_opts = None  # Options from setup.py
        self.setup_py = None  # setup.py if found
        self.start_file = None  # Hopefully the name of the script that starts the program
        # these two are used by PrettyLog
        self.format_level = 0
        self.format_space = {0: ''}
        #
        # Set some defaults
        self.dep_default = {'python': {'version': '>= 5.6',
                                       'status': 'required'},
                            'PyQt5': {'version': '>= 5.12',
                                      'status': 'required'},
                            'Qt5': {'version': '>= 5.9',
                                    'parent': 'PyQt5',
                                    'status': 'required'},
                            'pymediainfo': {'version': '>= 2.2',
                                            'status': 'required'},
                            'sqlalchemy': {'version': '>= 0.5',
                                           'status': 'required'},
                            'enchant': {'version': '>= 1.6',
                                        'status': 'required'}
                            }


class PrettyLog(metaclass=Singleton):
    """Pretty-printing log method for objects.

    Hopefully it's thread-safe as well.
    """
    __showme__ = ['width', 'indent', 'indent_str', 'indents', 'log_items']

    @classmethod
    def create(self):
        """Initialize the class"""
        # Possible stdout redirect on cli
        try:
            c, r = os.get_terminal_size()
        except OSError:
            c = 200
        self.width = c - 10
        self.indent = 0
        self.indent_str = ' ' * self.indent
        self.indents = {0: ''}
        self.log_items = []

    def format_line(self):
        """Split a line as needed for logging

        Retrieves the last item from log_items for logging.
        """
        def check_spaces(line):
            """Helper to find natural split point in line

            Find the last whitespace location in string that
            that fits within line-length boundaries

            :param str line: Line to check
            :return: 0 or last natural splitting point position
            :rtype: int
            """
            re_chk = [i for i in re.finditer('\s', line)]  # noqa
            if re_chk:
                return re_chk[-1].start()
            return 0

        item = self.log_items[-1]
        msg = item['txt'].__str__()
        lvl = item['lvl']
        if self.log_line(self, lvl=lvl, txt=msg):
            return

        last = len(msg)
        lead = self.get_lead(self)
        curr = 0
        while curr < last:
            pre_len = len(lead)
            # Double the prefix to make sure some long items
            # like fully-qualified paths can hopefully print
            size = curr + self.width - pre_len - pre_len
            _line = msg[curr:size]
            if curr + len(_line) >= last:
                # Last part of the line to log
                self.log_line(self, lvl=lvl, txt=_line)
                break

            chk = check_spaces(_line)
            if chk < 1:
                # No split point found in line, just log it
                log_chk = self.log_line(self, lvl=lvl, txt=_line)
                curr += len(_line)
            else:
                # Found a split point - adjust output to match
                log_chk = self.log_line(self, lvl=lvl, txt=_line[:chk])
                curr += chk
            if not log_chk:
                log.warning('(PrettyLog:format_line) Line failed to print')

    def get_lead(self):
        if self.indent not in self.indents:
            self.indents[self.indent] = '     ' * self.indent
        return self.indents[self.indent]

    @classmethod
    def log(self, txt, lvl=None, head=None, single=False):
        """
        :param txt: Text to log
        :type txt: object
        :param func lvl: Logging function (logging.debug, logging.info, ...)
        :param str head: Text prefix
        :param bool single: For lists, show each entry on a separate line
        """
        prefix = head if head is not None else ''
        # Check if we don't have to process further

        # If this script added to a different project, you
        # may have to adapt the isinstance() to your project.
        if not isinstance(txt, (Singleton)):
            if self.log_line(self, lvl=lvl, txt=f'{prefix}{txt}'):
                return

        self.log_items.append({'lvl': lvl, 'head': head, 'txt': txt})
        # Too long to log onto a single line. Separate processing.
        if type(txt) is list:
            self.log_list(self, single)
        elif type(txt) is dict:
            self.log_dict(self)
        elif type(txt) is ModuleSpec:
            self.log_modspec(self)
        else:
            self.log_obj(self)

        self.pop_item(self.log_items)

    def log_line(self, txt, lvl):
        """Common point to actually log.

        Verify the text to print will fit within the display
        terminal or specified width.

        :param str txt: Text to log
        :param func lvl: Logging level instance (logging.debug, logging.info, ...)
        :return: True if logged
        :rtype: bool
        """
        if not txt:
            return False
        _lvl = log.debug if lvl is None else lvl
        lead = self.get_lead(self)
        _line = f'{lead}{txt}'
        if len(_line) > self.width - len(lead):
            return False
        _lvl(_line)
        return True

    def log_dict(self):
        """Format a dictionary for logging"""
        item = self.log_items[-1]
        lvl = item['lvl']
        head = item['head']
        txt = item['txt']
        self.log_line(self, lvl=lvl, txt=f'{head} : {{')
        self.set_indent(self)
        for k, v in txt.items():
            # Recursion point
            self.log(lvl=lvl, head=f'{k}: ', txt=v)
        self.log_line(self, lvl=lvl, txt='}')
        self.set_indent(self, decr=True)

    def log_list(self, single):
        """Format a list object for logging"""
        item = self.log_items[-1]
        lvl = item['lvl']
        head = item['head']
        text = item['txt']
        self.log_line(self, lvl=lvl, txt=head)
        self.set_indent(self)
        if single:
            for itm in text:
                self.log_line(self, lvl=lvl, txt=itm)
        else:
            self.format_line(self)
        self.set_indent(self, decr=True)

    def log_modspec(self):
        """Print a ModuleSpec item"""
        item = self.log_items[-1]
        self.log_line(self, lvl=item['lvl'], txt=f'{item["head"]} ModuleSpec(too_long_to_show_for_now)')

    def log_obj(self):
        """Format a class object for logging"""
        item = self.log_items[-1]
        # if isinstance(item, (Singleton)):
        #    # Try and get the current instance
        #    item = item()
        lvl = item['lvl']
        head = item['head']
        text = item['txt']
        self.log_line(self, lvl=lvl, txt=(f'{head} {{'))
        self.set_indent(self)
        for k in text:
            self.log(lvl=lvl, head=f'{k}: ', txt=getattr(text, k))

        self.set_indent(self, decr=True)
        self.log_line(self, lvl=lvl, txt=('}'))

    def set_indent(self, decr=False):
        """Common routine to work with the indentation level of entries

        :param bool decr: Decrement indent level
        """
        if decr:
            if self.indent > 0:
                if self.indent in self.indents:
                    self.indents.pop(self.indent)
                self.indent -= 1
        else:
            self.indent += 1


DataClass.create()
PrettyLog.create()


# Exclude directories from project
ExclDir = ['__pycache__', 'resources', 'documentation', 'docs']
# Exclude directories in tests
ExclDirTest = ['js']
# Exclude files
ExclFile = ['resources.py']
InclExt = ['.py']

# Indicates there are no files in a directory list
No_Files_Marker = '###-NOFILES-###'

Dep_Check_Markers = {'ignore': '###-IGNORE-###',
                     'check': '###-CHECK-###',
                     'sys': '###-SYSTEM-###',
                     'unknown': '###-UNKNOWN-###',
                     }


###########################################################
#                                                         #
#                Private Functions                        #
#                                                         #
###########################################################


def _check_dependencies(depcheck):
    """Check each dependency in list for non-project dependencies

    Updates DataList.dep_list

    :param str depcheck: Line to scan and validate dependencies
    """
    __my_name__ = '_check_dependencies'

    def system_check(name, syschk=None):
        """Helper to do system checks on package"""
        _syscheck = False
        if name in sys.builtin_module_names:
            _syscheck = True
        elif syschk is not None:
            if syschk.name.startswith('python'):
                _syscheck = True
            elif syschk.parent.name.startswith('python'):
                _syscheck = True
            elif syschk.parent.name.startswith('lib-') and syschk.parent.parent.name.startswith('python'):
                _syscheck = True

        if _syscheck:
            log.debug(f'({__my_name__}.build_check) System module {name} - skipping')

        return _syscheck

    def build_check(name, spec, mark=Dep_Check_Markers['unknown']):
        """builds a dictionary with module check items

        DataClass.dep_check['name'] =  { 'spec': importlib.machinery.ModuleSpec
                                         'mark': Dep_Check_Markers[mark]
                                         }

        :param str name: Module name
        :param ModuleSpec spec: ModuleSpec instance
        :param str marker: Dep_Check_Markers[mark] entry
        """
        if name in DataClass.imports_list:
            # Already checked - ignore
            log.debug(f'({__my_name__}.build_check) Duplicate entry {name}')
            return

        _check = {'modulespec': spec,
                  'mark': mark}

        if hasattr(spec, 'origin'):
            path = Path(spec.origin).parent
            log.debug(f'({__my_name__}.build_check) Checking origin={spec.origin}')
            log.debug(f'({__my_name__}.build_check) Checking path={path}')
            if system_check(name, path):
                return
            log.debug(f'({__my_name__}.build_check) name={path.name} parent={path.parent.name}')

            if path.name == name and path.parent.name.startswith('site-'):
                log.debug(f'({__my_name__}.build_check) Possible site package {name}')
                _check['mark'] = Dep_Check_Markers['check']

        log.debug(f'({__my_name__}.build_check) Adding entry {name} as "{_check["mark"]}"')
        DataClass.dep_check[name] = _check

    def check_submodule(name):
        """Check module path to find parent module

        :param str name: Package name dotted.notation
        :param Path path:
        :rtype: (name, ModuleSpec) or None
        """
        # NOTE: Add from imports to check list
        search = copy(name)
        while search:
            log.debug(f'({__my_name__}.check_submodule) Checking {search}')
            chk = _get_spec(search)
            if chk:
                log.debug(f'({__my_name__}.check_submodule) Returning {search}')
                return (search, chk)
            search = '.'.join(search.split('.')[:-1])
        return None

    def check_module(name):
        """Helper to verify module"""
        if name.startswith(DataClass.project) or name.startswith('.') or system_check(name):
            log.debug(f'({__my_name__}.check_module) Ignoring project import {name}')
            return

        log.debug(f'({__my_name__}.check_module) Checking {name}')

        _name = name
        _spec = None
        if '.' in name:
            chk = check_submodule(_name)
            if chk is not None:
                _name, _spec = chk
        else:
            _spec = _get_spec(name)

        if _spec is None:
            log.debug(f'({__my_name__}.check_module) Spec not found: '
                      f'marking {_name} as "{Dep_Check_Markers["unknown"]}"')
            DataClass.dep_check[_name] = Dep_Check_Markers['unknown']
            return
        return build_check(name=_name, spec=_spec)

    # ########### END LOCAL FUNCTIONS ############

    log.info(f'({__my_name__}) Starting import checks on "{depcheck}"')

    lst = depcheck.replace(',', ' ').split()
    if lst[-2] == 'as':
        # Looks like we have an 'import ... as ..'
        lst = lst[-2]
    if lst[0] == 'import':
        for itm in lst[1:]:
            check_module(itm)

    # NOTE: Include from extras for later checks
    elif lst[0] == 'from':
        check_module(lst[1])

    else:
        log.warning(f'({__my_name__}) Invalid line? {depcheck}')


def _get_directory(base, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Process the project directory and add source files to DataClass.file_list

    Since we may have recursion issues, indicate the directory has not been
    scanned by setting entry to None instead of an empty list.

    :param Path base: Initial directory to process relative to DataClass.base_dir
    :param list e_dir: Directory names to exclude
    :param list e_file: File names to exclude
    :param list i_ext: File name extensions to include (default ['.py'])
    """
    __my_name__ = '_get_directory'

    if not base.is_dir():
        log.error(f'({__my_name__}) Base is not a directory - exiting')
        return

    log.info(f'({__my_name__}) Starting process on {base}')

    if base not in DataClass.file_list or DataClass.file_list[base] is None:
        DataClass.file_list[base] = []
    dirs, files = _list_dir(DataClass.base_dir.joinpath(base))

    # Process directories
    if dirs is not None:
        for chk in dirs:
            if chk not in DataClass.file_list:
                DataClass.file_list[chk] = None

    if files is None:
        # No files, so mark it as so
        DataClass.file_list[base] = No_Files_Marker
    else:
        for chk in files:
            # file_list key is directory, so just add file name to list
            DataClass.file_list[base].append(chk.name)
    PrettyLog.log(lvl=log.debug, head=f'({__my_name__}) Directory list: ', txt=DataClass.file_list[base])


def _get_project(proj=DataClass.project):
    """Finds the project directory

    Sets DataClass.proj_dir to (DataClass.base_dir)/dir.

    :param str proj: Name of project
    :return: None
    """
    __my_name__ = '_get_project'
    if DataClass.base_dir is None:
        DataClass.base_dir = Path('.').resolve()

    dirs, files = _list_dir(DataClass.base_dir)
    if dirs is None:
        log.error(f'({__my_name__}) Unable to determine starting point - exiting')
        return

    log.info(f'({__my_name__}) Starting base checks')
    _pkg_check = []
    _extra = []
    while dirs:
        _chk = dirs.pop()
        log.debug(f'({__my_name__}) Checking {_chk}')
        if _chk.name.startswith('test') and _chk.is_dir():
            log.debug(f'({__my_name__}) Setting test directory as "{_chk.name}"')
            DataClass.project_dirs['test'] = _chk
            continue
        elif _chk.name.startswith('script'):
            log.debug(f'({__my_name__}) Adding "{_chk.name}" to helpers list')
            DataClass.project_dirs['helpers'].append(_chk)
            continue
        elif _chk.joinpath('__init__.py').exists():
            log.debug(f'({__my_name__}) Adding "{_chk.name}" to possible')
            _pkg_check.append(_chk)
            continue
        _extra.append(_chk)

    log.debug(f'({__my_name__}) Finished processing directories')
    if len(_pkg_check) == 1:
        log.debug(f'({__my_name__}) Adding "{_pkg_check[0].name}" as project')
        DataClass.project_name = _pkg_check[0].name
        DataClass.project['dir'] = _pkg_check[0]
        DataClass.project['json'] = f'{DataClass.project_name}-deps.json'
        log.debug(f'({__my_name__}) Setting JSON file to "{DataClass.project["json"]}"')
        DataClass.project['version'], DataClass.project['git_version'] = _get_version()

    if len(_extra) > 0:
        log.debug(f'({__my_name__}) Unknown directories: {_extra}')

    _chkfiles = []
    if files is not None:
        for _file in files:
            if DataClass.start_file is None and _file.name.startswith('run_'):
                log.debug(f'({__my_name__}) Adding {_file.name} as starting file')
                DataClass.start_file = _file
                continue
            elif 'setup.py' == _file.name:
                log.debug(f'({__my_name__}) Adding setup.py for later checks')
                DataClass.setup_py = _file
                continue
            _chkfiles.append(_file)
        if _chkfiles:
            log.debug(f'({__my_name__}) Extra files: {_chkfiles}')

    PrettyLog.log(txt=DataClass, head=f'({__my_name__}) DataClass:', lvl=log.debug)
    log.debug(f'({__my_name__}) Finished project checks')


def _get_spec(module, path=None):
    """Find a module spec

    :param Path name: Name of module
    :param str path: Fully-qualified path to search
    :returns: importlib.machinery.ModuleSpec or None
    """
    if path is None:
        _chk = PathFinder.find_spec(module.name)
    else:
        _chk = PathFinder.find_spec(module.name, path)
    return None if _chk is None else _chk


def _get_source_file(path):
    """Loads the source file 'path' into memory, removing docstrings and comments"""
    __my_name__ = "_get_source_file"
    log.debug(f'{__my_name__}) Scanning file {path.name}')

    def get_docstring(fp, chk_s, chk_t):
        """Helper for docstring processing"""
        # chk_s = initial line
        # chk_t = single- or double-quote docsitring
        myline = chk_s
        _chk_t = chk_t * 3
        for chk in fp:
            chk = chk.strip()
            myline = f'{myline} {chk}'
            if _chk_t not in chk or fp.closed:
                break
        return myline

    get_src = []

    # Comments and docstrings
    with path.open() as fp:
        for line in fp:
            if not line or fp.closed:
                break
            line = line.strip()
            # Docstring check so we don't add lines that should not be part of the check
            if '""' in line:
                # Double-quote docstring
                line = get_docstring(fp, line, '"')
            elif "''" in line:
                line = get_docstring(fp, line, "'")
            if line.startswith('#'):
                continue
            # Handle inline comments
            elif '#' in line:
                line = line.split('#', 1)[0]

            get_src.append(line)
            # Make txt a list so PrettyLog processes it correctly
            PrettyLog.log(head=f'({__my_name__}) Adding line:', txt=[get_src[-1]])

    PrettyLog.log(lvl=log.debug,
                  head=f'{__my_name__}) Finished comments and docstring processing:',
                  txt=get_src,
                  single=True)

    # Check for continuation lines
    my_cont = False
    my_line = None
    for line in get_src:
        my_line = '' if my_line is None else my_line
        if line.endswith('\\'):
            if my_cont:
                log.debug(f'({__my_name__}) Appending "{line}"')
            else:
                log.debug(f'{__my_name__}) Continuation line detected:')
                log.debug(f'{line}')
            my_cont = True
            line = line.rstrip('\\').strip()
            my_line = f'{my_line}{" " if line.endswith(",") else ""}{line}'
            continue
        elif my_cont:
            my_cont = False
            my_line = None
            line = my_line
            PrettyLog.log(head=f'({__my_name__}) Adding line:', txt=[line])

        if line and (line.startswith('import ') or line.startswith('from ')):
            DataClass.imports_list.append(line)
            PrettyLog.log(head=f'({__my_name__}) Adding line to DataClass.imports_list:',
                          txt=[DataClass.imports_list[-1]])


def _get_unchecked_directories():
    """Find all entries in data.file_list that are set to None

    Helper function to find directories that have not been scanned yet.

    :return: dict
    """
    ret = {k: None for k in DataClass.file_list if DataClass.file_list[k] is None}
    PrettyLog.log(lvl=log.debug,
                  head='(_get_unchecked_directories) Returning ',
                  txt=ret)
    return ret


def _get_version(proj=None, vfile=None):
    """Get version information from Git, project/.version

    :param str proj: Project directory name
    :param str vfile: File with single-line version number format "N.N.N"

    :returns: (version, git_version)
    :rtype: tuple
    """
    __my_name__ = '_get_version'
    proj_name = DataClass.project_name if proj is None else proj
    vers_file = DataClass.project['version_file'] if vfile is None else vfile

    log.info(f'({__my_name__}) Getting version for project "{DataClass.project_name}"')
    git_version = None
    proj_version = None

    from subprocess import run
    try:
        git_version = run(['git', 'describe', '--tags'],
                          capture_output=True,
                          check=True,
                          universal_newlines=True).stdout.strip()
    except FileNotFoundError:
        # Git not available or not installed?
        pass

    try:
        vf = Path(proj_name, vers_file)
        with vf.open() as fp:
            proj_version = [v for v in fp.readlines() if v]
            proj_version = proj_version[0].strip()
            log.info(f'({__my_name__}) project version: {proj_version}')
            DataClass.project['version'] = proj_version
    except FileNotFoundError:
        # Version file not available
        if git_version is not None:
            # Try to get version from git_version
            proj_version = git_version.split('-', 1)[0]

    if proj_version is None:
        log.warning(f'({__my_name__}) Unable to get {proj_name} version')
        log.warning(f'({__my_name__}) Version file {vers_file} missing')
        log.warning(f'({__my_name__}) and/or git either unavailable or not installed')
    else:
        log.info(f'({__my_name__}) '
                 f'project version: {DataClass.project["version"]} '
                 f'git version: {DataClass.project["git_version"]}')
    return (proj_version, git_version)


def _list_dir(base, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Scan directory and returns entries.

    :param str base: Fully qualified Path()
    :return: ([directories], [files])
    :rtype: tuple
    """
    __my_name__ = '_list_dir'

    check = Path(base).resolve()
    if not check.is_dir():
        log.warning(f'({__my_name__}) "{base} not a directory - returning')
        return (None, None)

    log.info(f'({__my_name__}) Starting directory scan in {base}')
    dirs = []
    files = []

    for chk in check.iterdir():
        # log.debug(f'({__my_name__}) Checking {_check}')
        if chk.is_file() \
                and chk.suffix in i_ext \
                and chk.name not in e_file \
                and not chk.name.startswith('.'):
            log.debug(f'({__my_name__}) Adding {chk.name} to files')
            files.append(chk.relative_to(DataClass.base_dir))

        elif chk.is_dir() \
                and chk.name not in e_dir \
                and not chk.name.startswith('.'):
            log.debug(f'({__my_name__}) Adding {chk.name} to directories')
            dirs.append(chk.relative_to(DataClass.base_dir))

    dirs = dirs if dirs else None
    files = files if files else None
    PrettyLog.log(lvl=log.debug, head=f'({__my_name__}) dirs  : ', txt=dirs)
    PrettyLog.log(lvl=log.debug, head=f'({__my_name__}) files : ', txt=files)
    return (dirs, files)


# #####################################################################################
# #####################################################################################
# #####################################################################################
# #####################################################################################


def check_deps(base=DataClass.base_dir, full=False, testdir=None, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):  # noqa since kdevelop doesn't fold multi-line def statements
    """Entry point for dependency checks. Initializes required options.

    :param Path base: Base directory of project (default Path('.'))
    :param bool full: Force full dependency check (default False)
    :param bool testdir: Check test directory files
    :param list e_dir: Directory names to exclude
    :param list e_file: File names to exclude
    :param list i_ext: File name extensions to include (default ['.py']
    """
    __my_name__ = 'check_deps'
    log.info(f'({__my_name__}) Starting run')

    # Initialize DataClass with important first-time data, like project name
    if DataClass.project['dir'] is None:
        _get_project()
        if DataClass.project['dir'] is None:
            # In case _get_project could not find source
            log.error(f'({__my_name__}) Project directory not set - exiting')
            return

    # Either retrieve previously-saved state or initialize a new state
    log.info(f'({__my_name__}) Getting dependency list in'
             f'{DataClass.base_dir.joinpath(DataClass.project["json"])}')
    json_file(DataClass.project['json'])

    if full \
            or DataClass.dep_list is None \
            or len(DataClass.dep_list) <= len(DataClass.dep_list_default):

        # len(DataClass.dep_list) <= len(DataClass.dep_list_default indicates
        # a new dep_list
        #   - No dependency list found
        #   - Error with JSON file
        #
        # In these cases, a new dependency list is created
        log.info(f'({__my_name__}) Scanning all project source files')

        if not DataClass.dep_list:
            DataClass.dep_list = copy(DataClass.dep_list_default)
        PrettyLog.log(txt=DataClass.dep_list, head=f'({__my_name__}) DataClass.dep_list')

        # Process directories
        if DataClass.file_list is None:
            log.debug(f'({__my_name__}) Starting new file search')
            # Initialize the list with the project name so we have a
            # starting point for _get_unchecked_directories() to work with
            DataClass.file_list = {DataClass.project_name: None}
        else:
            log.debug(f'({__my_name__}) Updating file list')

        # ===============

        json_file(DataClass.project['json'], DataClass.project)
        return

        # ===============

        dir_list = _get_unchecked_directories()
        while dir_list:
            for key in dir_list:
                # Scan directories to find source files
                _get_directory(key)
            # Reset dir_list
            dir_list = _get_unchecked_directories()

        dir_list = [k for k in DataClass.file_list]
        PrettyLog.log(lvl=log.debug, head=f'({__my_name__} Scanning directories: ',
                      txt=dir_list)

        while dir_list:
            my_dir = dir_list.pop()
            PrettyLog.log(lvl=log.debug, head=f'({__my_name__} Scanning files: ',
                          txt=my_dir)
            # We have the directories, now go through the files
            if DataClass.file_list[my_dir] == No_Files_Marker:
                # No source files to scan in this directory
                continue
            PrettyLog.log(lvl=log.debug,
                          head=f'({__my_name__}) Checking ',
                          txt=DataClass.file_list[my_dir])

            for _file in DataClass.file_list[my_dir]:
                _get_source_file(DataClass.base_dir.joinpath(my_dir, _file))

            # Finished processing directory files,, so remove it from the global list
            DataClass.file_list.pop(my_dir)

    PrettyLog.log(lvl=log.debug,
                  head=f'({__my_name__}) Dependency list: ',
                  txt=DataClass.imports_list,
                  single=True)
    log.debug(f'({__my_name__}) Finished dependency list')

    # Done/skipped finding deps, now to check them

    log.debug(f'({__my_name__}) Starting dependency checks')

    log.debug(f'({__my_name__}) Flushing module caches')
    PathFinder.invalidate_caches()

    while DataClass.imports_list:
        # for dep in DataClass.imports_list:
        dep = DataClass.imports_list.pop(0)
        log.debug(f'({__my_name__}) Calling dep checks with "{dep}"')
        _check_dependencies(dep)

    # Save the results
    DataClass.dep_list['dep_check'] = DataClass.dep_check
    json_file(DataClass.base_dir.joinpath(DataClass.project['json']), DataClass.dep_list)
    return


def json_file(name=None, datalist=None):
    """Save/Read project JSON file

    If json_file exists, populate from previously saved list.

    :param str name: Project directory name
    :param list datalist: Data to save, otherwise get data
    """
    __my_name__ = 'json_file'

    def dump_json(o):
        if issubclass(o.__class__, Path):
            return {'Path': str(o)}

        elif issubclass(o.__class__, ModuleSpec):
            chk = []
            for itm in o.submodule_search_locations:
                if DataClass.project_name in itm:
                    str(chk.append(Path(itm).resolve().relative_to(DataClass.project['dir'])))

            return {'ModuleSpec': {'name': o.name,
                                   'origin': o.origin,
                                   'submodule_search_locations': chk}
                    }

    def save_json():
        # Load JSON or start a new dict
        if name is None and DataClass.project['json'] is None:
            # No previous file specified - so use default name
            DataClass.project['json'] = 'project-deps.json'
            log.warning(f'({__my_name__}) Unknown project save file - using default'
                        f'{DataClass.project["json"]}')

        # Try to load previous state
        log.info(f'({__my_name__}) Checking for previous JSON list')
        src = Path(DataClass.project['json'])

        ret = None
        if src.exists():
            log.info(f'({__my_name__}) Parsing {src}')
            try:
                with src.open('r') as fp:
                    ret = json.load(fp)
                    PrettyLog.log(txt=ret, lvl=log.debug, head=f'({__my_name__})')
                    log.info(f'({__my_name__}) Loaded JSON file')
            except json.JSONDecodeError:
                log.warning(f'({__my_name__}) Source {src} appears to be corrupted')
                ret = None
        else:
            log.info(f'({__my_name__}) Source {src} does not exists')

        if ret is None:
            log.info(f'({__my_name__}) Creating new dependency list')

        DataClass.dep_list = ret
        return ret is not None

    def load_json():
        # Save JSON data
        if type(datalist) is not dict:
            log.warning(f'({__my_name__}) Cannot save data - wrong type (not dict)')
            return False

        log.info(f'({__my_name__}) Saving data to {name}')
        DataClass.dep_list['dep_check'] = copy(DataClass.dep_check)

        '''
        log.debug(f'({__my_name__}) Removing ModuleSpec items')

        _chk_dep = copy(DataClass.dep_check)
        for k in _chk_dep:
            log.debug(f'({__my_name__}) Checking {k}')
            if 'modulespec' in _chk_dep[k]:
                log.debug(f'({__my_name__}) Deleting entry {_chk_dep[k]["modulespec"]}')
                del _chk_dep[k]['modulespec']
        DataClass.dep_list['dep_check'] = _chk_dep
        '''

        try:
            with open(name, 'w') as fp:
                # Skipkeys=True should only skip the ModSpec key
                # since importlib.machinery.ModuleSpec is non-serializable at this time
                json.dump(datalist, fp, indent=4, skipkeys=True, default=dump_json)

        except Exception as err:
            log.warning(f'({__my_name__}) Error saving data: ({err=}')
            return False
        log.info(f'({__my_name__}) Data saved to {name}')
        del DataClass.dep_list['dep_check']
        return True

    if datalist is None:
        return save_json()
    else:
        return load_json()

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
    parser.add_argument('-l', '--log', help='Log save file')
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

    if args.start is not None and args.start.endswith('.py'):
        DataClass.start_py = args.start
    DataClass.project['json'] = args.save

    check_deps(full=args.full, testdir=args.test)
    PrettyLog.log(lvl=log.debug, head='(__main__) DataClass:', txt=DataClass)
    # PrettyLog.log(lvl=log.debug, head='DataDir PrettyLog:', txt=PrettyLog)
