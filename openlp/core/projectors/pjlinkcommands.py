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
The :mod:`openlp.core.lib.projector.pjlinkcmmands` module provides the necessary functions for
processing projector replies.

NOTE: PJLink Class (version) checks are handled in the respective PJLink/PJLinkUDP classes.
      process_clss is the only exception.

NOTE: Some commands are both commannd replies as well as UDP terminal-initiated status
      messages.

      Ex: POWR

      CLSS1 (TCP): controller  sends "POWR x", projector replies "POWR=xxxxx"
      CLSS2 (UDP): projector sends "POWER=xxxx"

      Inn both instances, the messagege is processed the same.

      For CLSS1, we initiate communication, so we know which projecttor instance
      the message is routed to.

      For CLSS2, the terminal initiates communication, so as part of the UDP process
      we must find the projector that initiated the message.
"""

import logging
import re
import string

from openlp.core.common.registry import Registry

from openlp.core.projectors.constants import E_AUTHENTICATION, PJLINK_DEFAULT_CODES, PJLINK_ERRORS, \
    PJLINK_ERST_DATA, PJLINK_ERST_LIST, PJLINK_ERST_STATUS, PJLINK_POWR_STATUS, PJLINK_TOKEN_SIZE, \
    E_NO_AUTHENTICATION, S_AUTHENTICATE, S_CONNECT, S_DATA_OK, S_OFF, S_OK, S_ON, S_STANDBY, STATUS_MSG

log = logging.getLogger(__name__)
log.debug('Loading pjlinkcommands')

__all__ = ['process_command']


# This should be the only function that's imported.
def process_command(projector, cmd, data):
    """
    Verifies any return error code. Calls the appropriate command handler.

    :param projector: Projector instance
    :param cmd: Command to process
    :param data: Data being processed
    """
    log.debug(f'({projector.entry.name}) Processing command "{cmd}" with data "{data}"')
    # cmd should already be in uppercase, but data may be in mixed-case.
    # Due to some replies should stay as mixed-case, validate using separate uppercase check
    _data = data.upper()
    # Check if we have a future command not available yet
    if cmd not in pjlink_functions:
        log.warning(f'({projector.entry.name}) Unable to process command="{cmd}" (Future option?)')
        return
    elif _data == 'OK':
        log.debug(f'({projector.entry.name}) Command "{cmd}" returned OK')
        # A command returned successfully, so do a query on command to verify status
        return S_DATA_OK

    elif _data in PJLINK_ERRORS:
        # Oops - projector error
        log.error(f'({projector.entry.name}) {cmd}: {STATUS_MSG[PJLINK_ERRORS[_data]]}')
        return PJLINK_ERRORS[_data]

    # Command checks already passed
    log.debug(f'({projector.entry.name}) Calling function for {cmd}')
    return pjlink_functions[cmd](projector=projector, data=data)


def process_ackn(projector, data):
    """
    Process the ACKN command.

    UDP reply to SRCH command

    :param projector: Projector instance
    :param data: Data in packet
    """
    # TODO: Have to rethink this one
    pass


def process_avmt(projector, data):
    """
    Process shutter and speaker status. See PJLink specification for format.
    Update projector.mute (audio) and projector.shutter (video shutter).
    10 = Shutter open, audio unchanged
    11 = Shutter closed, audio unchanged
    20 = Shutter unchanged, Audio normal
    21 = Shutter unchanged, Audio muted
    30 = Shutter open, audio muted
    31 = Shutter closed,  audio normal

    :param projector: Projector instance
    :param data: Shutter and audio status
    """
    settings = {'10': {'shutter': False, 'mute': projector.mute},
                '11': {'shutter': True, 'mute': projector.mute},
                '20': {'shutter': projector.shutter, 'mute': False},
                '21': {'shutter': projector.shutter, 'mute': True},
                '30': {'shutter': False, 'mute': False},
                '31': {'shutter': True, 'mute': True}
                }
    if data not in settings:
        log.warning('({ip}) Invalid av mute response: {data}'.format(ip=projector.entry.name, data=data))
        return
    shutter = settings[data]['shutter']
    mute = settings[data]['mute']
    # Check if we need to update the icons
    update_icons = (shutter != projector.shutter) or (mute != projector.mute)
    if update_icons:
        if projector.shutter != shutter:
            projector.shutter = shutter
            log.debug('({ip}) Setting shutter to {chk}'.format(ip=projector.entry.name,
                                                               chk='closed' if shutter else 'open'))
        if projector.mute != mute:
            projector.mute = mute
            log.debug('({ip}) Setting speaker to {chk}'.format(ip=projector.entry.name,
                                                               chk='muted' if shutter else 'normal'))
        if 'AVMT' in projector.status_timer_checks:
            projector.status_timer_delete('AVMT')
        projector.projectorUpdateIcons.emit()
    return


def process_clss(projector, data):
    """
    PJLink class that this projector supports. See PJLink specification for format.
    Updates projector.class.

    :param projector: Projector instance
    :param data: Class that projector supports.
    """
    # bug 1550891: Projector returns non-standard class response:
    #            : Expected: '%1CLSS=1'
    #            : Received: '%1CLSS=Class 1'  (Optoma)
    #            : Received: '%1CLSS=Version1'  (BenQ)
    if len(data) > 1:
        log.warning(f'({projector.entry.name}) Non-standard CLSS reply: "{data}"')
        # Due to stupid projectors not following standards (Optoma, BenQ comes to mind),
        # AND the different responses that can be received, the semi-permanent way to
        # fix the class reply is to just remove all non-digit characters.
        chk = re.findall(r'\d', data)
        if len(chk) < 1:
            log.warning(f'({projector.entry.name}) No numbers found in class version reply '
                        f'"{data}" - defaulting to class "1"')
            clss = '1'
        else:
            clss = chk[0]  # Should only be the first match
    elif not data.isdigit():
        log.warning(f'({projector.entry.name}) NAN CLSS version reply '
                    f'"{data}" - defaulting to class "1"')
        clss = '1'
    else:
        clss = data
    projector.pjlink_class = clss
    log.debug(f'({projector.entry.name}) Setting pjlink_class for this projector to "{projector.pjlink_class}"')
    if projector.no_poll:
        return

    # Since we call this one on first connect, setup polling from here
    log.debug(f'({projector.entry.name}) process_pjlink(): Starting timer')
    projector.poll_timer.setInterval(1000)  # Set 1 second for initial information
    projector.poll_timer.start()
    return


def process_erst(projector, data):
    """
    Error status. See PJLink Specifications for format.
    Updates projector.projector_errors

    :param projector: Projector instance
    :param data: Error status
    """
    if len(data) != PJLINK_ERST_DATA['DATA_LENGTH']:
        count = PJLINK_ERST_DATA['DATA_LENGTH']
        log.warning('({ip}) Invalid error status response "{data}": length != {count}'.format(ip=projector.entry.name,
                                                                                              data=data,
                                                                                              count=count))
        return
    if not data.isnumeric():
        # Bad data - ignore
        log.warning('({ip}) Invalid error status response "{data}"'.format(ip=projector.entry.name, data=data))
        return
    if int(data) == 0:
        projector.projector_errors = None
        # No errors
        return
    # We have some sort of status error, so check out what it/they are
    projector.projector_errors = {}
    fan, lamp, temp, cover, filt, other = (data[PJLINK_ERST_DATA['FAN']],
                                           data[PJLINK_ERST_DATA['LAMP']],
                                           data[PJLINK_ERST_DATA['TEMP']],
                                           data[PJLINK_ERST_DATA['COVER']],
                                           data[PJLINK_ERST_DATA['FILTER']],
                                           data[PJLINK_ERST_DATA['OTHER']])
    if fan != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['FAN']] = PJLINK_ERST_STATUS[fan]
    if lamp != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['LAMP']] = PJLINK_ERST_STATUS[lamp]
    if temp != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['TEMP']] = PJLINK_ERST_STATUS[temp]
    if cover != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['COVER']] = PJLINK_ERST_STATUS[cover]
    if filt != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['FILTER']] = PJLINK_ERST_STATUS[filt]
    if other != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['OTHER']] = PJLINK_ERST_STATUS[other]
    return


def process_inf1(projector, data):
    """
    Manufacturer name set in projector.
    Updates projector.manufacturer

    :param projector: Projector instance
    :param data: Projector manufacturer
    """
    projector.manufacturer = data
    log.debug('({ip}) Setting projector manufacturer data to "{data}"'.format(ip=projector.entry.name,
                                                                              data=projector.manufacturer))
    return


def process_inf2(projector, data):
    """
    Projector Model set in projector.
    Updates projector.model.

    :param projector: Projector instance
    :param data: Model name
    """
    projector.model = data
    log.debug('({ip}) Setting projector model to "{data}"'.format(ip=projector.entry.name, data=projector.model))
    return


def process_info(projector, data):
    """
    Any extra info set in projector.
    Updates projector.other_info.

    :param projector: Projector instance
    :param data: Projector other info
    """
    projector.other_info = data
    log.debug('({ip}) Setting projector other_info to "{data}"'.format(ip=projector.entry.name,
                                                                       data=projector.other_info))
    return


def process_inpt(projector, data):
    """
    Current source input selected. See PJLink specification for format.
    Update projector.source

    :param projector: Projector instance
    :param data: Currently selected source
    """
    # First, see if we have a valid input based on what is installed (if available)
    if projector.source_available is not None:
        # We have available inputs, so verify it's in the list
        if data not in projector.source_available:
            log.warning('({ip}) Input source not listed in available sources - '
                        'ignoring'.format(ip=projector.entry.name))
            return
    elif data not in PJLINK_DEFAULT_CODES:
        # Hmm - no sources available yet, so check with PJLink defaults
        log.warning('({ip}) Input source not listed as a PJLink valid source '
                    '- ignoring'.format(ip=projector.entry.name))
        return
    projector.source = data
    log.debug('({ip}) Setting current source to "{data}"'.format(ip=projector.entry.name, data=projector.source))
    return


def process_inst(projector, data):
    """
    Available source inputs. See PJLink specification for format.
    Updates projector.source_available

    :param projector: Projector instance
    :param data: Sources list
    """
    sources = []
    check = data.split()
    for source in check:
        sources.append(source)
    sources.sort()
    projector.source_available = sources
    log.debug('({ip}) Setting projector source_available to "{data}"'.format(ip=projector.entry.name,
                                                                             data=projector.source_available))
    projector.projectorUpdateIcons.emit()
    return


def process_lamp(projector, data):
    """
    Lamp(s) status. See PJLink Specifications for format.
    Data may have more than 1 lamp to process.
    Update projector.lamp dictionary with lamp status.

    :param projector: Projector instance
    :param data: Lamp(s) status.
    """
    lamps = []
    lamp_list = data.split()
    if len(lamp_list) < 2:
        # Invalid data - not enough information
        log.warning('({ip}) process_lamp(): Invalid data "{data}" - '
                    'Missing data'.format(ip=projector.entry.name, data=data))
        return
    else:
        while lamp_list:
            if not lamp_list[0].isnumeric() or not lamp_list[1].isnumeric():
                # Invalid data - we'll ignore the rest for now
                log.warning('({ip}) process_lamp(): Invalid data "{data}"'.format(ip=projector.entry.name, data=data))
                return
            fill = {'Hours': int(lamp_list[0]), 'On': False if lamp_list[1] == '0' else True}
            lamps.append(fill)
            lamp_list.pop(0)  # Remove lamp hours
            lamp_list.pop(0)  # Remove lamp on/off
    projector.lamp = lamps
    return


def process_lkup(projector, data):
    """
    Process UDP request indicating remote is available for connection

    :param projector: Projector instance
    :param data: Data packet from remote
    """
    log.debug('({ip}) Processing LKUP command'.format(ip=projector.entry.name))
    if Registry().get('settings').value('projector/connect when LKUP received'):
        projector.connect_to_host()


def process_name(projector, data):
    """
    Projector name set in projector.
    Updates projector.pjlink_name

    :param projector: Projector instance
    :param data: Projector name
    """
    projector.pjlink_name = data
    log.debug('({ip}) Setting projector PJLink name to "{data}"'.format(ip=projector.entry.name,
                                                                        data=projector.pjlink_name))
    return


def process_pjlink(projector, data):
    """
    Process initial socket connection to terminal.

    :param projector: Projector instance
    :param data: Initial packet with authentication scheme
    """
    log.debug('({ip}) Processing PJLINK command'.format(ip=projector.entry.name))
    chk = data.split(' ')
    if len(chk[0]) != 1:
        # Invalid - after splitting, first field should be 1 character, either '0' or '1' only
        log.error('({ip}) Invalid initial authentication scheme - aborting'.format(ip=projector.entry.name))
        return E_AUTHENTICATION
    elif chk[0] == '0':
        # Normal connection no authentication
        if len(chk) > 1:
            # Invalid data - there should be nothing after a normal authentication scheme
            log.error('({ip}) Normal connection with extra information - aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        elif projector.pin:
            log.error('({ip}) Normal connection but PIN set - aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        log.debug('({ip}) PJLINK: Returning S_CONNECT'.format(ip=projector.entry.name))
        return S_CONNECT
    elif chk[0] == '1':
        if len(chk) < 2:
            # Not enough information for authenticated connection
            log.error('({ip}) Authenticated connection but not enough info - aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        elif len(chk[-1]) != PJLINK_TOKEN_SIZE:
            # Bad token - incorrect size
            log.error('({ip}) Authentication token invalid (size) - aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        elif not all(c in string.hexdigits for c in chk[-1]):
            # Bad token - not hexadecimal
            log.error('({ip}) Authentication token invalid (not a hexadecimal number) '
                      '- aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        elif not projector.pin:
            log.error('({ip}) Authenticate connection but no PIN - aborting'.format(ip=projector.entry.name))
            return E_NO_AUTHENTICATION
        log.debug('({ip}) PJLINK: Returning S_AUTHENTICATE'.format(ip=projector.entry.name))
        return S_AUTHENTICATE


def process_powr(projector, data):
    """
    Power status. See PJLink specification for format.
    Update projector.power with status. Update icons if change from previous setting.

    :param projector: Projector instance
    :param data: Power status
    """
    log.debug('({ip}) Processing POWR command'.format(ip=projector.entry.name))
    if data not in PJLINK_POWR_STATUS:
        # Log unknown status response
        log.warning('({ip}) Unknown power response: "{data}"'.format(ip=projector.entry.name, data=data))
        return

    power = PJLINK_POWR_STATUS[data]
    update_icons = projector.power != power
    if update_icons:
        projector.power = power
        projector.change_status(PJLINK_POWR_STATUS[data])
        projector.projectorUpdateIcons.emit()
        if power == S_ON:
            # Input sources list should only be available after power on, so update here
            projector.send_command('INST')

    if projector.power in [S_ON, S_STANDBY, S_OFF] and 'POWR' in projector.status_timer_checks:
        projector.status_timer_delete(cmd='POWR')
    return


def process_rfil(projector, data):
    """
    Process replacement filter type

    :param projector: Projector instance
    :param data: Filter replacement model number
    """
    if projector.model_filter is None:
        projector.model_filter = data
    else:
        log.warning('({ip}) Filter model already set'.format(ip=projector.entry.name))
        log.warning('({ip}) Saved model: "{old}"'.format(ip=projector.entry.name, old=projector.model_filter))
        log.warning('({ip}) New model: "{new}"'.format(ip=projector.entry.name, new=data))


def process_rlmp(projector, data):
    """
    Process replacement lamp type

    :param projector: Projector instance
    :param data: Lamp replacement model number
    """
    if projector.model_lamp is None:
        projector.model_lamp = data
    else:
        log.warning('({ip}) Lamp model already set'.format(ip=projector.entry.name))
        log.warning('({ip}) Saved lamp: "{old}"'.format(ip=projector.entry.name, old=projector.model_lamp))
        log.warning('({ip}) New lamp: "{new}"'.format(ip=projector.entry.name, new=data))


def process_snum(projector, data):
    """
    Serial number of projector.

    :param projector: Projector instance
    :param data: Serial number from projector.
    """
    if projector.serial_no is None:
        log.debug('({ip}) Setting projector serial number to "{data}"'.format(ip=projector.entry.name, data=data))
        projector.serial_no = data
        projector.db_update = False
        return

    # Compare serial numbers and see if we got the same projector
    if projector.serial_no != data:
        log.warning('({ip}) Projector serial number does not match saved serial '
                    'number'.format(ip=projector.entry.name))
        log.warning('({ip}) Saved:    "{old}"'.format(ip=projector.entry.name, old=projector.serial_no))
        log.warning('({ip}) Received: "{new}"'.format(ip=projector.entry.name, new=data))
        log.warning('({ip}) NOT saving serial number'.format(ip=projector.entry.name))
        projector.serial_no_received = data


def process_srch(projector=None, data=None):
    """
    Process the SRCH command.

    SRCH is processed by terminals so we ignore any packet.

    UDP command to find active CLSS 2 projectors. Reply is ACKN.

    :param projector: Projector instance (actually ignored for this command)
    :param data: Data in packet
    """
    if projector is None:
        log.warning('SRCH packet detected - ignoring')
    else:
        log.warning(f'({projector.entry.name}) SRCH packet detected - ignoring')
    return


def process_sver(projector, data):
    """
    Software version of projector

    :param projector: Projector instance
    :param data: Software version of projector
    """
    if len(data) > 32:
        # Defined in specs max version is 32 characters
        log.warning('Invalid software version - too long')
        return
    if projector.sw_version is not None:
        if projector.sw_version == data:
            log.debug('({ip}) Software version same as saved version - returning'.format(ip=projector.entry.name))
            return
        log.warning('({ip}) Projector software version does not match saved '
                    'software version'.format(ip=projector.entry.name))
        log.warning('({ip}) Saved:    "{old}"'.format(ip=projector.entry.name, old=projector.sw_version))
        log.warning('({ip}) Received: "{new}"'.format(ip=projector.entry.name, new=data))
        log.warning('({ip}) Updating software version'.format(ip=projector.entry.name))

    log.debug('({ip}) Setting projector software version to "{data}"'.format(ip=projector.entry.name, data=data))
    projector.sw_version = data
    projector.db_update = True


# Map command to function.
pjlink_functions = {
    'ACKN': process_ackn,  # Class 2 (command is SRCH)
    'AVMT': process_avmt,
    'CLSS': process_clss,
    'ERST': process_erst,
    'INFO': process_info,
    'INF1': process_inf1,
    'INF2': process_inf2,
    'INPT': process_inpt,
    'INST': process_inst,
    'LAMP': process_lamp,
    'LKUP': process_lkup,  # Class 2  (terminal request only - no cmd)
    'NAME': process_name,
    'PJLINK': process_pjlink,
    'POWR': process_powr,
    'SNUM': process_snum,
    'SRCH': process_srch,   # Class 2 (reply is ACKN)
    'SVER': process_sver,
    'RFIL': process_rfil,
    'RLMP': process_rlmp
}
