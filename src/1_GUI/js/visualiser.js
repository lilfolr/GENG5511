side_nav_open = false;

function show_side_nav() {
    if (!side_nav_open) {
        $('#side_bar').sideNav('show');
        side_nav_open = true;
    }
}

function hide_side_nav() {
    if (side_nav_open) {
        $('#side_bar').sideNav('hide');
        side_nav_open = false;
    }
}

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

$(function() {
    $('.modal').modal();


    //CONSTANTS
    NODE_SPACING = 200;

    // SETUP COMPONENTS
    $('#side_bar').sideNav({
        edge: 'right',
        closeOnClick: false,
        draggable: false
    });
    $('#loading_modal').modal({
        dismissible: false
    });
    $("#node_type").material_select();

    // SETUP NETWORK
    var nodeDetails, nodes, edges, network;
    var current_node_id = 1;
    var current_edge_id = 0;
    var current_x = NODE_SPACING;
    
    app.$data.nodes= [{
        id: 0,
        label: 'Client 1',
        shape: 'circle',
        type: ['C'],
        color: node_color(0, 1),
        committed: true
    }, {
        id: 1,
        label: 'Server 1',
        shape: 'circle',
        type: ['S'],
        color: node_color(1, 0),
        committed: true
    }];
	nodeDetails = app.$data.nodes;
    nodes = new vis.DataSet(nodeDetails);

    edges = new vis.DataSet([{
        id: 0,
        from: 0,
        to: 1
    }]);

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
        var x = network.nodes;
        var my_node = nodeDetails[node_id];
        if (my_node !== null) {
            app.$data.selected_node['type']=my_node.type;
            show_side_nav();
        }
    }

    function load_firewall_dialog(node_id) {
        websocket_run('get-firewall', node_id, function(){
            $('#firewall_modal').modal('open');
        });
    }

    $("#nav_btn_node_new").click(function() {
        app.clear_selected_node();
        show_side_nav();
    });
    $("#nav_btn_node_del").click(function() {
        network.deleteSelected();
    });

    connect_node_start = null;
    $("#nav_btn_node_connect").click(function() {
        if (network.getSelectedNodes().length == 1) {
            connect_node_start = network.getSelectedNodes()[0];
            alert_msg('Select node to connect to', 'info');
        } else {
            alert_msg('Select a node first', 'warning');
        }
    });

    $('#node_details_firewall').click(function(){
        if (network.getSelectedNodes().length == 1) {
            node_id = network.getSelectedNodes()[0];
            load_firewall_dialog(node_id);
        } else {
            alert_msg('Select a node first', 'warning');
        }
    });

    $("#form_node_new").submit(function(e) {
        e.preventDefault();
        var name = app.$data.selected_node['label'];
        var s = $("#node_type").val().includes('S');
        var c = $("#node_type").val().includes('C');
        if (!app.$data.selected_node['committed']) {
            var newId = current_node_id+1;
            websocket_run('create-node', newId, function(){
                console.log('Creating node');
                var newId = ++current_node_id;
                current_x += NODE_SPACING;
                node_to_add = {
                id: newId,
                    label: name,
                    shape: 'circle',
                    color: node_color(s, c),
                    type: s ? c ? ['S', 'C'] : ['S'] : ['C'],
                    x: current_x,
                    committed: true
                };
                nodeDetails.push(node_to_add);
                nodes.add(node_to_add);
            })

        } else {
            var selectedNode = app.$data.selected_node;
            var name = selectedNode['label'];   // Needs to be manually set to avoid race
            var id = selectedNode['id'];        // Needs to be manually set to avoid race
            websocket_run('update-node', id, function() {
                nodes.update({
                    id: id,
                    label: name,
                    color: node_color(s, c)
                });
                nodeDetails[id]['label'] = name;
                nodeDetails[id]['type'] = s ? c ? ['S', 'C'] : ['S'] : ['C'];
                network.unselectAll();
                fitAnimated();
            });
        }
        hide_side_nav();
        app.clear_selected_node();
        fitAnimated();
    });

    network.on("click", function(params) {
        if (params.nodes.length == 1) {
            var x=nodeDetails[network.getSelectedNodes()[0]];
            var vs =['color','id','label','shape','type','committed'];
            for (var y=0;y<vs.length;y++){
                app.$data.selected_node[vs[y]]=x[vs[y]];
            }
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
                        websocket_run('add-edge', [connect_node_start, network.getSelectedNodes()[0]], function(){
                            new_edge = {
                                id: ++current_edge_id,
                                from: connect_node_start,
                                to: network.getSelectedNodes()[0]
                            };
                            edges.add(new_edge);
                            alert_msg("Connected nodes", "info");
                        });
                    }
                    network.unselectAll();
                }
                connect_node_start = null;
            } else {
                load_details_bar(params.nodes[0]);
            }
        } else {
            app.clear_selected_node();
            hide_side_nav();
        }
    });


    $("#btn_close_sideNav").click(function() {
        hide_side_nav();
        app.clear_selected_node();
    })
});
