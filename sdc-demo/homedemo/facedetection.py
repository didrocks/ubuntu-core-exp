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
from time import time
import cv2

from home import Home
from sphero import Sphero

logger = logging.getLogger(__name__)

# Create the filter cascade
faceCascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), '..', 'logic.xml'))

INACTIVITY_PERIOD = 30

_last_detected_face = None

def detect_face():
    # Read the image
    video_capture = cv2.VideoCapture(0)
    ret, image = video_capture.read()

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    face_detected = False
    if len(faces) > 0:
        global _last_detected_face
        _last_detected_face = time()
        face_detected = True
    sphero = Sphero()
    if sphero.current_room == Home().start_room and face_detected:
        logger.info("Face recognized and sphero in ketten, moving to welcome guest")
        sphero.move_to(Home().facedetectdest_room.name)
    # if no activity for a long time and no face either, put the sphero back to the ketten
    elif (not face_detected and sphero.current_room == Home().facedetectdest_room
          and (time() - _last_detected_face) > INACTIVITY_PERIOD and (time() - sphero.last_move) > INACTIVITY_PERIOD):
        logger.info("No activity or face showing up for a long time, going back to ketten")
        sphero.move_to(Home().start_room.name)

    video_capture.release()

    return True
