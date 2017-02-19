var ws = new WebSocket("ws://localhost:9998/");

function setup_socket() {
    if ("WebSocket" in window) {
        ws.onopen = function () {
            ws.send("Message to send");
            alert_msg("Message is sent...", 'info');
        };

        ws.onmessage = function (evt) {
            var received_msg = evt.data;
            alert_msg("Message received..."+received_msg, 'info');
        };

        ws.onclose = function () {
            alert_msg("Socket connection closed", 'error');
        };
    } else {
        alert("WebSocket NOT supported by your Browser!", 'error');
    }
}