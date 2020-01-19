# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

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
The :mod:`db` module provides the database and schema that is the backend for
the Custom plugin
"""
from sqlalchemy import Column, Table, types
from sqlalchemy.orm import mapper

from openlp.core.lib.db import BaseModel, init_db


class RemoteSyncItem(BaseModel):
    """
    RemosteSync model
    """
    pass


class SyncQueueItem(BaseModel):
    """
    SyncQueue model
    """
    pass


class ConflictItem(BaseModel):
    """
    Conflict model
    """
    pass


def init_schema(url):
    """
    Setup the custom database connection and initialise the database schema

    :param url:  The database to setup
    """
    session, metadata = init_db(url)

    remote_sync_table = Table('remote_sync_map', metadata,
                              Column('item_id', types.Integer(), primary_key=True),
                              Column('type', types.Unicode(64), primary_key=True),
                              Column('uuid', types.Unicode(36), nullable=False),
                              Column('version', types.Unicode(64), nullable=False),
                              )

    sync_queue_table = Table('sync_queue_table', metadata,
                             Column('item_id', types.Integer(), primary_key=True, nullable=False),
                             Column('type', types.Unicode(64), primary_key=True, nullable=False),
                             Column('action', types.Unicode(32)),
                             Column('lock_id', types.Unicode(128)),
                             Column('first_attempt', types.DateTime()),
                             )

    conflicts_table = Table('conflicts_table', metadata,
                            Column('type', types.Unicode(64), primary_key=True, nullable=False),
                            Column('uuid', types.Unicode(36), nullable=False),
                            Column('conflict_reason', types.Unicode(64), nullable=False),
                            )

    mapper(RemoteSyncItem, remote_sync_table)
    mapper(SyncQueueItem, sync_queue_table)
    mapper(ConflictItem, conflicts_table)

    metadata.create_all(checkfirst=True)
    return session
