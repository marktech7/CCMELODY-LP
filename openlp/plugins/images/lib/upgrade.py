# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
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
The :mod:`upgrade` module provides the migration path for the OLP Paths database
"""
import json
import logging
from pathlib import Path

from sqlalchemy import Column, Table, types

from openlp.core.common import sha256_file_hash
from openlp.core.common.applocation import AppLocation
from openlp.core.common.db import drop_columns
from openlp.core.common.json import OpenLPJSONEncoder, OpenLPJSONDecoder
from openlp.core.lib.db import PathType, get_upgrade_op


log = logging.getLogger(__name__)
__version__ = 3


def upgrade_1(session, metadata):
    """
    Version 1 upgrade - old db might/might not be versioned.
    """
    log.debug('Skipping upgrade_1 of files DB - not used')


def upgrade_2(session, metadata):
    """
    Version 2 upgrade - Move file path from old db to JSON encoded path to new db. Added during 2.5 dev
    """
    log.debug('Starting upgrade_2 for file_path to JSON')
    old_table = Table('image_filenames', metadata, autoload=True)
    if 'file_path' not in [col.name for col in old_table.c.values()]:
        op = get_upgrade_op(session)
        op.add_column('image_filenames', Column('file_path', PathType()))
        conn = op.get_bind()
        results = conn.execute('SELECT * FROM image_filenames')
        data_path = AppLocation.get_data_path()
        for row in results.fetchall():
            file_path_json = json.dumps(Path(row.filename), cls=OpenLPJSONEncoder, base_path=data_path)
            sql = 'UPDATE image_filenames SET file_path = \'{file_path_json}\' WHERE id = {id}'.format(
                file_path_json=file_path_json, id=row.id)
            conn.execute(sql)
        # Drop old columns
        if metadata.bind.url.get_dialect().name == 'sqlite':
            drop_columns(op, 'image_filenames', ['filename', ])
        else:
            op.drop_constraint('image_filenames', 'foreignkey')
            op.drop_column('image_filenames', 'filenames')


def upgrade_3(session, metadata):
    """
    Version 3 upgrade - add sha256 hash
    """
    log.debug('Starting upgrade_3 for adding sha256 hashes')
    old_table = Table('image_filenames', metadata, autoload=True)
    if 'file_hash' not in [col.name for col in old_table.c.values()]:
        op = get_upgrade_op(session)
        op.add_column('image_filenames', Column('file_hash', types.Unicode(128)))
        conn = op.get_bind()
        results = conn.execute('SELECT * FROM image_filenames')
        for row in results.fetchall():
            file_path = json.loads(row.file_path, cls=OpenLPJSONDecoder)
            hash = sha256_file_hash(file_path)
            sql = 'UPDATE image_filenames SET file_hash = \'{hash}\' WHERE id = {id}'.format(hash=hash, id=row.id)
            conn.execute(sql)
