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
from time import time
import cv2

from home import Home
from servers import WebClientsCommands
from sphero import Sphero
from tools import Singleton

logger = logging.getLogger(__name__)


class FaceDetection(object):
    """The home owner of all rooms and directions of a house"""
    __metaclass__ = Singleton

    # Create the filter cascade
    faceCascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), '..', 'logic.xml'))

    INACTIVITY_PERIOD = 30
    FACE_DETECTION_INTERNAL = 3

    def __init__(self):
        """Create this Face Detection object"""
        self._source_id = None
        self._enabled = False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._enabled:
            logger.info("Enabling face detection feature")
            self._source_id = GLib.timeout_add_seconds(self.FACE_DETECTION_INTERNAL, self.detect_face)
        else:
            logger.info("Disabling face detection feature")
            if self._source_id:
                GLib.source_remove(self._source_id)
            self._source_id = None
        self._last_detected_face = time()
        WebClientsCommands.sendFaceDetectionStateAll()

    def detect_face(self):
        # Read the image
        video_capture = cv2.VideoCapture(0)
        ret, image = video_capture.read()
        video_capture.release()

        # Detect faces in the image
        faces = self.faceCascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        face_detected = False
        if len(faces) > 0:
            self._last_detected_face = time()
            face_detected = True
        sphero = Sphero()
        if sphero.current_room == Home().start_room and face_detected:
            logger.info("Face recognized and sphero in ketten, moving to welcome guest")
            sphero.move_to(Home().facedetectdest_room.name)
        # if no activity for a long time and no face either, put the sphero back to the ketten
        elif (not face_detected and sphero.current_room == Home().facedetectdest_room and
              (time() - self._last_detected_face) > self.INACTIVITY_PERIOD and
              (time() - sphero.last_move) > self.INACTIVITY_PERIOD):
            logger.info("No activity or face showing up for a long time, going back to ketten")
            sphero.move_to(Home().start_room.name)

        return True
