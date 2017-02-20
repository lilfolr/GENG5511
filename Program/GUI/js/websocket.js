var ws = new WebSocket("ws://localhost:9998/");
timeout = 5;
function setup_socket() {
    if ("WebSocket" in window) {
        ws.onopen = function() {
            ws.send("ack");
            alert_msg("Connecting to socket...", 'info');
        };

        ws.onmessage = function(evt) {
            var received_msg = evt.data;
            process_msg(evt.data);
        };

        ws.onclose = function() {
            timeout = timeout *2;
            alert_msg("Socket connection closed. Retrying in "+timeout+"s", 'error', timeout*1000);
            setTimeout(function(){
                ws = new WebSocket("ws://localhost:9998/");
                setup_socket();}, timeout*1000);
        };
    } else {
        alert("WebSocket NOT supported by your Browser!", 'error');
    }
}

function process_msg(msg) {
    switch (msg) {
        case 'ack':
            // Checking connection - getting ack        
            if (msg == 'ack')
                alert_msg("Connection established", 'info');
            break;
        default:
            // Waiting for polling information
            j = JSON.parse(msg);
            var markup = "<tr><td>" + j.id + "</td><td>Server name</td><td>" + j.p_in + "</td><td>" + j.p_in_b + "</td><td>" + j.p_out + "</td><td>" + j.p_out_b + "</td></tr>";
            $("#data_table").children().remove();
            $("#data_table").append(markup);
    }
}

function start_polling() {
    if (ws.readyState == 1) {
        ws.send('poll_status')
    }
    setTimeout(start_polling, 500);
}