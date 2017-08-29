var socket = io.connect('http://ip_vm:8080/');
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
    message: 'Disconnected from Socket - please refresh the page',
    type: 'error',
    duration: 0
  });
  app.$data.loading=true;
});
socket.on('error', function(er){
  app.$notify({
    title: 'An error occured',
    message: er,
    type: 'error'
  });
})

socket.on('update-table', function(table_data){
  for (i=0;i<table_data.length;i++){
    table_data[i].Node_Name = app.$data.nodes[table_data[i].Node_ID].label
  }
  app.$data.tableData=table_data
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
    console.log('Running '+func+' with data '+data);
    socket.emit(func,data, (data) => {
      console.log(data)
      if (typeof data === 'undefined')
        data = ["S", ""]
      status = data[0];
      msg = data[1];
      if (status=="S"){
        if (data.length>2)
          succ_func(data[2]);
        else
          succ_func();
        if (msg!=="")
        app.$message({
          showClose: true,
          message: msg,
          type: 'info'
        });
      }
      else if (status=="E")
        app.$notify({
          title: 'An error occured',
          message: msg,
          type: 'error'
        });
    	app.$data.loading=false;
    }
  );
}
