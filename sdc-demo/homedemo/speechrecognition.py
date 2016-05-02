# -*- coding: utf-8 -*-
# Copyright (C) 2016 Canonical
#
# Authors:
#  Didier Roche
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gi.repository import GLib
import logging
import os

from servers import WebClientsCommands
from sphero import Sphero
from tools import Singleton, suppress, get_data_path

logger = logging.getLogger(__name__)


class SpeechRecognition(object):
    """We are reading a file for now on speech recognition"""
    __metaclass__ = Singleton

    def __init__(self):
        """Create this Speech recognition object"""
        self._source_id = None
        self._enabled = False
        self.speech_recognition_file_path = os.path.join(get_data_path(), "speech.recognition")
        GLib.timeout_add_seconds(0.1, self.check_speech_recognition)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._enabled:
            logger.info("Enabling speech recognition feature")
        else:
            logger.info("Disabling speech recognition feature")
        WebClientsCommands.sendSpeechRecognitionStateAll()

    def check_speech_recognition(self):
        # Read file on disk
        with suppress(IOError):
            # we want to always remove the speech recognition file, even if enabled
            if self.enabled and Sphero().current_room.speech_recognition:
                with open(self.speech_recognition_file_path) as f:
                    action_name = f.read().strip()
                    dest_room = None
                    # for now, redo a mapping between actions and room name (FIXME, get all events names as config)
                    if action_name == "turn_on_the_light" or action_name == "turn_the_light_off":
                        dest_room = "bedroom"
                    elif (action_name == "turn_on_the_air_conditioning" or
                          action_name == "turn_the_air_conditioning_off"):
                        dest_room = "livingroom"
                    elif action_name == "open_garage_door" or action_name == "close_garage":
                        dest_room = "garage"
                    elif action_name == "kitchen_turn_on_light" or action_name == "kitchen_turn_the_light_off":
                        dest_room = "kitchen"
                    else:
                        logger.info("Unrecognized speech event")

                    if dest_room:
                        Sphero().move_to(dest_room)
            self.clean_speech_recognition_state()

        return True

    def clean_speech_recognition_state(self):
        with suppress(OSError):
            os.remove(self.speech_recognition_file_path)
