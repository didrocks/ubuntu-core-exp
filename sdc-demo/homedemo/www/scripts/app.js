(function (document) {
  'use strict';

  var app = document.querySelector('#app');
  app.is_calibrating = false;
  app.calibrationPos = 0;
  var _lastCalibrationPosSent = 0;
  app.current_room = 'space';
  app.availables_room = ['earth', 'space', 'gallifrey', 'skaro'];
  app.current_room_index = 0;

  // imports are loaded and elements have been registered
  window.addEventListener('WebComponentsReady', function () {

    /* calibration button */
    var calibrationButton = document.querySelector('#calibrationButton');
    calibrationButton.addEventListener('click', calibrationToggle);
    function calibrationToggle(_) {
      if (calibrationButton.active) {
        app.calibrationMessage = 'End calibration';

        // TODO: send calibration message
      } else {
        // reset new 0 as 0
        app.calibrationPos = 0;
        _lastCalibrationPosSent = 0;
        app.calibrationMessage = 'Start calibration';

        // TODO: send end calibration message
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

    // only here get the websocket status back and toggle values if needed
    //var socket = new WebSocket("ws://" + window.location.hostname + ":8002/");

    // TODO: receive message from client (and below should be in client callback)

    // initiate calibration toggle label
    calibrationToggle();

    // select current sphero position
    app.current_room_index = app.availables_room.indexOf(app.current_room);

  });

})(document);
