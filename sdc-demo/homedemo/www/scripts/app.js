(function (document) {
  'use strict';

  var app = document.querySelector('#app');
  app.is_calibrating = false;
  app.started_calibration = false;
  app.calibrationPos = 0;
  app.current_room = 'space';
  app.availables_room = ['earth', 'space', 'gallifrey', 'skaro'];
  app.current_room_index = 0;
  app.current_sphero = 'None';
  app.spheros = [app.current_sphero];
  app.current_sphero_index = 0;

  app.facedetection_enabled = false;
  app.speechrecognition_enabled = false;

  // imports are loaded and elements have been registered
  window.addEventListener('WebComponentsReady', function () {

    /* calibration button */
    var calibrationButton = document.querySelector('#calibrationButton');
    calibrationButton.addEventListener('click', calibrationToggle);
    function calibrationToggle() {
      if (!calibrationButton.active) {
        // reset new 0 as 0
        app.calibrationPos = 0;
      } else {
        app.started_calibration = true;
      }

      var msg = { topic: 'calibrationstate', content: calibrationButton.active };
      websocket.send(JSON.stringify(msg));

      refreshCalibrationMessage();
    }

    function refreshCalibrationMessage() {
      if (calibrationButton.active) {
        app.calibrationMessage = 'End calibration';
        calibrationSlider.disabled = !app.started_calibration;
      } else {
        app.calibrationMessage = 'Start calibration';
        calibrationSlider.disabled = false;
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

      var msg = { topic: 'recenter', content: calibrationSlider.immediateValue };
      websocket.send(JSON.stringify(msg));
    }

    /* move current location */
    var moveSpheroButton = document.querySelector('#move-sphero');
    moveSpheroButton.addEventListener('iron-select', function () {
      // don't do anything for noop (can be triggered when external elements change it)
      if (app.current_room === moveSpheroButton.selectedItemLabel) {
        return;
      }

      var msg = { topic: 'move', content: moveSpheroButton.selectedItemLabel };
      websocket.send(JSON.stringify(msg));
    });

    /* manually set current location */
    var manualResetSpheroButton = document.querySelector('#manualreset-sphero');
    manualResetSpheroButton.addEventListener('iron-select', function () {
      // don't do anything for noop (can be triggered when external elements change it)
      if (app.current_room === manualResetSpheroButton.selectedItemLabel) {
        return;
      }

      var msg = { topic: 'manualmove', content: manualResetSpheroButton.selectedItemLabel };
      websocket.send(JSON.stringify(msg));
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

    /* change default sphero */
    var defaultSpheroMenu = document.querySelector('#change-default-sphero');
    defaultSpheroMenu.addEventListener('iron-select', function () {
      // don't do anything for noop (can be triggered when external elements change it)
      if (app.current_sphero === defaultSpheroMenu.selectedItemLabel) {
        return;
      }

      var msg = { topic: 'changesphero', content: defaultSpheroMenu.selectedItemLabel };
      websocket.send(JSON.stringify(msg));
    });

    /* quit server */
    document.querySelector('#restartButton').addEventListener('click', function () {
       var msg = { topic: 'quit', content: '' };
       websocket.send(JSON.stringify(msg));
     });

    // only here get the websocket status back and toggle values if needed
    var websocket = new ReconnectingWebSocket('ws://' + window.location.hostname + ':8002/');
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
      console.log('Message received: ' + e.data);
      var message = JSON.parse(e.data);
      switch (message.topic) {
        case 'roomslist':
          app.availables_room = message.content;
          app.current_room_index = -1; // force a reindex
          app.current_room_index = app.availables_room.indexOf(app.current_room);
          break;
        case 'currentroom':
          app.current_room = message.content;
          app.current_room_index = -1; // force a reindex
          app.current_room_index = app.availables_room.indexOf(app.current_room);
          break;
        case 'calibrationstate':
          // if we didn't initiate the calibration, turn it to false
          if (!app.is_calibrating) {
            app.started_calibration = false;
          }
          app.is_calibrating = message.content;
          refreshCalibrationMessage();
          break;
        case 'facedetectionstate':
          app.facedetection_enabled = message.content;
          break;
        case 'speechrecognitionstate':
          app.speechrecognition_enabled = message.content;
          break;
        case 'spheroinfo':
          app.spheros = message.content.spheros;
          app.current_sphero = message.content.current;
          app.current_sphero_index = -1;  // force a reindex
          app.current_sphero_index = app.spheros.indexOf(app.current_sphero);
          console.log(app.current_sphero_index);
          break;
        default:
          console.log('Unknown message');
      }
    };

  });

})(document);
