
function node_color(is_server, is_client) {
    if (is_server) {
        if (is_client) {
            return "#ffcf47";
        }
        return "#ff7b7b";
    }
    if (is_client) {
        return "#7dff7b";
    }
    return "#000";
}

function alert_msg(msg, level, timeout) {
    if (level == "error") {
        Materialize.toast(msg, timeout || 200000, "red");
    } else if (level == "warning") {
        Materialize.toast(msg, timeout || 8000, "orange");
    } else if (level == "info") {
        Materialize.toast(msg, timeout || 5000, "blue");
    }
}
var current_node_id = -1;
var current_edge_id = -1;
var nodes
var edges
$(function() {
    // SETUP NETWORK
    var nodeDetails;

    app.$data.nodes= [];
	nodeDetails = app.$data.nodes;
    nodes = new vis.DataSet(nodeDetails);

    app.$data.edges = [];
    edges = new vis.DataSet(app.$data.edges);
    // create a network
    var container = document.getElementById('firewall_network');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        "physics": {
            "enabled": false
        },
        "edges": {
            "smooth": {
                "type": "horizontal",
                "forceDirection": "vertical",
                "roundness": 0
            },
            "color": "black"
        },
        "interaction":{
            "zoomView": false
        }
    };
    network = new vis.Network(container, data, options);

    function fitAnimated() {
        var options = {
            easingFunction: "easeInQuad"
        };
        network.fit({
            animation: options
        });
    }

    function load_details_bar(node_id) {
        var my_node = nodeDetails[node_id];
        if (my_node !== null) {
            app.$data.selected_node['type']=my_node.type;
            app.open_side_bar();
        }
    }

    $("#form_node_new").submit(function(e) {
        e.preventDefault();
    });

    network.on("click", function(params) {
        if (params.nodes.length == 1) {
            var x=nodeDetails[network.getSelectedNodes()[0]];
            var vs =['color','id','label','shape','type','committed'];
            for (var y=0;y<vs.length;y++){
                app.$data.selected_node[vs[y]]=x[vs[y]];
            }
            var connect_node_start = app.$data.connect_node_start;
            if (connect_node_start !== null) {
                if (network.getSelectedNodes()[0] == connect_node_start) {
                    alert_msg("Can't connect node to self", "warning");
                } else {
                    already_connected = false;
                    for (i = 0; i < edges.length; i++) {
                        if (edges._data[i].from == connect_node_start && edges._data[i].to == network.getSelectedNodes()[0]) {
                            already_connected = true;
                            break;
                        } else if (edges._data[i].from == network.getSelectedNodes()[0] && edges._data[i].to == connect_node_start) {
                            already_connected = true;
                            break;
                        }
                    }
                    if (already_connected) {
                        alert_msg("Nodes already connected", "warning");
                    } else {
                        var from = connect_node_start;
                        var to = network.getSelectedNodes()[0];
                        websocket_run('add-edge', [connect_node_start, network.getSelectedNodes()[0]], function(){
                            new_edge = {
                                id: ++current_edge_id,
                                from: from,
                                to: to
                            };
                            edges.add(new_edge);
                            app.$data.edges.push(new_edge);
                            alert_msg("Connected nodes", "info");
                        });
                    }
                    network.unselectAll();
                }
                app.$data.connect_node_start = null;
            } else {
                load_details_bar(params.nodes[0]);
            }
        } else {
            app.clear_selected_node();
            app.close_side_bar()
        }
    });
});
