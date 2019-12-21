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
Functional tests to test the API Error Class.
"""
from openlp.core.api.http.errors import HttpError, NotFound, ServerError


def test_http_error():
    """
    Test the HTTPError class
    """
    # GIVEN: An HTTPError class
    # WHEN: An instance is created
    error = HttpError(400, 'Access Denied')

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Access Denied', 400), 'to_response() should have returned the correct info'


def test_not_found():
    """
    Test the Not Found error displays the correct information
    """
    # GIVEN: A NotFound class
    # WHEN: An instance is created
    error = NotFound()

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Not Found', 404), 'to_response() should have returned the correct info'


def test_server_error():
    """
    Test the server error displays the correct information
    """
    # GIVEN: A ServerError class
    # WHEN: An instance of the class is created
    error = ServerError()

    # THEN: The to_response() method should return the correct information
    assert error.to_response() == ('Server Error', 500), 'to_response() should have returned the correct info'
