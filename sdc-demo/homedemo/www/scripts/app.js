(function (document) {
  'use strict';

  var app = document.querySelector('#app');
  app.is_calibrating = false;
  app.calibrationMessage = 'Start calibration';

  // imports are loaded and elements have been registered
  window.addEventListener('WebComponentsReady', function () {
    var calibrationButton = document.querySelector('#calibrationButton');

    calibrationButton.addEventListener('click', calibrationToggle);

    function calibrationToggle(_) {
      if (calibrationButton.active) {
        app.calibrationMessage = 'End calibration';
      } else {
        app.calibrationMessage = 'Start calibration';
      }
    }

    // only here get the websocket status back and toggle values if needed
    var socket = new WebSocket("ws://" + window.location.hostname + ":8002/");

  });

})(document);
