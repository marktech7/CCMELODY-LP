# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
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
The :mod:`~openlp.core.ui.media` module contains classes and objects for media player integration.
"""
import logging

from PySide6.QtMultimedia import QMediaFormat

from openlp.core.common.platform import is_win
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__ + '.__init__')

# Audio and video extensions copied from 'include/vlc_interface.h' from vlc 2.2.0 source
AUDIO_EXT = ['*.3ga', '*.669', '*.a52', '*.aac', '*.ac3', '*.adt', '*.adts', '*.aif', '*.aifc', '*.aiff', '*.amr',
             '*.aob', '*.ape', '*.awb', '*.caf', '*.dts', '*.flac', '*.it', '*.kar', '*.m4a', '*.m4b', '*.m4p', '*.m5p',
             '*.mid', '*.mka', '*.mlp', '*.mod', '*.mpa', '*.mp1', '*.mp2', '*.mp3', '*.mpc', '*.mpga', '*.mus',
             '*.oga', '*.ogg', '*.oma', '*.opus', '*.qcp', '*.ra', '*.rmi', '*.s3m', '*.sid', '*.spx', '*.thd', '*.tta',
             '*.voc', '*.vqf', '*.w64', '*.wav', '*.wma', '*.wv', '*.xa', '*.xm']
VIDEO_EXT = ['*.3g2', '*.3gp', '*.3gp2', '*.3gpp', '*.amv', '*.asf', '*.avi', '*.bik', '*.divx', '*.drc', '*.dv',
             '*.f4v', '*.flv', '*.gvi', '*.gxf', '*.iso', '*.m1v', '*.m2v', '*.m2t', '*.m2ts', '*.m4v', '*.mkv',
             '*.mov', '*.mp2', '*.mp2v', '*.mp4', '*.mp4v', '*.mpe', '*.mpeg', '*.mpeg1', '*.mpeg2', '*.mpeg4', '*.mpg',
             '*.mpv2', '*.mts', '*.mtv', '*.mxf', '*.mxg', '*.nsv', '*.nuv', '*.ogg', '*.ogm', '*.ogv', '*.ogx', '*.ps',
             '*.rec', '*.rm', '*.rmvb', '*.rpl', '*.thp', '*.tod', '*.ts', '*.tts', '*.txd', '*.vob', '*.vro', '*.webm',
             '*.wm', '*.wmv', '*.wtv', '*.xesc', '*.nut', '*.rv', '*.xvid']

AVI = "video/x-msvideo"  # AVI

MP4 = 'video/mp4'


def get_supported_media_suffix():
    """
    Provide a list of suffixes the Media input dialog to use for selection
    """
    suffixes = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        suffixes += ['*.'+ s for s in mime_type.suffixes()]
    suffix_filter = []
    suffix_filter.append('Media files ({suffixes})'.format(suffixes=' '.join(suffixes)))
    suffix_filter.append('Any files (*)')
    return suffix_filter


def get_supported_mime_types():
    """
    Provide a list of Mime types for  the Media imput dialog to use for selection
    """
    mime_types = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        mime_types.append(mime_type.name())
        print(mime_type.suffixes())
    #if (is_win() and AVI not in mime_types):
    #    mime_types.append(AVI)
    #if MP4 not in mime_types:
    #    mime_types.append(MP4)
    # Add mimetype for all files (*.*)
    mime_types.append('; '.join(mime_types))
    mime_types.append('application/octet-stream')
    return mime_types


def validate_supported_mime_type(mime: str) -> bool:
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
        for m in mime_type.suffixes():
            print(m, mime)
            if mime in m:
                return True
    return False



class MediaState(object):
    """
    An enumeration for possible States of the Media Player
    """
    Off = 0
    Loaded = 1
    Playing = 2
    Paused = 3
    Stopped = 4


class MediaType(object):
    """
    An enumeration of possible Media Types
    """
    Unused = 0
    Audio = 1
    Video = 2
    Dual = 3
    DeviceStream = 4
    NetworkStream = 5


class MediaPlayItem(object):
    """
    This class hold the media related info
    """
    external_stream = []  # for remote things like USB Cameras
    audio_file = None  # for song Audio files when we have background videos
    media_file = None  # for standalone media
    is_background = False
    is_theme_background = False
    length = 0
    start_time = 0
    end_time = 0
    is_playing = MediaState.Off
    timer = 1000
    media_type = MediaType().Unused


def get_volume(controller) -> int:
    """
    The volume needs to be retrieved

    :param controller: the controller in use
    :return: Are we looping
    """
    if controller.is_live:
        return Registry().get('settings').value('media/live volume')
    else:
        return Registry().get('settings').value('media/preview volume')


def save_volume(controller, volume: int) -> None:
    """
    The volume needs to be saved

    :param controller: the controller in use
    :param volume: The volume to use and save
    :return: Are we looping
    """
    if controller.is_live:
        return Registry().get('settings').setValue('media/live volume', volume)
    else:
        return Registry().get('settings').setValue('media/preview volume', volume)


def saved_looping_playback(controller) -> bool:
    """
    :param controller: the controller in use
    :return: Are we looping
    """
    if controller.is_live:
        return Registry().get('settings').value('media/live loop')
    else:
        return Registry().get('settings').value('media/preview loop')


def toggle_looping_playback(controller) -> None:
    """

    :param controller: the controller in use
    :return: None
    """
    if controller.is_live:
        Registry().get('settings').setValue('media/live loop', not Registry().get('settings').value('media/live loop'))
    else:
        Registry().get('settings').setValue('media/preview loop',
                                            not Registry().get('settings').value('media/preview loop'))


def parse_stream_path(input_string):
    """
    Split the device stream path info.

    :param input_string: The string to parse
    :return: The elements extracted from the string:  type, streamname, MRL, VLC-options
    """
    log.debug('parse_stream_path, about to parse: "{text}"'.format(text=input_string))
    # identify header: 'devicestream:' or 'networkstream:'
    type_str, data = input_string.split(':', 1)
    if type_str == 'devicestream':
        stream_type = MediaType.DeviceStream
    else:
        stream_type = MediaType.NetworkStream
    # split at '&&'
    stream_info = data.split('&&')
    name = stream_info[0]
    mrl = stream_info[1]
    options = stream_info[2]
    return stream_type, name, mrl, options


def format_milliseconds(milliseconds):
    """
    Format milliseconds into a human readable time string.
    :param milliseconds: Milliseconds to format
    :return: Time string in format: hh:mm:ss,ttt
    """
    milliseconds = int(milliseconds)
    seconds, millis = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def format_play_time(milliseconds):
    """
    Format milliseconds into a human readable time string.
    :param milliseconds: Milliseconds to format
    :return: Time string in format: hh:mm:ss,ttt
    """
    milliseconds = int(milliseconds)
    seconds, _ = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    _, minutes = divmod(minutes, 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_play_seconds(seconds: float) -> str:
    """

    """
    secs, psec = divmod(seconds, 10)
    return f"{secs:01d}.{psec:01d}"


media_empty_song = [{"title": "", "text": "", "verse": 0, "footer": ""}]
