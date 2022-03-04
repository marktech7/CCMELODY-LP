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
"""
Fixtures for projector tests
"""
import os
import pytest

from unittest.mock import patch

from openlp.core.projectors.db import Projector, ProjectorDB
from openlp.core.projectors.manager import ProjectorManager
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST_DB, TEST1_DATA

'''
NOTE: Since Registry is a singleton, sleight of hand allows us to verify
      calls to Registry.methods()

@patch(path.to.imported.Registry)
def test_function(mock_registry):
    mocked_registry = MagicMock()
    mock_registry.return_value = mocked_registry
    ...
    assert mocked_registry.method.has_call(...)
'''


@pytest.fixture()
def projector_manager(settings):
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = 'sqlite:///%s' % TEST_DB
        projectordb = ProjectorDB()
        proj_manager = ProjectorManager(projectordb=projectordb)
        yield proj_manager
        projectordb.session.close()
        del proj_manager


@pytest.fixture()
def projector_manager_nodb(settings):
    proj_manager = ProjectorManager(projectordb=None)
    yield proj_manager
    del proj_manager


@pytest.fixture()
def projector_manager_mtdb(settings):
    with patch('openlp.core.projectors.db.init_url') as mock_url:
        mock_url.return_value = 'sqlite:///%s' % TEST_DB
        t_db = ProjectorDB()
        # Ensure we have an empty DB at the beginning of the test
        for itm in t_db.get_projector_all():
            t_db.delete_projector(itm)
        t_db.session.commit()

        t_manager = ProjectorManager(projectordb=t_db)
        yield t_manager
        t_db.session.close()
        del t_db
        del t_manager


@pytest.fixture()
def projectordb(temp_folder, settings):
    """
    Set up anything necessary for all tests
    """
    tmpdb_url = 'sqlite:///{db}'.format(db=os.path.join(temp_folder, TEST_DB))
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = tmpdb_url
        proj = ProjectorDB()
    yield proj
    proj.session.close()
    del proj


@pytest.fixture()
def pjlink():
    pj_link = PJLink(Projector(**TEST1_DATA), no_poll=True)
    yield pj_link
    del pj_link
