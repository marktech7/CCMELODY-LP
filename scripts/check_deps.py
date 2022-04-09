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
        "deplist"        : { module : { "status"  : string,
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
import importlib
import json
import logging
import os
import re
import sys

from copy import copy
from importlib.machinery import PathFinder, ModuleSpec
from pathlib import Path

__all__ = ['check_deps']

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
                  'file_list',
                  'git_version',
                  'helpers',
                  'proj_dir',
                  'project',
                  'project_name',
                  'save_file',
                  'setup',
                  'setup_py',
                  'start_py',
                  'test_dir',
                  'version',
                  'version_file',
                  # Show last since they may be big
                  'imports_list',
                  'dep_list',
                  'dep_check'
                  ]

    def __repr__(self):
        return f'<DataClass: ' \
            f'base_dir={self.base_dir},' \
            f' dep_list={self.dep_list},' \
            f' dep_check={self.dep_check}', \
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
            f' imports_list={self.imports_list}' \
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
            f' version_file={self.version_file}' \
            f' imports_list={self.imports_list}'

    @classmethod
    def create(self):
        # All directories in here are relative to base_dir
        self.base_dir = Path('.').resolve()  # Project base directory (current directory)
        self.dep_list = None  # (dict() of JSON file contents
        self.dep_check = {}  # Intermediate dictionary of found dependencies
        # All files in file_list will be relative to the directory they're found in
        # file_list.keys() are directories relative to base_dir
        self.file_list = None  # Keep track of files to check
        self.git_version = None  # Git version
        self.imports_list = []  # List of lines to check for imports
        self.helpers = []  # Director(ies) that contain helper scripts
        # proj_dir will be relative to base_dir
        self.proj_dir = None  # Subdirectory of base_dir where source files are located
        self.project = 'openlp'  # Project name - should be the same as the directory name
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
        #
        # Following variables are used by the local functions
        self._format_level = 0
        self._format_space = {0: ''}
        #
        # Set some defaults
        self.default_dep = {'project': self.project,
                            'name': self.project_name,
                            'version': self.version,
                            'git_version': self.git_version
                            }
        self.default_deplist = {'python': {'version': '>= 5.6',
                                           'status': 'required'},
                                'PyQt5': {'version': '>= 5.12',
                                          'status': 'required'},
                                'Qt5': {'version': '>= 5.9',
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
    def log(self, txt, lvl=None, head=None, fromlist=False):
        """
        :param txt: Text to log
        :type txt: object
        :param func lvl: Logging function (logging.debug, logging.info, ...)
        :param str head: Text prefix
        """
        prefix = head if head is not None else ''
        self.log_items.append({'lvl': lvl, 'head': head, 'txt': txt})
        # Check if we don't have to process further

        # If this script added to a different project, you
        # may have to adapt the isinstance() to your project.
        if not isinstance(txt, (Singleton)):
            if self.log_line(self, lvl=lvl, txt=f'{prefix}{txt}'):
                self.pop_item(self.log_items)
                return

        # Too long to log onto a single line. Separate processing.
        if type(txt) is list:
            self.log_list(self)
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

    def log_list(self):
        """Format a list object for logging"""
        item = self.log_items[-1]
        lvl = item['lvl']
        head = item['head']
        self.log_line(self, lvl=lvl, txt=head)
        self.set_indent(self)
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


def _get_directory(base, recurse=True, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Process the project directory and add source files to DataClass.file_list

    Since we may have recursion issues, indicate the directory has not been
    scanned by setting entry to None instead of an empty list.

    :param Path base: Initial directory to process relative to DataClass.base_dir
    :param bool recurse: Process subdirectories
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


def _get_json_file(src):
    """Initialize DataClass.dep_list

    If json_file exists, populate from previously saved list.
    DataClass.base_dir must already be checked before calling this function.

    :param Path src: Fully qualified file path/name
    """
    __my_name__ = '_get_json_file'
    log.info(f'({__my_name__}) Checking for previous {src.relative_to(DataClass.base_dir)} dependency list')

    ret = None
    _src = DataClass.base_dir.joinpath(src)

    if _src.exists():
        log.info(f'({__my_name__}) Parsing {src}')
        try:
            with open(_src, 'r') as fp:
                ret = json.load(fp)
                PrettyLog.log(txt=ret, lvl=log.debug, head=f'({__my_name__})')
                log.info(f'({__my_name__}) Loaded JSON file')

        except json.JSONDecodeError:
            log.warning(f'({__my_name__}) {src} appears to be corrupted')
            ret = None
    else:
        log.info(f'({__my_name__}) Source {src} does not exists')

    if ret is None:
        log.info(f'({__my_name__}) Creating new dependency list')
        if DataClass.version is None:
            DataClass.version, DataClass.git_version = _get_version()

        ret = DataClass.default_dep

    if 'dep_check' in ret:
        DataClass.dep_check = ret['dep_check']
        del ret['dep_check']
    DataClass.dep_list = ret
    return


def _get_project_dir(proj=DataClass.project):
    """Finds the project directory

    Sets DataClass.proj_dir to (DataClass.base_dir)/dir.

    :param str proj: Name of project
    :return: None
    """
    __my_name__ = '_get_project_dir'
    if DataClass.base_dir is None:
        dirs, files = _list_dir('.')
    else:
        dirs, files = _list_dir(DataClass.base_dir)

    if dirs is None:
        log.error(f'({__my_name__}) Unable to determine starting point - exiting')
        return

    log.info(f'({__my_name__}) Starting base checks')
    if dirs is not None:
        proj_chk = []
        for checkdir in dirs:
            log.debug(f'({__my_name__}) Checking {checkdir}')
            if checkdir.name == 'src':
                # Possible PyPI project
                if DataClass.base_dir.joinpath(checkdir).exists():
                    proj_chk.append(checkdir)
                    continue
            elif DataClass.project is not None and checkdir.name == DataClass.project:
                log.debug(f'({__my_name__}) Adding "{checkdir.name}"')
                proj_chk.append(checkdir)
                continue
            elif checkdir.name.startswith('test'):
                log.debug(f'({__my_name__}) Setting DataClass.test_dir to "{checkdir.name}"')
                DataClass.test_dir = checkdir
                continue
            elif checkdir.name.startswith('script'):
                log.debug(f'({__my_name__}) Adding "{checkdir.name}" to helpers list')
                DataClass.helpers.append(checkdir)
                continue
            # Check for module spec
            chk = '.'.join([c for c in DataClass.base_dir.joinpath(checkdir).parts])
            chk = PathFinder.find_spec(chk)
            if not chk:
                continue
            elif chk.origin is None:
                # Did not find spec - not a package
                continue
            elif 'site-package' in chk.origin:
                # We're looking for source, not dpes here
                continue

            chk = Path(chk.origin).parts
            if 'test' in chk[-2]:
                DataClass.test_dir = checkdir.relative_to(DataClass.base_dir)
                continue
            elif 'script' in chk[-2]:
                # Helper scripts
                DataClass.helpers = checkdir.relative_to(DataClass.base_dir)
                continue

            # Unknown directory - recheck later
            proj_chk.append(checkdir.relative_to(DataClass.base_dir))

        if len(proj_chk) == 1:
            # Hopefully found our package
            DataClass.project = proj_chk[0].name
            DataClass.proj_dir = proj_chk[0]
            proj_chk.pop(0)

    log.debug(f'({__my_name__}) Finished processing directories')
    log.debug(f'({__my_name__}) Leftover list: {proj_chk}')

    proj_chk = []
    if files is not None:
        for _file in files:
            if DataClass.start_py is None and _file.name.startswith('run_'):
                DataClass.start_py = _file.name
                continue
            elif 'setup.py' == _file.name:
                DataClass.setup_py = _file.name
                continue
            proj_chk.append(_file)
    if proj_chk:
        PrettyLog(lvl=log.info,
                  head=f'({__my_name__}) Extra files found:',
                  txt=proj_chk)


def _get_spec(name):
    """Find a module spec

    :param str name: Name of module
    :returns: importlib.machinery.ModuleSpec or None
    """
    _chk = PathFinder.find_spec(name)
    if not _chk:
        return None
    return _chk


def _get_source_file(path):
    """Loads the source file 'path' into memory, removing docstrings and comments"""
    __my_name__ = "_get_source_file"
    log.debug(f'{__my_name__}) Scanning file {path.name}')

    def strip_docstring(fp, check):
        for chk in fp:
            if chk.startswith(check) or chk.endswith(check):
                break
        if fp.closed:
            return None
        return fp.readline()

    src = []
    with path.open() as fp:
        for line in fp:
            line = line.strip()
            check = None
            check = '"' * 3 if '""' in line else check
            if check is None:
                check = "'" * 3 if "''" in line else check
            if check is not None:
                line = strip_docstring(fp, check)

            if line is not None:
                src.append(line)

    # Check for continuation lines
    chk = ['']
    cont = False
    for line in src:
        line = line.strip()
        if line.endswith('\\'):
            chk[-1] = ' '.join([chk[-1], line.rstrip('\\')[0]])
            cont = True
            continue
        if cont:
            chk[-1] = ' '.join([chk[-1], line])
            cont = False
            continue
        chk.append(line)
    src = chk

    # Comments
    chk = []
    for line in src:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        elif '#' in line:
            line = line.split('#', 1)[0]

        if line.startswith('import ') or line.startswith('from '):
            if line in DataClass.imports_list:
                log.debug(f'({__my_name__}) Duplicate import - skipping')
                continue
            chk.append(line)
    src = chk

    # Finally, add to the import checker list
    DataClass.imports_list.extend(src)


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


def _get_version(proj=DataClass.project, vfile=DataClass.version_file):
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
        # Git not available or not installed?
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
        log.warning(f'({__my_name__}) Version file {proj}/{vfile} missing')
        log.warning(f'({__my_name__}) Git either unavailable or not installed')
    else:
        log.info(f'({__my_name__}) Project version: {proj_version} Git version: {git_version}')

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


def _save_json_file(src, deps):
    """Save dependency list to file.

    :param Path src: Fully-qualified /path/to/file to save to
    :param dict deps: Dependency dictionary
    :return: bool
    """
    __my_name__ = '_save_json_file'

    if type(deps) is not dict:
        log.warning(f'({__my_name__}) Cannot save data - wrong type (not dict)')
        return False

    log.info(f'({__my_name__}) Saving data to {src}')
    log.debug(f'({__my_name__}) Removing ModuleSpec items')

    chk = copy(DataClass.dep_check)
    for k in chk:
        log.debug(f'({__my_name__}) Checking {k}')
        if 'modulespec' in chk[k]:
            log.debug(f'({__my_name__}) Deleting entry {[k]}["modulespec"] from save list')
            del chk[k]['modulespec']

    DataClass.dep_list['dep_check'] = chk
    try:
        with open(src, 'w') as fp:
            # Skipkeys=True should only skip the ModSpec key
            # since importlib.machinery.ModuleSpec is non-serializable at this time
            json.dump(deps, fp, indent=4, skipkeys=True)

    except Exception as err:
        log.warning(f'({__my_name__}) Error saving data: ({err=}')
        return False
    log.info(f'({__my_name__}) Data saved to {src}')
    if 'dep_check' in DataClass.dep_list:
        del DataClass.dep_list['dep_check']
    return True


# #####################################################################################
# #####################################################################################
# #####################################################################################
# #####################################################################################


def check_deps(base=DataClass.base_dir, full=False, jfile=None,
               testdir=None, e_dir=ExclDir, e_file=ExclFile, i_ext=InclExt):
    """Entry point for dependency checks. Initializes required options.

    :param Path base: Base directory of project (default Path('.'))
    :param bool full: Force full dependency check (default False)
    :param str jfile: Name of JSON file (default [project]-deps.json)
    :param bool testdir: Check test directory files
    :param list e_dir: Directory names to exclude
    :param list e_file: File names to exclude
    :param list i_ext: File name extensions to include (default ['.py']
    """
    __my_name__ = 'check_deps'
    log.info(f'({__my_name__}) Starting dependency checks')

    if DataClass.proj_dir is None:
        _get_project_dir()
    if DataClass.proj_dir is None:
        log.error(f'({__my_name__}) Project directory not set - exiting')
        return
    if jfile is not None:
        DataClass.save_file = jfile
    elif DataClass.project is not None:
        DataClass.save_file = f'{DataClass.project}-deps.json'
    else:
        log.warning(f'({__my_name__}) Save file not specified - using "project-deps.json"')
        DataClass.save_file = 'project-deps.json'
    log.info(f'({__my_name__}) Saving dependency list in {DataClass.base_dir.joinpath(DataClass.save_file)}')
    _get_json_file(DataClass.base_dir.joinpath(DataClass.save_file))

    if full or DataClass.dep_list is None or len(DataClass.dep_list) <= 4:
        # len(DataClass.dep_list) <= 4 indicates
        #   - No dependency list found
        #   - Error with previous file
        #
        # In these cases, a new dependency list is created
        log.info(f'({__my_name__}) Scanning all project source files')

        if not DataClass.dep_list:
            # Try to load previous dependency list
            _get_json_file(DataClass.base_dir.joinpath(DataClass.save_file))

        # Process directories
        if DataClass.file_list is None:
            log.debug(f'({__my_name__}) Starting new file search')
            DataClass.file_list = {DataClass.proj_dir: None}
        else:
            log.debug(f'({__my_name__}) Updating file list')

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
                  txt=DataClass.imports_list)
    log.debug(f'({__my_name__}) Finished dependency list')

    # Done/skipped finding deps, now to check them

    log.debug(f'({__my_name__}) Starting dependency checks')

    log.debug(f'({__my_name__}) Flushing module caches')
    importlib.invalidate_caches()

    while DataClass.imports_list:
        # for dep in DataClass.imports_list:
        dep = DataClass.imports_list.pop(0)
        log.debug(f'({__my_name__}) Calling dep checks with "{dep}"')
        _check_dependencies(dep)

    # Save the results
    DataClass.dep_list['dep_check'] = DataClass.dep_check
    _save_json_file(DataClass.base_dir.joinpath(DataClass.save_file), DataClass.dep_list)
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
    parser.add_argument('-l', '--log', help='Log save file')
    parser.add_argument('-v', help='Increase debuging level for each -v', action='count', default=0)
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(filename=args.log, format='%(levelname)-10s :  %(message)s')
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

    check_deps(full=args.full, testdir=args.test, jfile=args.save)
    PrettyLog.log(lvl=log.debug, head='DataDir DataClass:', txt=DataClass)
    # PrettyLog.log(lvl=log.debug, head='DataDir PrettyLog:', txt=PrettyLog)
