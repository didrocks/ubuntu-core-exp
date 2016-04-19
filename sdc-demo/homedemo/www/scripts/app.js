(function (document) {
  'use strict';

  var app = document.querySelector('#app');
  app.is_calibrating = false;
  app.calibrationPos = 0;
  var _lastCalibrationPosSent = 0;
  app.current_room = 'space';
  app.availables_room = ['Room1', 'Room2', 'Room3', 'Room1', 'Room2', 'Room3'];

  // imports are loaded and elements have been registered
  window.addEventListener('WebComponentsReady', function () {

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


    // only here get the websocket status back and toggle values if needed
    //var socket = new WebSocket("ws://" + window.location.hostname + ":8002/");


    // initiate calibration toggle label
    calibrationToggle();

  });

})(document);
