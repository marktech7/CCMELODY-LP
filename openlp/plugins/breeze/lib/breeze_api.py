# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2023 OpenLP Developers                              #
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
The :mod:`~openlp.plugins.breeze.lib.breeze_api` module contains
an API interface for Breeze
"""
import logging
import os
import ssl
import requests

log = logging.getLogger(__name__)


class BreezeAPI:
    """
    The :class:`BreezeAPI` class is Breeze v2 API Class.
    """

    def __init__(self, username, secret, subdomain, token=""):
        """
        Initialize.

        :param username: User's Breeze username.
        :param secret:  User's Breeze password.
        :param subdomain: User's Breeze subdomain
        :param token: The cached Breeze token
        """
        self.api_url = 'https://api.breezechms.com/api/v2/'
        self.username = username
        self.secret = secret
        self.subdomain = subdomain
        self.token = token

    def test(self):
        """
        Fetches user info from Breeze.
        """
        response = self.__get('me')
        organization = response['organization']['name']
        return organization

    def token(self):
        return self.token

    def get_event_instances(self, start, end):
        """
        Returns the list of events that have service plans.

        :param start: Start Date, as date object.
        :type start: date
        :param end: End Date, as date object.
        :type end: date
        """
        events = self.__get('event-instances?filter[start_datetime:gt:date]={0}&filter[start_datetime:lt:date]={1}'
                            .format(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
                            )
        return filter(lambda event: 'service_plan_id' in event and event['service_plan_id'] is not None, events)

    def get_service_plan(self, service_plan_id):
        """
        Returns the service plan for the id given

        :param service_plan_id: ID of the service plan.
        """
        return self.__get(f'service-plans/{service_plan_id}')

    def __get(self, url):
        """
        Gets the response from the API for the provided url_suffix and returns
        the response as an object.

        :param url: The query part of the URL for the API.  The base is
        in self.api_url, and this suffix is appended to that to make the query.
        """
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
                getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context

        if not self.token:
            self.__login()

        # Fetch
        endpoint = self.api_url + url
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(endpoint, headers=headers)

        if 200 <= response.status_code < 300:
            return response.json()['data']
        elif response.status_code == 401:
            self.__refresh()
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(endpoint, headers=headers)
            if 200 <= response.status_code < 300:
                return response.json()['data']

        # TODO: Throw error if not 200
        return {}

    def __login(self):
        response = requests.post(self.api_url + 'auth/login', data={
            'username': self.username,
            'password': self.secret,
            'subdomain': self.subdomain,
            'version': 1
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']

        # TODO: Throw error if not 200

    def __refresh(self):
        response = requests.post(self.api_url + 'auth/refresh', headers={
            'Authorization': f'Bearer {self.token}'
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']

        # TODO: Throw error if not 200
