(function (document) {
  'use strict';

  var app = document.querySelector('#app');
  app.is_calibrating = false;
  app.calibrationPos = 0;
  var _lastCalibrationPosSent = 0;
  app.current_room = 'space';
  app.availables_room = ['earth', 'space', 'gallifrey', 'skaro'];
  app.current_room_index = 0;

  app.facedetection_enabled = false;
  app.speechrecognition_enabled = false;

  // imports are loaded and elements have been registered
  window.addEventListener('WebComponentsReady', function () {

    /* calibration button */
    var calibrationButton = document.querySelector('#calibrationButton');
    calibrationButton.addEventListener('click', calibrationToggle);
    function calibrationToggle() {
      if (calibrationButton.active) {

        // TODO: send calibration message
      } else {
        // reset new 0 as 0
        app.calibrationPos = 0;
        _lastCalibrationPosSent = 0;

        // TODO: send end calibration message
      }

      refreshCalibrationMessage();
    }

    function refreshCalibrationMessage() {
      if (calibrationButton.active) {
        app.calibrationMessage = 'End calibration';
      } else {
        app.calibrationMessage = 'Start calibration';
      }
    }

    /* calibration slider */
    var calibrationSlider = document.querySelector('#calibrationSlider');
    calibrationSlider.addEventListener('immediate-value-change', valueChanged);
    calibrationSlider.addEventListener('value-change', valueChanged);

    function valueChanged() {
      // we just ended calibration and reset pos to 0
      if (!calibrationButton.active && app.calibrationPos === 0) {
        return;
      }

      // ensure we are in calibration mode
      if (!app.is_calibrating) {
        app.is_calibrating = true;
        calibrationToggle();
      }

      // send position over
      // calibrationSlider.immediateValue - _lastCalibrationPosSent
      _lastCalibrationPosSent = calibrationSlider.immediateValue;
    }

    /* move current location */
    var moveSpheroButton = document.querySelector('#move-sphero');
    moveSpheroButton.addEventListener('iron-select', function () {
      // don't do anything for noop (can be triggered when external elements change it)
      if (app.current_room === moveSpheroButton.selectedItemLabel) {
        return;
      }

      // TODO: send sphero move message
    });

    /* manually set current location */
    var manualResetSpheroButton = document.querySelector('#manualreset-sphero');
    manualResetSpheroButton.addEventListener('iron-select', function () {
      // don't do anything for noop (can be triggered when external elements change it)
      if (app.current_room === manualResetSpheroButton.selectedItemLabel) {
        return;
      }

      // TODO: send sphero manual set message
    });

    /* change face detection enablement */
    var faceDetectionSwitch = document.querySelector('#face-detection-toggle');
    faceDetectionSwitch.addEventListener('change', function () {
      var msg = { topic: 'facedetectionchange', content: faceDetectionSwitch.active };
      websocket.send(JSON.stringify(msg));
    });

    /* change speech recognition enablement */
    var speechRecogntionSwitch = document.querySelector('#speech-recognition-toggle');
    speechRecogntionSwitch.addEventListener('change', function () {
      var msg = { topic: 'speechrecognitionchange', content: speechRecogntionSwitch.active };
      websocket.send(JSON.stringify(msg));
    });

    // only here get the websocket status back and toggle values if needed
    var websocket = new WebSocket('ws://' + window.location.hostname + ':8002/');
    websocket.onopen = function () {
      console.log('websocket connected');
    };

    websocket.onclose = function () {
      console.log('websocket disconnected');
    };

    websocket.onerror = function (e) {
      console.log('Error in websocket: ' + e.data);
    };

    websocket.onmessage = function (e) {
      console.log('Message: ' + e.data);
      var message = JSON.parse(e.data);
      switch (message.topic) {
        case 'roomslist':
          app.availables_room = message.content;
          app.current_room_index = app.availables_room.indexOf(app.current_room);
          break;
        case 'currentroom':
          app.current_room = message.content;
          app.current_room_index = app.availables_room.indexOf(app.current_room);
          break;
        case 'calibrationstate':
          app.is_calibrating = message.content;
          refreshCalibrationMessage();
          break;
        case 'facedetectionstate':
          app.facedetection_enabled = message.content;
          break;
        case 'speechrecognitionstate':
          app.speechrecognition_enabled = message.content;
          break;
        default:
          console.log('Unknown message');
      }
    };

    // TODO: receive message from client (and below should be in client callback)


  });

})(document);
