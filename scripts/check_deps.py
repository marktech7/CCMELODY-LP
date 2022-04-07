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

This script does NOT install missing dependencies. Modules listed
as dependencies may be updated in the resulting json file to
include the package that the module may be located as well as
the repository where the package may be found (ex. PyPI or a fedora repo).

After building a dependency list, project managers can then
assign "required | optional | dev | ..." status to the dependencies.

project.json format:

{
    "project"        : Project name (ex. "openlp")
    "name"           : Proper project name (ex. "OpenLP")
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
                       Note: "parent" points to another module entry

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
else:
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


class DataClass(metaclass=Singleton):
    """Class to hold module data"""
    @classmethod
    def create(self):
        # All directories in here are relative to base_dir
        self.base_dir = Path('.').resolve()  # Project base directory (current directory)
        self.dep_list = None  # (dict() of JSON file contents
        # All files in file_list will be relative to the directory they're found in
        # file_list.keys() are directories relative to base_dir
        self.file_list = None  # Keep track of files to check
        self.git_version = None  # Git version
        self.imports_list = []  # List of lines to check for imports
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
        #
        # Following variables are used by the local functions
        self._format_level = 0
        self._format_space = {0: ''}

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

    def __iter__(self):
        """Make class iterable"""
        for i in dict([('base_dir', self.base_dir),
                       ('dep_list', self.dep_list),
                       ('file_list', self.file_list),
                       ('git_version', self.git_version),
                       ('helpers', self.helpers),
                       ('proj_dir', self.proj_dir),
                       ('project', self.project),
                       ('project_name', self.project_name),
                       ('save_file', self.save_file),
                       ('setup', self.setup),
                       ('setup_py', self.setup_py),
                       ('start_py', self.start_py),
                       ('test_dir', self.test_dir),
                       ('version', self.version),
                       ('version_file', self.version_file),
                       ('imports_list', self.imports_list)
                       ]):
            yield i


class PrettyLog(metaclass=Singleton):
    """Pretty-printing log method for objects.

    Hopefully it's thread-safe as well.
    """
    def __iter__(self):
        """Make it an iterable"""
        for k in dict([('width', self.width),
                       ('indent', self.indent),
                       ('indent_str', self.indent_str),
                       ('indents', self.indents),
                       ('log_items', self.log_items)
                       ]):
            yield k

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
        # Check if we don't have to process further
        if isinstance(txt, (Singleton)):
            log.warning('To log Singleton class, provide instance (i.e. PrettyLog())')
            log.warning(f'Log called with {txt}')
            return
        elif not isinstance(txt, (DataClass, PrettyLog)):
            # Check for my two classes so I can actually show
            # what they have.
            # If this script added to a different project, you
            # may have to adapt the isinstance() to your project.
            if self.log_line(self, lvl=lvl, txt=f'{prefix}{txt}'):
                return

        # Item too big to log on a single line, time to process
        self.log_items.append({'lvl': lvl, 'head': head, 'txt': txt})
        if type(txt) is list:
            self.log_list(self)
        elif type(txt) is dict:
            self.log_dict(self)
        else:
            self.log_obj(self)

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
        self.pop_item(self.log_items)

    def log_list(self):
        """Format a list object for logging"""
        item = self.log_items[-1]
        lvl = item['lvl']
        head = item['head']
        self.log_line(self, lvl=lvl, txt=head)
        self.set_indent(self)
        self.format_line(self)
        self.set_indent(self, decr=True)
        self.pop_item(self.log_items)

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

        chk = dict()
        for k in text:
            # Build dict from attributes
            chk[k] = getattr(text, k)
        for k in chk:
            itm = chk[k]
            self.log(lvl=lvl, head=f'{k}: ', txt=itm)

        self.set_indent(self, decr=True)
        self.log_line(self, lvl=lvl, txt=('}'))
        self.pop_item(self.log_items)

    @classmethod
    def pop_item(self, lst):
        """Pops the last item from a list"""
        if type(lst) is not list:
            log.warning('(PrettyLog:pop_item) Not a list - returning')
            return
        try:
            lst.pop(-1)
        except IndexError:
            log.warning('(PrettyLog:pop_item) Trying to pop an empty list')

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
    line = check.strip()
    if line and not line.startswith('#'):
        return line

    # Already checked current line, continue with following lines
    for line in fp:
        if not line or fp.closed:
            # Empty line or end of file
            return ''
        line = line.strip()
        if line and not line.startswith('#'):
            # Found a non-comment line
            break
    return line


def _check_continues(fp, check):
    """Check for multi-line command and condense it

    :param obj fp: Open file object
    :param str check: Initial string to check
    :return: Full line
    :rtype: str
    """
    line = check.strip()
    if not line.endswith('\\'):
        return line

    line = line.rstrip('\\').strip()
    for _l in fp:
        if not _l or fp.closed:
            return line
        _l = _l.strip()
        line = ' '.join([line, _l])

        if not line.endswith('\\'):
            break
        line = line.rstrip('\\').strip()

    return line


def _check_docstrings(fp, check, skip=True):
    """Check for docstring and skip if found

    :param obj fp: File object to scan
    :param str check: Initial tring to check
    :param bool skip: If False, return docstring as a single string
    :return: str
    """
    line = check.strip()
    if "'" * 3 in line:
        # Get around possible issues with using triplets string and parsing this file
        chk = "'" * 3
    elif '"' * 3 in line:
        # Get around possible issues with using triplets string and parsing this file
        chk = '"' * 3
    else:
        # No initial docstring marker found
        return line

    _c = line.split(chk)
    if len(_c) == 3 and not f'{_c[0]}{_c[-1]}':
        # Single-line docstring
        if skip:
            return ''
        return line

    for _l in fp:
        if not _l or fp.closed:
            # Empty line or end of file
            break
        _l = _l.strip()
        line = ' '.join([line, _l])
        if chk in _l:
            # Found closing docstring marker
            break

    return line if not skip else ''


def _get_deps(src):
    """Process file and find dependencies in file

    :param Path src: Source file
    """
    __my_name__ = '_get_deps'
    log.info(f'({__my_name__}) Starting import scan on {src.relative_to(DataClass.base_dir)}')
    with src.open() as fp:
        for line in fp:
            if fp.closed:
                break
            line = _get_next_line(fp, line)
            if line.startswith('import ') or line.startswith('from '):
                if line in DataClass.imports_list:
                    log.debug(f'({__my_name__}) Duplicate dependency "{line}" - skipping')
                else:
                    log.debug(f'({__my_name__}) Adding "{line}"')
                    DataClass.imports_list.append(line)
    log.info(f'({__my_name__}) Finished import scan')


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

        ret = {'project': DataClass.project,
               'name': DataClass.project_name,
               'version': DataClass.version,
               'git_version': DataClass.git_version
               }
    DataClass.dep_list = ret
    return


def _get_next_line(fp, check, skip=True):
    """Helper to find next line that's not a comment or a docstring

    :param obj fp: File object
    :param str check: Initial string to check
    :return: str
    """
    check = _check_comments(fp, check)
    if check:
        check = _check_continues(fp, check)
        if check:
            return _check_docstrings(fp, check, skip=skip)

    return ''


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
                _get_deps(DataClass.base_dir.joinpath(my_dir, _file))

    log.debug(f'({__my_name__}) Finished dependency list')
    '''
    PrettyLog.log(lvl=log.debug,
                  head=f'({__my_name__}) Dependency list: ',
                  txt=DataClass.imports_list)
    '''

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
        DataClass.start_py = args.start

    check_deps(full=args.full, testdir=args.test, jfile=args.save)
    # PrettyLog.log(lvl=log.debug, head='DataDir : DataClass: ', txt=DataClass)
    PrettyLog.log(lvl=log.debug, head='DataDir : PrettyLog: ', txt=PrettyLog())
