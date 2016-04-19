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

import argparse
import logging
from gi.repository import GLib
import os
import sys
from tools import MainLoop

from facedetection import detect_face
from servers import StaticServer, CommandSocketServer
from sphero import Sphero

logger = logging.getLogger(__name__)
_default_log_level = logging.WARNING


def _setup_logging(env_key='LOG_CFG', level=_default_log_level):
    """Setup logging configuration

    Order of preference:
    - manually define level
    - env_key env variable if set (logging config file)
    - fallback to _default_log_level
    """
    path = os.getenv(env_key, '')
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    if level == _default_log_level:
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = yaml.load(f.read())
            logging.config.dictConfig(config)
    logging.info("Logging level set to {}".format(logging.getLevelName(logging.root.getEffectiveLevel())))


def set_logging_from_args(args, parser):
    """Choose logging ignoring any unknown sys.argv options"""
    result_verbosity_arg = []
    for arg in args:
        if arg.startswith("-v"):
            for char in arg:
                if char not in ['-', 'v']:
                    break
            else:
                result_verbosity_arg.append(arg)
    args = parser.parse_args(result_verbosity_arg)

    # setup logging level if set by the command line
    if args.verbose == 1:
        _setup_logging(level=logging.INFO)
    elif args.verbose > 1:
        _setup_logging(level=logging.DEBUG)
    else:
        _setup_logging()


def main():
    mainloop = MainLoop()

    parser = argparse.ArgumentParser(description="Home demo gateway with robot")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output verbosity (2 levels)")
    parser.add_argument("--without-sphero", action="store_true", help="Use a mock sphero instead of a real one")
    parser.add_argument("--no-facedetection", action="store_true", help="Disable face detection feature")

    # set logging level
    set_logging_from_args(sys.argv, parser)
    args = parser.parse_args()

    # connect to sphero and set it at starting position
    sphero = Sphero(without_sphero=args.without_sphero)

    # start servers
    StaticServer().start()
    CommandSocketServer().start()

    # detect faces every 3 seconds
    if not args.no_facedetection:
        GLib.timeout_add_seconds(3, detect_face)

    sphero.move_to("livingroom")
    sphero.move_to("entrance")
    sphero.move_to("kitchen")
    sphero.move_to("livingroom")

    mainloop.run()
