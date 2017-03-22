var socket = io.connect('http://localhost:8080');
app.$message({
  message: 'Connecting to socket...',
  type: 'info'
});

socket.on('connect', function () {
  app.$message({
    message: 'Connected to Socket',
    type: 'info'
  });
});
socket.on('disconnect', function () {
  app.$message({
    message: 'Disconnected from Socket',
    type: 'warning'
  });
});
socket.on('error', function(er){
  app.$notify({
    title: 'An error occured',
    message: er,
    type: 'error'
  });
})

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
	app.$data.loading=true;
    // Timeout to simluate network
    setTimeout(function(){
        console.log('Running '+func+' with data '+data);
        socket.emit(func,data)
    	  app.$data.loading=false;
        succ_func()
    },1000)
}