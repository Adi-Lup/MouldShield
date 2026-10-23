/* Visible startup diagnostics if a script is missing or this browser cannot run it. */
(function () {
  let failure = null;
  function show(message) {
    failure = message;
    function display() {
      const panel = document.getElementById('startup-error');
      if (panel) {
        panel.hidden = false;
        panel.textContent = 'Dashboard could not start: ' + failure + ' Extract all files into one folder, or open START_HERE.html. Send this message if you need help.';
      }
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', display, { once: true });
    else display();
  }
  window.addEventListener('error', function (event) {
    if (event.target && event.target.tagName === 'SCRIPT') show('A required JavaScript file did not load.');
    else if (event.message) show(event.message);
  }, true);
  window.addEventListener('unhandledrejection', function (event) {
    show(event.reason && event.reason.message ? event.reason.message : 'An unexpected error occurred.');
  });
  window.MouldShieldBoot = {
    ready: function () {
      const panel = document.getElementById('startup-status');
      if (panel) panel.hidden = true;
    }
  };
}());
