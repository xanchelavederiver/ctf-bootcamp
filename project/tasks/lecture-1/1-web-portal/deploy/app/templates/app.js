// Портал клиента — интерфейсные мелочи.
(function () {
  "use strict";

  // Служебная заметка аудита: показывается по Ctrl+Shift+Y.
  var note = [{{ codes }}];

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.shiftKey && (e.key === "Y" || e.key === "y")) {
      e.preventDefault();
      var text = String.fromCharCode.apply(null, note);
      window.alert(text);
    }
  });
})();
