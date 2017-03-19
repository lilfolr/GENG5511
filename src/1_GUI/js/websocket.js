var socket = io.connect('http://localhost:8080');
alert_msg('Connecting to socket...', 'info');

socket.on('connect', function () {
    alert_msg('Socket Connected.', 'info');
});
socket.on('disconnect', function () {
    alert_msg('Socket Disconnected', 'info');
});

/**
 * Possible methods include:
 * create-node
 * update-node
 * add-connection
 * remove-connection
 *
 * @param func
 * @param data
 * @param succ_func
 */
function websocket_run(func, data, succ_func){

    $('#loading_modal').modal('open');
    // Timeout to simluate network
    setTimeout(function(){
        console.log('Running '+func+' with data '+data);
        $('#loading_modal').modal('close');
        succ_func()
    },200)
}