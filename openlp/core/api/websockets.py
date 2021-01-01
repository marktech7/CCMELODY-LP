# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2021 OpenLP Developers                              #
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
The :mod:`http` module contains the API web server. This is a lightweight web server used by remotes to interact
with OpenLP. It uses JSON to communicate with the remotes.
"""
import asyncio
import json
import logging
import time

from websockets import serve

from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.threading import ThreadWorker, run_thread

USERS = set()


log = logging.getLogger(__name__)
# Disable DEBUG logs for the websockets lib
ws_logger = logging.getLogger('websockets')
ws_logger.setLevel(logging.ERROR)


async def handle_websocket(websocket, path):
    """
    Handle web socket requests and return the state information
    Check every 0.2 seconds to get the latest position and send if it changed.

    :param websocket: request from client
    :param path: determines the endpoints supported - Not needed
    """
    log.debug('WebSocket handle_websocket connection')
    await register(websocket)
    reply = Registry().get('poller').poll_first_time()
    if reply:
        json_reply = json.dumps(reply).encode()
        await websocket.send(json_reply)
    while True:
        try:
            await notify_users()
            await asyncio.wait_for(websocket.recv(), 0.2)
        except asyncio.TimeoutError:
            pass
        except Exception:
            await unregister(websocket)
            break


async def register(websocket):
    """
    Register Clients
    :param websocket: The client details
    :return:
    """
    log.debug('WebSocket handler register')
    USERS.add(websocket)


async def unregister(websocket):
    """
    Unregister Clients
    :param websocket: The client details
    :return:
    """
    log.debug('WebSocket handler unregister')
    USERS.remove(websocket)


async def notify_users():
    """
    Dispatch state to all registered users if we have any changes
    :return:
    """
    if USERS:  # asyncio.wait doesn't accept an empty list
        reply = Registry().get('poller').poll()
        if reply:
            json_reply = json.dumps(reply).encode()
            await asyncio.wait([user.send(json_reply) for user in USERS])


class WebSocketWorker(ThreadWorker, RegistryProperties, LogMixin):
    """
    A special Qt thread class to allow the WebSockets server to run at the same time as the UI.
    """
    def start(self):
        """
        Run the worker.
        """
        settings = Registry().get('settings_thread')
        address = settings.value('api/ip address')
        port = settings.value('api/websocket port')
        # Start the event loop
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        # Create the websocker server
        loop = 1
        self.server = None
        while not self.server:
            try:
                self.server = serve(handle_websocket, address, port)
                log.debug('WebSocket server started on {addr}:{port}'.format(addr=address, port=port))
            except Exception:
                log.exception('Failed to start WebSocket server')
                loop += 1
                time.sleep(0.1)
            if not self.server and loop > 3:
                log.error('Unable to start WebSocket server {addr}:{port}, giving up'.format(addr=address, port=port))
        if self.server:
            # If the websocket server exists, start listening
            self.event_loop.run_until_complete(self.server)
            try:
                self.event_loop.run_forever()
            finally:
                self.event_loop.close()
        self.quit.emit()

    def stop(self):
        """
        Stop the websocket server
        """
        self.event_loop.call_soon_threadsafe(self.event_loop.stop)


class WebSocketServer(RegistryProperties, LogMixin):
    """
    Wrapper round a server instance
    """
    def __init__(self):
        """
        Initialise and start the WebSockets server
        """
        super(WebSocketServer, self).__init__()
        if not Registry().get_flag('no_web_server'):
            worker = WebSocketWorker()
            run_thread(worker, 'websocket_server')
