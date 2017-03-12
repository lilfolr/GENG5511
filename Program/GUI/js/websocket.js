var socket = io.connect('http://localhost:8080');
alert_msg('Connecting to socket...', 'info');

socket.on('connect', function () {
    alert_msg('Socket Connected.', 'info');
});
socket.on('disconnect', function () {
    alert_msg('Socket Disconnected', 'info');
});


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