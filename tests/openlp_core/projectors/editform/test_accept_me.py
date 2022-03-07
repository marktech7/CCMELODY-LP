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
Test ProjectorEditForm.accept_me
"""
import logging
import pytest

import openlp.core.projectors.db
import openlp.core.projectors.editform

from openlp.core.projectors.constants import PJLINK_PORT, PJLINK_VALID_PORTS
from openlp.core.projectors.db import Projector
from tests.resources.projector.data import TEST1_DATA

_test_module = openlp.core.projectors.editform.__name__
_test_module_db = openlp.core.projectors.db.__name__
Message = openlp.core.projectors.editform.Message


def test_name_NAME_BLANK(projector_editform_mtdb, caplog):
    """
    Test when name field blank
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received')]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText('')

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.NAME_BLANK.title,
                                                                         Message.NAME_BLANK.text)


def test_name_DATABASE_ERROR_id(projector_editform_mtdb, caplog):
    """
    Test with mismatch ID between Projector() and DB
    """
    # GIVEN: Test setup
    t_id = TEST1_DATA['id']
    t_name = TEST1_DATA['name']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module, logging.WARNING,
             f'editform(): No record found but projector had id={t_id}')]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.projector.id = t_id

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.DATABASE_ERROR.title,
                                                                         Message.DATABASE_ERROR.text)


def test_name_DATABASE_ERROR_name(projector_editform_mtdb, caplog):
    """
    Test with mismatch between name and DB
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module, logging.WARNING,
             f'editform(): No record found when there should be name="{t_name}"')]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.projector.name = t_name
    projector_editform_mtdb.new_projector = False

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.DATABASE_ERROR.title,
                                                                         Message.DATABASE_ERROR.text)


def test_name_NAME_DUPLICATE(projector_editform, caplog):
    """
    Test when name duplicate
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    # As long as the new record port number is different, we should be good
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module, logging.WARNING, f'editform(): Name "{t_name}" already in database')
            ]
    projector_editform.exec()
    projector_editform.name_text.setText(t_name)
    projector_editform.projector.name = t_name

    # WHEN: Called
    caplog.clear()
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform.mock_msg_box.warning.assert_called_once_with(None,
                                                                    Message.NAME_DUPLICATE.title,
                                                                    Message.NAME_DUPLICATE.text)


def test_name_DATABASE_MULTIPLE(projector_editform, caplog):
    """
    Test when multiple database records have the same name
    """
    # GIVEN: Test setup
    # Save another instance of TEST1_DATA
    t_proj = Projector(**TEST1_DATA)
    t_proj.id = None
    projector_editform.projectordb.save_object(t_proj)

    # Test variables
    t_id1 = TEST1_DATA['id']
    # There should only be 3 records in the DB, TEST[1,2,3]_DATA
    # The above save_object() should have created record 4
    t_id2 = t_proj.id
    t_name = TEST1_DATA['name']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module, logging.WARNING, f'editform(): Multiple records found for name "{t_name}"'),
            (_test_module, logging.WARNING, f'editform() Found record={t_id1} name="{t_name}"'),
            (_test_module, logging.WARNING, f'editform() Found record={t_id2} name="{t_name}"')
            ]
    projector_editform.exec()
    projector_editform.name_text.setText(t_name)

    # WHEN: Called
    caplog.clear()
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform.mock_msg_box.warning.assert_called_once_with(None,
                                                                    Message.DATABASE_MULTIPLE.title,
                                                                    Message.DATABASE_MULTIPLE.text)


def test_ip_IP_BLANK(projector_editform_mtdb, caplog):
    """
    Test when IP field blank
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name')]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText('')

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.IP_BLANK.title,
                                                                         Message.IP_BLANK.text)


def test_ip_IP_INVALID(projector_editform_mtdb, caplog):
    """
    Test when IP invalid
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    t_ip = 'a'
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name')]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText(t_ip)

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.IP_INVALID.title,
                                                                         Message.IP_INVALID.text)


