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
The :mod:`openlp.core.lib.projector.pjlink` module provides the necessary functions for connecting to a PJLink-capable
projector.

PJLink Class 1 Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Website: http://pjlink.jbmia.or.jp/english/dl_class1.html

- Section 5-1 PJLink Specifications
- Section 5-5 Guidelines for Input Terminals

PJLink Class 2 Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Website: http://pjlink.jbmia.or.jp/english/dl_class2.html

- Section 5-1 PJLink Specifications
- Section 5-5 Guidelines for Input Terminals

.. note:
    Function names follow the following syntax::

        def process_CCCC(...):

    where ``CCCC`` is the PJLink command being processed
"""
import logging
from codecs import decode
from copy import copy

from PyQt5 import QtCore, QtNetwork

from openlp.core.common import qmd5_hash
from openlp.core.common.i18n import translate
from openlp.core.common.settings import Settings
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import CONNECTION_ERRORS, E_AUTHENTICATION, E_CONNECTION_REFUSED, E_GENERAL, \
    E_NETWORK, E_NOT_CONNECTED, E_SOCKET_TIMEOUT, PJLINK_CLASS, \
    PJLINK_MAX_PACKET, PJLINK_PORT, PJLINK_PREFIX, PJLINK_SUFFIX, \
    PJLINK_VALID_CMD, PROJECTOR_STATE, QSOCKET_STATE, S_AUTHENTICATE, S_CONNECT, S_CONNECTED, S_CONNECTING, \
    S_DATA_OK, S_NOT_CONNECTED, S_OFF, S_OK, S_ON, STATUS_CODE, STATUS_MSG


log = logging.getLogger(__name__)
log.debug('pjlink loaded')

__all__ = ['PJLink', 'PJLinkUDP']

# Shortcuts
SocketError = QtNetwork.QAbstractSocket.SocketError
SocketSTate = QtNetwork.QAbstractSocket.SocketState

# Add prefix here, but defer linkclass expansion until later when we have the actual
# PJLink class for the command
PJLINK_HEADER = '{prefix}{{linkclass}}'.format(prefix=PJLINK_PREFIX)


class PJLinkUDP(QtNetwork.QUdpSocket):
    """
    Socket service for PJLink UDP socket.
    """

    data_received = QtCore.pyqtSignal(QtNetwork.QHostAddress, int, str, name='udp_data')  # host, port, data

    def __init__(self, port=PJLINK_PORT):
        """
        Socket services for PJLink UDP packets.

        Since all UDP packets from any projector will come into the same
        port, process UDP packets here then route to the appropriate
        projector instance as needed.

        :param port:  UDP port to listen on
        """
        super().__init__()
        self.port = port
        # Local defines
        self.search_active = False
        self.search_time = 30000  # 30 seconds for allowed time
        self.search_timer = QtCore.QTimer()
        self.udp_broadcast_listen_setting = False
        log.debug('(UDP:{port}) PJLinkUDP() Initialized'.format(port=self.port))
        if Settings().value('projector/udp broadcast listen'):
            self.udp_start()

    def udp_start(self):
        """
        Start listening on UDP port
        """
        log.debug('(UDP:{port}) Start called'.format(port=self.port))
        self.readyRead.connect(self.get_datagram)
        self.check_settings(checked=Settings().value('projector/udp broadcast listen'))

    def udp_stop(self):
        """
        Stop listening on UDP port
        """
        log.debug('(UDP:{port}) Stopping listener'.format(port=self.port))
        self.close()
        self.readyRead.disconnect(self.get_datagram)

    @QtCore.pyqtSlot()
    def get_datagram(self):
        """
        Retrieve packet and basic checks
        """
        log.debug('(UDP:{port}) get_datagram() - Receiving data'.format(port=self.port))
        read_size = self.pendingDatagramSize()
        if -1 == read_size:
            log.warning('(UDP:{port}) No data (-1)'.format(port=self.port))
            return
        elif 0 == read_size:
            log.warning('(UDP:{port}) get_datagram() called when pending data size is 0'.format(port=self.port))
            return
        elif read_size > PJLINK_MAX_PACKET:
            log.warning('(UDP:{port}) UDP Packet too large ({size} bytes)- ignoring'.format(size=read_size,
                                                                                            port=self.port))
            return
        data_in, peer_host, peer_port = self.readDatagram(read_size)
        data = data_in.decode('utf-8') if isinstance(data_in, bytes) else data_in
        log.debug('(UDP:{port}) {size} bytes received from {adx}'.format(size=len(data),
                                                                         adx=peer_host.toString(),
                                                                         port=self.port))
        log.debug('(UDP:{port}) packet "{data}"'.format(data=data, port=self.port))
        log.debug('(UDP:{port}) Sending data_received signal to projectors'.format(port=self.port))
        self.data_received.emit(peer_host, self.localPort(), data)
        return

    def search_start(self):
        """
        Start search for projectors on local network
        """
        self.search_active = True
        # TODO: Send SRCH packet here
        self.search_timer.singleShot(self.search_time, self.search_stop)

    @QtCore.pyqtSlot()
    def search_stop(self):
        """
        Stop search
        """
        self.search_active = False
        self.search_timer.stop()

    def check_settings(self, checked):
        """
        Update UDP listening state based on settings change.
        NOTE: This method is called by projector settings tab and setup/removed by ProjectorManager
        """
        if self.udp_broadcast_listen_setting == checked:
            log.debug('(UDP:{port}) No change to status - skipping'.format(port=self.port))
            return
        self.udp_broadcast_listen_setting = checked
        if self.udp_broadcast_listen_setting:
            if self.state() == self.ListeningState:
                log.debug('(UDP:{port}) Already listening - skipping')
                return
            self.bind(self.port)
            log.debug('(UDP:{port}) Listening'.format(port=self.port))
        else:
            # Close socket
            self.udp_stop()


class PJLink(QtNetwork.QTcpSocket):
    """
    Socket services for PJLink TCP packets.
    """
    # Signals sent by this module
    changeStatus = QtCore.pyqtSignal(str, int, str)
    projectorStatus = QtCore.pyqtSignal(int)  # Status update
    projectorAuthentication = QtCore.pyqtSignal(str)  # Authentication error
    projectorNoAuthentication = QtCore.pyqtSignal(str)  # PIN set and no authentication needed
    projectorReceivedData = QtCore.pyqtSignal()  # Notify when received data finished processing
    projectorUpdateIcons = QtCore.pyqtSignal()  # Update the status icons on toolbar

    def __init__(self, projector, *args, **kwargs):
        """
        Setup for instance.
        Options should be in kwargs except for port which does have a default.

        :param projector: Database record of projector

        Optional parameters
        :param poll_time: Time (in seconds) to poll connected projector
        :param socket_timeout: Time (in seconds) to abort the connection if no response
        """
        log.debug('PJlink(projector="{projector}", args="{args}" kwargs="{kwargs}")'.format(projector=projector,
                                                                                            args=args,
                                                                                            kwargs=kwargs))
        super().__init__()
        self.settings_section = 'projector'
        self.entry = projector
        self.ip = self.entry.ip
        self.qhost = QtNetwork.QHostAddress(self.ip)
        self.location = self.entry.location
        self.mac_adx = self.entry.mac_adx
        self.name = self.entry.name
        self.notes = self.entry.notes
        self.pin = self.entry.pin
        self.port = int(self.entry.port)
        self.pjlink_class = PJLINK_CLASS if self.entry.pjlink_class is None else self.entry.pjlink_class
        self.ackn_list = {}  # Replies from online projectors (Class 2 option)
        self.db_update = False  # Use to check if db needs to be updated prior to exiting
        # Poll time 20 seconds unless called with something else
        self.poll_time = 20000 if 'poll_time' not in kwargs else kwargs['poll_time'] * 1000
        # Socket timeout (in case of brain-dead projectors) 5 seconds unless called with something else
        self.socket_timeout = 5000 if 'socket_timeout' not in kwargs else kwargs['socket_timeout'] * 1000
        # In case we're called from somewhere that only wants information
        self.no_poll = 'no_poll' in kwargs
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        # Socket information
        # Add enough space to input buffer for extraneous \n \r
        self.max_size = PJLINK_MAX_PACKET + 2
        self.setReadBufferSize(self.max_size)
        self.reset_information()
        self.send_queue = []
        self.priority_queue = []
        self.send_busy = False
        # Poll timer for status updates
        self.poll_timer = QtCore.QTimer(self)  # Timer that calls the poll_loop
        self.poll_timer.setInterval(self.poll_time)
        self.poll_timer.timeout.connect(self.poll_loop)
        # Socket timer for some possible brain-dead projectors or network issues
        self.socket_timer = QtCore.QTimer(self)
        self.socket_timer.setInterval(self.socket_timeout)
        self.socket_timer.timeout.connect(self.socket_abort)
        # Timer for doing status updates for commands that change state and should update faster
        self.status_timer_checks = {}  # Keep track of events for the status timer
        self.status_timer = QtCore.QTimer(self)
        self.status_timer.setInterval(2000)  # 2 second interval should be fast enough
        self.status_timer.timeout.connect(self.status_timer_update)
        # Socket status signals
        self.connected.connect(self.check_login)
        self.disconnected.connect(self.disconnect_from_host)
        self.error.connect(self.get_error)
        self.projectorReceivedData.connect(self._send_command)

    def reset_information(self):
        """
        Initialize instance variables. Also used to reset projector-specific information to default.
        """
        conn_state = STATUS_CODE[QSOCKET_STATE[self.state()]]
        log.debug('({ip}) reset_information() connect status is {state}'.format(ip=self.entry.name,
                                                                                state=conn_state))
        self.fan = None  # ERST
        self.filter_time = None  # FILT
        self.lamp = None  # LAMP
        self.mac_adx_received = None  # ACKN
        self.manufacturer = None  # INF1
        self.model = None  # INF2
        self.model_filter = None  # RFIL
        self.model_lamp = None  # RLMP
        self.mute = None  # AVMT
        self.other_info = None  # INFO
        self.pjlink_class = copy(PJLINK_CLASS)
        self.pjlink_name = None  # NAME
        self.power = S_OFF  # POWR
        self.projector_errors = {}  # Full ERST errors
        self.serial_no = None  # SNUM
        self.serial_no_received = None
        self.sw_version = None  # SVER
        self.sw_version_received = None
        self.shutter = None  # AVMT
        self.source_available = None  # INST
        self.source = None  # INPT
        # These should be part of PJLink() class, but set here for convenience
        if hasattr(self, 'poll_timer'):
            log.debug('({ip}): Calling poll_timer.stop()'.format(ip=self.entry.name))
            self.poll_timer.stop()
        if hasattr(self, 'socket_timer'):
            log.debug('({ip}): Calling socket_timer.stop()'.format(ip=self.entry.name))
            self.socket_timer.stop()
        if hasattr(self, 'status_timer'):
            log.debug('({ip}): Calling status_timer.stop()'.format(ip=self.entry.name))
            self.status_timer.stop()
        self.status_timer_checks = {}
        self.send_busy = False
        self.send_queue = []
        self.priority_queue = []

    def socket_abort(self):
        """
        Aborts connection and closes socket in case of brain-dead projectors.
        Should normally be called by socket_timer().
        """
        log.debug('({ip}) socket_abort() - Killing connection'.format(ip=self.entry.name))
        self.disconnect_from_host(abort=True)

    def poll_loop(self):
        """
        Retrieve information from projector that changes.
        Normally called by timer().
        """
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning('({ip}) poll_loop(): Not connected - returning'.format(ip=self.entry.name))
            # Stop timer just in case it's missed elsewhere
            self.poll_timer.stop()
            return
        log.debug('({ip}) poll_loop(): Updating projector status'.format(ip=self.entry.name))
        # The following commands do not change, so only check them once
        # Call them first in case other functions rely on something here
        if self.power == S_ON and self.source_available is None:
            self.send_command('INST')
        if self.other_info is None:
            self.send_command('INFO')
        if self.manufacturer is None:
            self.send_command('INF1')
        if self.model is None:
            self.send_command('INF2')
        if self.pjlink_name is None:
            self.send_command('NAME')
        if self.pjlink_class == '2':
            # Class 2 specific checks
            if self.serial_no is None:
                self.send_command('SNUM')
            if self.sw_version is None:
                self.send_command('SVER')
            if self.model_filter is None:
                self.send_command('RFIL')
            if self.model_lamp is None:
                self.send_command('RLMP')
        # These commands may change during connection
        check_list = ['POWR', 'ERST', 'LAMP', 'AVMT', 'INPT']
        if self.pjlink_class == '2':
            check_list.extend(['FILT', 'FREZ'])
        for command in check_list:
            self.send_command(command)
        # Reset the poll_timer for normal operations in case of initial connection
        self.poll_timer.setInterval(self.poll_time)

    def _get_status(self, status):
        """
        Helper to retrieve status/error codes and convert to strings.

        :param status: Status/Error code
        :returns: tuple (-1 if code not INT, None)
        :returns: tuple (string: code as string, None if no description)
        :returns: tuple (string: code as string, string: Status/Error description)
        """
        if not isinstance(status, int):
            return -1, None
        elif status not in STATUS_MSG:
            return None, None
        else:
            return STATUS_CODE[status], STATUS_MSG[status]

    def change_status(self, status, msg=None):
        """
        Check connection/error status, set status for projector, then emit status change signal
        for gui to allow changing the icons.

        :param status: Status code
        :param msg: Optional message
        """
        if status in STATUS_CODE:
            log.debug('({ip}) Changing status to {status} '
                      '"{msg}"'.format(ip=self.entry.name,
                                       status=STATUS_CODE[status],
                                       msg=msg if msg is not None else STATUS_MSG[status]))
        else:
            log.warning('({ip}) Unknown status change code: {code}'.format(ip=self.entry.name,
                                                                           code=status))
            return
        if status in CONNECTION_ERRORS:
            # Connection state error affects both socket and projector
            self.error_status = status
            self.status_connect = E_NOT_CONNECTED
        elif status >= S_NOT_CONNECTED and status in QSOCKET_STATE:
            # Socket connection status update
            self.status_connect = status
            # Check if we need to update error state as well
            if self.error_status != S_OK and status != S_NOT_CONNECTED:
                self.error_status = S_OK
        elif status >= S_NOT_CONNECTED and status in PROJECTOR_STATE:
            # Only affects the projector status
            self.projector_status = status

        # These log entries are for troubleshooting only
        (status_code, status_message) = self._get_status(self.status_connect)
        log.debug('({ip}) status_connect: {code}: "{message}"'.format(ip=self.entry.name,
                                                                      code=status_code,
                                                                      message=status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.projector_status)
        log.debug('({ip}) projector_status: {code}: "{message}"'.format(ip=self.entry.name,
                                                                        code=status_code,
                                                                        message=status_message if msg is None else msg))
        (status_code, status_message) = self._get_status(self.error_status)
        log.debug('({ip}) error_status: {code}: "{message}"'.format(ip=self.entry.name,
                                                                    code=status_code,
                                                                    message=status_message if msg is None else msg))

        # Now that we logged extra information for debugging, broadcast the original change/message
        # Check for connection errors first
        if self.error_status != S_OK:
            log.debug('({ip}) Signalling error code'.format(ip=self.entry.name))
            code, message = self._get_status(self.error_status)
            status = self.error_status
        else:
            log.debug('({ip}) Signalling status code'.format(ip=self.entry.name))
            code, message = self._get_status(status)
        if msg is not None:
            message = msg
        elif message is None:
            # No message for status code
            message = translate('OpenLP.PJLink', 'No message') if msg is None else msg

        self.changeStatus.emit(self.ip, status, message)
        self.projectorUpdateIcons.emit()

    @QtCore.pyqtSlot()
    def check_login(self, data=None):
        """
        Processes the initial connection and convert to a PJLink packet if valid initial connection

        :param data: Optional data if called from another routine
        """
        log.debug('({ip}) check_login(data="{data}")'.format(ip=self.entry.name, data=data))
        if data is None:
            # Reconnected setup?
            if not self.waitForReadyRead(2000):
                # Possible timeout issue
                log.error('({ip}) Socket timeout waiting for login'.format(ip=self.entry.name))
                self.change_status(E_SOCKET_TIMEOUT)
                return
            read = self.readLine(self.max_size)
            self.readLine(self.max_size)  # Clean out any trailing whitespace
            if read is None:
                log.warning('({ip}) read is None - socket error?'.format(ip=self.entry.name))
                return
            elif len(read) < 8:
                log.warning('({ip}) Not enough data read - skipping'.format(ip=self.entry.name))
                return
            data = decode(read, 'utf-8')
            # Possibility of extraneous data on input when reading.
            # Clean out extraneous characters in buffer.
            self.read(1024)
            log.debug('({ip}) check_login() read "{data}"'.format(ip=self.entry.name, data=data.strip()))
        # At this point, we should only have the initial login prompt with
        # possible authentication
        # PJLink initial login will be:
        # 'PJLink 0' - Unauthenticated login - no extra steps required.
        # 'PJLink 1 XXXXXX' Authenticated login - extra processing required.
        if not data.startswith('PJLINK'):
            # Invalid initial packet - close socket
            log.error('({ip}) Invalid initial packet received - closing socket'.format(ip=self.entry.name))
            return self.disconnect_from_host()
        # Convert the initial login prompt with the expected PJLink normal command format for processing
        log.debug('({ip}) check_login(): Formatting initial connection prompt '
                  'to PJLink packet'.format(ip=self.entry.name))
        return self.get_data('{start}{clss}{data}'.format(start=PJLINK_PREFIX,
                                                          clss='1',
                                                          data=data.replace(' ', '=', 1)).encode('utf-8'))

    def _trash_buffer(self, msg=None):
        """
        Clean out extraneous stuff in the buffer.
        """
        log.debug('({ip}) Cleaning buffer - msg = "{message}"'.format(ip=self.entry.name, message=msg))
        if msg is None:
            msg = 'Invalid packet'
        log.warning('({ip}) {message}'.format(ip=self.entry.name, message=msg))
        self.send_busy = False
        trash_count = 0
        while self.bytesAvailable() > 0:
            trash = self.read(self.max_size)
            trash_count += len(trash)
        log.debug('({ip}) Finished cleaning buffer - {count} bytes dropped'.format(ip=self.entry.name,
                                                                                   count=trash_count))
        return

    @QtCore.pyqtSlot(QtNetwork.QHostAddress, int, str, name='udp_data')  # host, port, data
    def get_buffer(self, host, port, data):
        """
        Get data from somewhere other than TCP socket

        :param host:  QHostAddress of sender
        :param port:  Destination port
        :param data:  Data to process. buffer must be formatted as a proper PJLink packet.
        """
        if (port == int(self.port)) and (host.isEqual(self.qhost)):
            log.debug('({ip}) Received data from {host}'.format(ip=self.entry.name, host=host.toString()))
            log.debug('({ip}) get_buffer(data="{buff}")'.format(ip=self.entry.name, buff=data))
            return self.get_data(buff=data)
        else:
            log.debug('({ip}) Ignoring data for {host} - not me'.format(ip=self.entry.name, host=host.toString()))

    @QtCore.pyqtSlot()
    def get_socket(self):
        """
        Get data from TCP socket.
        """
        log.debug('({ip}) get_socket(): Reading data'.format(ip=self.entry.name))
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.debug('({ip}) get_socket(): Not connected - returning'.format(ip=self.entry.name))
            self.send_busy = False
            return
        # Although we have a packet length limit, go ahead and use a larger buffer
        self.socket_timer.start()
        while self.bytesAvailable() >= 1:
            data = self.readLine(1024)
            data = data.strip()
            if not data:
                log.warning('({ip}) get_socket(): Ignoring empty packet'.format(ip=self.entry.name))
                if self.bytesAvailable() < 1:
                    break

        self.socket_timer.stop()
        if data:
            log.debug('({ip}) get_socket(): "{buff}"'.format(ip=self.entry.name, buff=data))
        if data == -1:
            # No data available
            log.debug('({ip}) get_socket(): No data available (-1)'.format(ip=self.entry.name))
            return
        return self.get_data(buff=data)

    def get_data(self, buff, *args, **kwargs):
        """
        Process received data

        :param buff:    Data to process.
        """
        log.debug('({ip}) get_data(buffer="{buff}"'.format(ip=self.entry.name, buff=buff))
        ignore_class = 'ignore_class' in kwargs
        # NOTE: Class2 has changed to some values being UTF-8
        data_in = decode(buff, 'utf-8') if isinstance(buff, bytes) else buff
        data = data_in.strip()
        self.receive_data_signal()
        # Initial packet checks
        if len(data) < 7:
            self._trash_buffer(msg='get_data(): Invalid packet - length')
            return
        elif len(data) > self.max_size:
            self._trash_buffer(msg='get_data(): Invalid packet - too long ({length} bytes)'.format(length=len(data)))
            return
        elif not data.startswith(PJLINK_PREFIX):
            self._trash_buffer(msg='get_data(): Invalid packet - PJLink prefix missing')
            return
        elif data[6] != '=' and data[8] != '=':
            # data[6] = standard command packet
            # data[8] = initial PJLink connection (after mangling)
            self._trash_buffer(msg='get_data(): Invalid reply - Does not have "="')
            return
        log.debug('({ip}) get_data(): Checking new data "{data}"'.format(ip=self.entry.name, data=data))
        header, data = data.split('=')
        log.debug('({ip}) get_data() header="{header}" data="{data}"'.format(ip=self.entry.name,
                                                                             header=header, data=data))
        # At this point, the header should contain:
        #   "PVCCCC"
        #   Where:
        #       P = PJLINK_PREFIX
        #       V = PJLink class or version
        #       C = PJLink command
        version, cmd = header[1], header[2:].upper()
        log.debug('({ip}) get_data() version="{version}" cmd="{cmd}" data="{data}"'.format(ip=self.entry.name,
                                                                                           version=version,
                                                                                           cmd=cmd,
                                                                                           data=data))
        if cmd not in PJLINK_VALID_CMD:
            self._trash_buffer('get_data(): Invalid packet - unknown command "{data}"'.format(data=cmd))
            return
        elif version not in PJLINK_VALID_CMD[cmd]['version']:
            self._trash_buffer(msg='get_data() Command reply version does not match a valid command version')
            return
        elif int(self.pjlink_class) < int(version):
            if not ignore_class:
                log.warning('({ip}) get_data(): Projector returned class reply higher '
                            'than projector stated class'.format(ip=self.entry.name))
                return

        chk = process_command(self, cmd, data)
        if chk is None:
            # Command processed normally and not initial connection, so skip other checks
            return
        # PJLink initial connection checks
        elif chk == S_DATA_OK:
            # Previous command returned OK
            log.debug('({ip}) OK returned - resending command'.format(ip=self.entry.name))
            self.send_command(cmd=cmd, priority=True)
        elif chk == S_CONNECT:
            # Normal connection
            log.debug('({ip}) Connecting normal'.format(ip=self.entry.name))
            self.change_status(S_CONNECTED)
            self.send_command(cmd='CLSS', priority=True)
            self.readyRead.connect(self.get_socket)
        elif chk == S_AUTHENTICATE:
            # Connection with pin
            log.debug('({ip}) Connecting with pin'.format(ip=self.entry.name))
            data_hash = str(qmd5_hash(salt=chk[1].encode('utf-8'), data=self.pin.encode('utf-8')),
                            encoding='ascii')
            self.change_status(S_CONNECTED)
            self.readyRead.connect(self.get_socket)
            self.send_command(cmd='CLSS', salt=data_hash, priority=True)
        elif chk == E_AUTHENTICATION:
            # Projector did not like our pin
            log.warning('({ip}) Failed authentication - disconnecting'.format(ip=self.entry.name))
            self.disconnect_from_host()
            self.projectorAuthentication.emit(self.entry.name)
            self.change_status(status=E_AUTHENTICATION)

        return

    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketError)
    def get_error(self, err):
        """
        Process error from SocketError signal.
        Remaps system error codes to projector error codes.

        :param err: Error code
        """
        log.debug('({ip}) get_error(err={error}): {data}'.format(ip=self.entry.name,
                                                                 error=err,
                                                                 data=self.errorString()))
        if err <= 18:
            # QSocket errors. Redefined in projector.constants so we don't mistake
            # them for system errors
            check = err + E_CONNECTION_REFUSED
            self.poll_timer.stop()
        else:
            check = err
        if check < E_GENERAL:
            # Some system error?
            self.change_status(err, self.errorString())
        else:
            self.change_status(E_NETWORK, self.errorString())
        self.projectorUpdateIcons.emit()
        if self.status_connect == E_NOT_CONNECTED:
            self.abort()
            self.reset_information()
        return

    def send_command(self, cmd, opts='?', salt=None, priority=False):
        """
        Add command to output queue if not already in queue.

        :param cmd: Command to send
        :param opts: Command option (if any) - defaults to '?' (get information)
        :param salt: Optional  salt for md5 hash initial authentication
        :param priority: Option to send packet now rather than queue it up
        """
        log.debug('({ip}) send_command(cmd="{cmd}" opts="{opts}" salt="{salt}" '
                  'priority={pri}'.format(ip=self.entry.name, cmd=cmd, opts=opts, salt=salt, pri=priority))
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning('({ip}) send_command(): Not connected - returning'.format(ip=self.entry.name))
            return self.reset_information()
        if cmd not in PJLINK_VALID_CMD:
            log.error('({ip}) send_command(): Invalid command requested - ignoring.'.format(ip=self.entry.name))
            if self.priority_queue or self.send_queue:
                # Just in case there's already something to send
                return self._send_command()
            return
        log.debug('({ip}) send_command(): Building cmd="{command}" opts="{data}" '
                  '{salt}'.format(ip=self.entry.name,
                                  command=cmd,
                                  data=opts,
                                  salt='' if salt is None else 'with hash'))
        # Until we absolutely have to start doing version checks, use the default
        # for PJLink class
        header = PJLINK_HEADER.format(linkclass=PJLINK_VALID_CMD[cmd]['default'])
        out = '{salt}{header}{command} {options}{suffix}'.format(salt="" if salt is None else salt,
                                                                 header=header,
                                                                 command=cmd,
                                                                 options=opts,
                                                                 suffix=PJLINK_SUFFIX)
        if out in self.priority_queue:
            log.warning('({ip}) send_command(): Already in priority queue - skipping'.format(ip=self.entry.name))
        elif out in self.send_queue:
            log.warning('({ip}) send_command(): Already in normal queue - skipping'.format(ip=self.entry.name))
        else:
            if priority:
                log.debug('({ip}) send_command(): Adding to priority queue'.format(ip=self.entry.name))
                self.priority_queue.append(out)
            else:
                log.debug('({ip}) send_command(): Adding to normal queue'.format(ip=self.entry.name))
                self.send_queue.append(out)
        if self.priority_queue or self.send_queue:
            # May be some initial connection setup so make sure we send data
            self._send_command()

    @QtCore.pyqtSlot()
    def _send_command(self, data=None, utf8=False):
        """
        Socket interface to send data. If data=None, then check queue.

        :param data: Immediate data to send (Optional)
        :param utf8: Send as UTF-8 string otherwise send as ASCII string
        """
        if not data and not self.priority_queue and not self.send_queue:
            log.warning('({ip}) _send_command(): Nothing to send - returning'.format(ip=self.entry.name))
            self.send_busy = False
            return
        log.debug('({ip}) _send_command(data="{data}")'.format(ip=self.entry.name,
                                                               data=data.strip() if data else data))
        log.debug('({ip}) _send_command(): priority_queue: {queue}'.format(ip=self.entry.name,
                                                                           queue=self.priority_queue))
        log.debug('({ip}) _send_command(): send_queue: {queue}'.format(ip=self.entry.name,
                                                                       queue=self.send_queue))
        conn_state = STATUS_CODE[QSOCKET_STATE[self.state()]]
        log.debug('({ip}) _send_command(): Connection status: {data}'.format(ip=self.entry.name,
                                                                             data=conn_state))
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning('({ip}) _send_command() Not connected - abort'.format(ip=self.entry.name))
            self.send_busy = False
            return self.disconnect_from_host()
        if data and data not in self.priority_queue:
            log.debug('({ip}) _send_command(): Priority packet - adding to priority queue'.format(ip=self.entry.name))
            self.priority_queue.append(data)

        if self.send_busy:
            # Still waiting for response from last command sent
            log.debug('({ip}) _send_command(): Still busy, returning'.format(ip=self.entry.name))
            log.debug('({ip}) _send_command(): Priority queue = {data}'.format(ip=self.entry.name,
                                                                               data=self.priority_queue))
            log.debug('({ip}) _send_command(): Normal queue = {data}'.format(ip=self.entry.name, data=self.send_queue))
            return

        if not self.priority_queue and not self.send_queue:
            # No data to send
            log.warning('({ip}) _send_command(): No data to send'.format(ip=self.entry.name))
            self.send_busy = False
            return
        elif self.priority_queue:
            out = self.priority_queue.pop(0)
            log.debug('({ip}) _send_command(): Getting priority queued packet'.format(ip=self.entry.name))
        elif self.send_queue:
            out = self.send_queue.pop(0)
            log.debug('({ip}) _send_command(): Getting normal queued packet'.format(ip=self.entry.name))
        self.send_busy = True
        log.debug('({ip}) _send_command(): Sending "{data}"'.format(ip=self.entry.name, data=out.strip()))
        self.socket_timer.start()
        sent = self.write(out.encode('{string_encoding}'.format(string_encoding='utf-8' if utf8 else 'ascii')))
        self.waitForBytesWritten(2000)  # 2 seconds should be enough
        if sent == -1:
            # Network error?
            self.change_status(E_NETWORK,
                               translate('OpenLP.PJLink', 'Error while sending data to projector'))
            log.warning('({ip}) _send_command(): -1 received - disconnecting from host'.format(ip=self.entry.name))
            self.disconnect_from_host()

    def connect_to_host(self):
        """
        Initiate connection to projector.
        """
        log.debug('({ip}) connect_to_host(): Starting connection'.format(ip=self.entry.name))
        if QSOCKET_STATE[self.state()] == S_CONNECTED:
            log.warning('({ip}) connect_to_host(): Already connected - returning'.format(ip=self.entry.name))
            return
        self.error_status = S_OK
        self.change_status(S_CONNECTING)
        self.connectToHost(self.ip, self.port)

    @QtCore.pyqtSlot()
    def disconnect_from_host(self, abort=False):
        """
        Close socket and cleanup.
        """
        if abort or QSOCKET_STATE[self.state()] != S_NOT_CONNECTED:
            if abort:
                log.warning('({ip}) disconnect_from_host(): Aborting connection'.format(ip=self.entry.name))
                self.abort()
            else:
                log.warning('({ip}) disconnect_from_host(): Not connected'.format(ip=self.entry.name))
        try:
            self.readyRead.disconnect(self.get_socket)
        except TypeError:
            # Since we already know what's happening, just log it for reference.
            log.debug('({ip}) disconnect_from_host(): Issue detected with '
                      'readyRead.disconnect'.format(ip=self.entry.name))
        log.debug('({ip}) disconnect_from_host(): '
                  'Current status {data}'.format(ip=self.entry.name, data=self._get_status(self.status_connect)[0]))
        self.disconnectFromHost()
        if abort:
            self.change_status(E_NOT_CONNECTED)
        else:
            self.change_status(S_NOT_CONNECTED)
        self.reset_information()

    def get_av_mute_status(self, priority=False):
        """
        Send command to retrieve shutter status.
        """
        log.debug('({ip}) Sending AVMT command'.format(ip=self.entry.name))
        return self.send_command(cmd='AVMT', priority=priority)

    def get_available_inputs(self):
        """
        Send command to retrieve available source inputs.
        """
        log.debug('({ip}) Sending INST command'.format(ip=self.entry.name))
        return self.send_command(cmd='INST')

    def get_error_status(self):
        """
        Send command to retrieve currently known errors.
        """
        log.debug('({ip}) Sending ERST command'.format(ip=self.entry.name))
        return self.send_command(cmd='ERST')

    def get_input_source(self):
        """
        Send command to retrieve currently selected source input.
        """
        log.debug('({ip}) Sending INPT command'.format(ip=self.entry.name))
        return self.send_command(cmd='INPT')

    def get_lamp_status(self):
        """
        Send command to return the lap status.
        """
        log.debug('({ip}) Sending LAMP command'.format(ip=self.entry.name))
        return self.send_command(cmd='LAMP')

    def get_manufacturer(self):
        """
        Send command to retrieve manufacturer name.
        """
        log.debug('({ip}) Sending INF1 command'.format(ip=self.entry.name))
        return self.send_command(cmd='INF1')

    def get_model(self):
        """
        Send command to retrieve the model name.
        """
        log.debug('({ip}) Sending INF2 command'.format(ip=self.entry.name))
        return self.send_command(cmd='INF2')

    def get_name(self):
        """
        Send command to retrieve name as set by end-user (if set).
        """
        log.debug('({ip}) Sending NAME command'.format(ip=self.entry.name))
        return self.send_command(cmd='NAME')

    def get_other_info(self):
        """
        Send command to retrieve extra info set by manufacturer.
        """
        log.debug('({ip}) Sending INFO command'.format(ip=self.entry.name))
        return self.send_command(cmd='INFO')

    def get_power_status(self, priority=False):
        """
        Send command to retrieve power status.

        :param priority: (OPTIONAL) Send in priority queue
        """
        log.debug('({ip}) Sending POWR command'.format(ip=self.entry.name))
        return self.send_command(cmd='POWR', priority=priority)

    def set_audio_mute(self, priority=False):
        """
        Send command to set audio to muted
        """
        log.debug('({ip}) Setting AVMT to 21 (audio mute)'.format(ip=self.entry.name))
        self.send_command(cmd='AVMT', opts='21', priority=True)
        self.status_timer_add(cmd='AVMT', callback=self.get_av_mute_status)
        self.poll_loop()

    def set_audio_normal(self, priority=False):
        """
        Send command to set audio to normal
        """
        log.debug('({ip}) Setting AVMT to 20 (audio normal)'.format(ip=self.entry.name))
        self.send_command(cmd='AVMT', opts='20', priority=True)
        self.status_timer_add(cmd='AVMT', callback=self.get_av_mute_status)
        self.poll_loop()

    def set_input_source(self, src=None):
        """
        Verify input source available as listed in 'INST' command,
        then send the command to select the input source.

        :param src: Video source to select in projector
        """
        log.debug('({ip}) set_input_source(src="{data}")'.format(ip=self.entry.name, data=src))
        if self.source_available is None:
            return
        elif src not in self.source_available:
            return
        log.debug('({ip}) Setting input source to "{data}"'.format(ip=self.entry.name, data=src))
        self.send_command(cmd='INPT', opts=src, priority=True)
        self.poll_loop()

    def set_power_on(self):
        """
        Send command to turn power to on.
        """
        log.debug('({ip}) Setting POWR to 1 (on)'.format(ip=self.entry.name))
        self.send_command(cmd='POWR', opts='1', priority=True)
        self.status_timer_add(cmd='POWR', callback=self.get_power_status)
        self.poll_loop()

    def set_power_off(self):
        """
        Send command to turn power to standby.
        """
        log.debug('({ip}) Setting POWR to 0 (standby)'.format(ip=self.entry.name))
        self.send_command(cmd='POWR', opts='0', priority=True)
        self.status_timer_add(cmd='POWR', callback=self.get_power_status)
        self.poll_loop()

    def set_shutter_closed(self):
        """
        Send command to set shutter to closed position.
        """
        log.debug('({ip}) Setting AVMT to 11 (shutter closed)'.format(ip=self.entry.name))
        self.send_command(cmd='AVMT', opts='11', priority=True)
        self.status_timer_add('AVMT', self.get_av_mute_status)
        self.poll_loop()

    def set_shutter_open(self):
        """
        Send command to set shutter to open position.
        """
        log.debug('({ip}) Setting AVMT to "10" (shutter open)'.format(ip=self.entry.name))
        self.send_command(cmd='AVMT', opts='10', priority=True)
        self.status_timer_add('AVMT', self.get_av_mute_status)
        self.poll_loop()

    def status_timer_add(self, cmd, callback):
        """
        Add a callback to the status timer.

        :param cmd: PJLink command associated with callback
        :param callback: Method to call
        """
        if cmd in self.status_timer_checks:
            log.warning('({ip}) "{cmd}" already in checks - returning'.format(ip=self.entry.name, cmd=cmd))
            return
        log.debug('({ip}) Adding "{cmd}" callback for status timer'.format(ip=self.entry.name, cmd=cmd))
        self.status_timer_checks[cmd] = callback
        if not self.status_timer.isActive():
            self.status_timer.start()

    def status_timer_delete(self, cmd):
        """
        Delete a callback from the status timer.

        :param cmd: PJLink command associated with callback
        :param callback: Method to call
        """
        if cmd not in self.status_timer_checks:
            log.warning('({ip}) "{cmd}" not listed in status timer - returning'.format(ip=self.entry.name, cmd=cmd))
            return
        log.debug('({ip}) Removing "{cmd}" from status timer'.format(ip=self.entry.name, cmd=cmd))
        self.status_timer_checks.pop(cmd)
        if not self.status_timer_checks:
            self.status_timer.stop()

    def status_timer_update(self):
        """
        Call methods defined in status_timer_checks for updates
        """
        if not self.status_timer_checks:
            log.warning('({ip}) status_timer_update() called when no callbacks - '
                        'Race condition?'.format(ip=self.entry.name))
            self.status_timer.stop()
            return
        for cmd, callback in self.status_timer_checks.items():
            log.debug('({ip}) Status update call for {cmd}'.format(ip=self.entry.name, cmd=cmd))
            callback(priority=True)

    def receive_data_signal(self):
        """
        Clear any busy flags and send data received signal
        """
        self.send_busy = False
        self.projectorReceivedData.emit()
        return
