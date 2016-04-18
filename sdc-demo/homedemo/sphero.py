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

import logging
import os
import sys
from mock import Mock

from home import get_home
from tools import MainLoop

# enable importing kulka as if it was an external module
sys.path.insert(0, os.path.dirname(__file__))
import kulka

_sphero = None
logger = logging.getLogger(__name__)


class Sphero:

    default_sphero_color = (0, 0, 255)

    def __init__(self, without_sphero=False):
        if not without_sphero:
            logger.debug("Connecting to sphero")
            sphero_hw = "sphero.hw"
            try:
                self.sphero = kulka.Kulka(open(sphero_hw).read().strip())
            except IOError:
                logger.error("Couldn't connect to sphero: {} doesn't exist".format(sphero_hw))
                sys.exit(1)
            logger.debug("Connected to sphero")
            self.sphero.set_inactivity_timeout(3600)
            self.sphero.set_rgb(*self.default_sphero_color)
        else:
            logger.info("Using a false sphero")
            self.sphero = Mock()
        self.current_room = get_home().start_room

    @MainLoop.in_mainloop_thread
    def start_calibration(self):
        self.sphero.set_back_led(255)
        self.sphero.set_rgb(0, 0, 0)

    @MainLoop.in_mainloop_thread
    def recenter(self, angle):
        self.sphero.setheading(1)
        self.sphero.move(0, angle)
        self.sphero.setheading(0)

    @MainLoop.in_mainloop_thread
    def end_calibration(self):
        self.sphero.set_rgb(*default_sphero_color)
        self.sphero.set_back_led(0)

    @MainLoop.in_mainloop_thread
    def sleep(self):
        self.sphero.sleep()


def get_sphero(without_sphero=False):
    """Get sphero singleton"""
    global _sphero
    if not _sphero:
        _sphero = Sphero(without_sphero=without_sphero)
    return _sphero