def test_port_PORT_BLANK(projector_editform_mtdb, caplog):
    """
    Test when port field blank
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    t_ip = TEST1_DATA['ip']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            ]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText(t_ip)
    projector_editform_mtdb.port_text.setText('')

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.PORT_BLANK.title,
                                                                         Message.PORT_BLANK.text)


def test_port_PORT_INVALID_not_decimal(projector_editform_mtdb, caplog):
    """
    Test when port not a decimal digit
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    t_ip = TEST1_DATA['ip']
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            ]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText(t_ip)
    projector_editform_mtdb.port_text.setText('a')

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.PORT_INVALID.title,
                                                                         Message.PORT_INVALID.text)


def test_port_PORT_INVALID_low(projector_editform_mtdb, caplog):
    """
    Test when port number less than PJLINK_VALID_PORTS lower value
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    t_ip = TEST1_DATA['ip']
    t_port = PJLINK_VALID_PORTS.start - 1
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            ]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText(t_ip)
    projector_editform_mtdb.port_text.setText(str(t_port))

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.PORT_INVALID.title,
                                                                         Message.PORT_INVALID.text)


def test_port_PORT_INVALID_high(projector_editform_mtdb, caplog):
    """
    Test when port number greater than PJLINK_VALID_PORTS higher value
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    t_ip = TEST1_DATA['ip']
    t_port = PJLINK_VALID_PORTS.stop + 1
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            ]
    projector_editform_mtdb.exec()
    projector_editform_mtdb.name_text.setText(t_name)
    projector_editform_mtdb.ip_text.setText(t_ip)
    projector_editform_mtdb.port_text.setText(str(t_port))

    # WHEN: Called
    caplog.clear()
    projector_editform_mtdb.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform_mtdb.mock_msg_box.warning.assert_called_once_with(None,
                                                                         Message.PORT_INVALID.title,
                                                                         Message.PORT_INVALID.text)


def test_name_ADDRESS_DUPLICATE(projector_editform, caplog):
    """
    Test when IP:Port address duplicate
    """
    # GIVEN: Test setup
    t_ip = TEST1_DATA['ip']
    t_port = TEST1_DATA['port']

    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module_db, logging.DEBUG, 'Filter by IP Port'),
            (_test_module, logging.WARNING, f'editform(): Address already in database {t_ip}:{t_port}')
            ]
    projector_editform.exec()
    projector_editform.name_text.setText('A Different Name Not In DB')
    projector_editform.ip_text.setText(t_ip)
    projector_editform.port_text.setText(str(t_port))

    # WHEN: Called
    caplog.clear()
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform.mock_msg_box.warning.assert_called_once_with(None,
                                                                    Message.ADDRESS_DUPLICATE.title,
                                                                    Message.ADDRESS_DUPLICATE.text)


def test_adx_DATABASE_MULTIPLE(projector_editform, caplog):
    """
    Test when database has multiple same IP:Port records
    """
    # GIVEN: Test setup
    t_proj = Projector(**TEST1_DATA)
    t_proj.id = None
    projector_editform.projectordb.save_object(t_proj)
    t_id1 = TEST1_DATA['id']
    t_id2 = t_proj.id
    t_name = TEST1_DATA['name']
    t_ip = TEST1_DATA['ip']
    t_port = TEST1_DATA['port']

    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'accept_me() signal received'),
            (_test_module_db, logging.DEBUG, 'Filter by Name'),
            (_test_module_db, logging.DEBUG, 'Filter by IP Port'),
            (_test_module, logging.WARNING, f'editform(): Multiple records found for {t_ip}:{t_port}'),
            (_test_module, logging.WARNING, f'editform(): record={t_id1} name="{t_name}" adx={t_ip}:{t_port}'),
            (_test_module, logging.WARNING, f'editform(): record={t_id2} name="{t_name}" adx={t_ip}:{t_port}')
            ]
    projector_editform.exec()
    projector_editform.name_text.setText('A Different Name Not In DB')
    projector_editform.ip_text.setText(t_ip)
    projector_editform.port_text.setText(str(t_port))

    # WHEN: Called
    caplog.clear()
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    assert caplog.record_tuples == logs, 'Invalid logs'
    projector_editform.mock_msg_box.warning.assert_called_once_with(None,
                                                                    Message.DATABASE_MULTIPLE.title,
                                                                    Message.DATABASE_MULTIPLE.text)

