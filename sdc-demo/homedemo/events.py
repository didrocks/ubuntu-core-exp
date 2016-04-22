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
import subprocess
import threading
from time import sleep

logger = logging.getLogger(__name__)
_airconditioner_thread = None


def aircondition(sphero):
    """Simulate air conditioner on/off"""
    logger.info("Play a sound putting the air conditioner on and off")
    global _airconditioner_thread
    if not _airconditioner_thread:
        _airconditioner_thread = AirConditioner()
        _airconditioner_thread.start()
    else:
        _airconditioner_thread.stop()
        _airconditioner_thread = None
    sleep(3)


def garagedoor(sphero):
    """Simulating opening the garage door"""
    logger.info("Open gare door")
    current_angle = 0
    num_steps = 40
    # make 2 loops
    rotate_by = 360 * 2 / num_steps
    for _ in range(num_steps + 1):
        current_angle = (current_angle + rotate_by) % 360
        print(current_angle)
        _make_a_step(sphero, current_angle, 0, 0.3)


def switchlight(sphero):
    """simulate light switch on"""
    logger.info("Light switch on (on sphero)")
    for i in range(255):
        sphero.set_rgb(i, i, i)
        sleep(0.005)
    sleep(3)
    sphero._reset_default_color()


class AirConditioner(threading.Thread):
    """Play an air conditioner sound"""

    def __init__(self, *args, **kwargs):
        super(AirConditioner, self).__init__(*args, **kwargs)
        self.stopped = False

    def run(self):
        """Start playing the wav file in a separate thread"""
        conditioner_sound_file = os.path.join(os.path.dirname(__file__), "airconditioner.wav")
        while(not self.stopped):
            subprocess.call(["aplay", conditioner_sound_file])

    def stop(self):
        """Stop the running air conditioner"""
        self.stopped = True
        subprocess.call(["pkill", "aplay"])


def _make_a_step(sphero, current_angle, speed, step_time):
    sphero.roll(speed, current_angle)
    sleep(step_time)
    sphero.roll(0, current_angle)
