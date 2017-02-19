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

function alert_msg(msg, level) {
    if (level == "error") {
        Materialize.toast(msg, 5000, "red");
    } else if (level == "warning") {
        Materialize.toast(msg, 5000, "orange");
    } else if (level == "info") {
        Materialize.toast(msg, 5000, "blue");
    }
}
$(function() {
    //CONSTANTS
    NODE_SPACING = 200;

    // SETUP COMPONENTS
    $('#side_bar').sideNav({
        edge: 'right',
        closeOnClick: false,
        draggable: false
    });

    // SETUP NETWORK
    var nodeDetails, nodes, edgesArray, edges, network;
    current_node_id = 1;
    current_x = NODE_SPACING;

    nodeDetails = [{
        id: 0,
        label: 'Client 1',
        shape: 'circle',
        type: 'C',
        color: node_color(0, 1)
    }, {
        id: 1,
        label: 'Server 1',
        shape: 'circle',
        type: 'S',
        color: node_color(1, 0)
    }];
    nodes = new vis.DataSet(nodeDetails);

    current_edge_id = 0;
    var edges = new vis.DataSet([
        { id: 0, from: 0, to: 1 },
    ]);

    // create a network
    var container = document.getElementById('firewall_network');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        "physics": {
            "enabled": false,
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
    var network = new vis.Network(container, data, options);

    function fitAnimated() {
        var options = {
            easingFunction: "easeInQuad"
        };
        network.fit({
            animation: options
        });
    }

    function load_details_bar(node_id) {
        my_node = null;
        type_array = [];
        x = network.nodes;
        my_node = nodeDetails[node_id]
        if (my_node !== null) {
            $("#node_name").val(my_node.label);
            $("#node_type").val(my_node.type.split(','));
            $("#node_type").material_select();
            $("#node_details_btn").text("Save");
            show_side_nav();
        }
    }

    $("#nav_btn_node_new").click(function() {
        $("#node_name").val("");
        $("#node_details_btn").text("Create");
        show_side_nav();
    });
    $("#nav_btn_node_del").click(function() {
        network.deleteSelected();
    })

    connect_node_start = null;
    $("#nav_btn_node_connect").click(function() {
        if (network.getSelectedNodes().length == 1) {
            connect_node_start = network.getSelectedNodes()[0];
            alert_msg('Select node to connect to', 'info');
        } else {
            alert_msg('Select a node first', 'warning');
        }
    });

    $("#form_node_new").submit(function() {
        name = $("#node_name").val();
        s = $("#node_type").val().includes('S');
        c = $("#node_type").val().includes('C');
        if ($("#node_details_btn").text() == 'Create') {
            var newId = ++current_node_id;
            current_x += NODE_SPACING;
            node_to_add = {
                id: newId,
                label: name,
                shape: 'circle',
                color: node_color(s, c),
                type: s ? c ? 'S,C' : 'S' : 'C',
                x: current_x
            };
            nodeDetails.push(node_to_add)
            nodes.add(node_to_add);
        } else {
            var selectedNode = network.getSelectedNodes()[0];
            nodes.update({
                id: selectedNode,
                label: name,
                color: node_color(s, c),
            });
            nodeDetails[selectedNode] = {
                label: name,
                type: s ? c ? 'S,C' : 'S' : 'C',
            };
            network.unselectAll();
        }
        hide_side_nav();
        $("#node_type").val('S');
        $("#node_type").material_select();
        $("#node_name").val("");
        fitAnimated();
    });

    network.on("click", function(params) {
        if (params.nodes.length == 1) {
            if (connect_node_start !== null) {
                if (network.getSelectedNodes()[0] == connect_node_start) {
                    alert_msg("Can't connect node to self", "error");
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
                        alert_msg("Nodes already connected", "error");
                    } else {
                        new_edge = {
                            id: ++current_edge_id,
                            from: connect_node_start,
                            to: network.getSelectedNodes()[0]
                        }
                        edges.add(new_edge);
                        alert_msg("Connected nodes", "info");
                    }
                    network.unselectAll();
                }
                connect_node_start = null;
            } else {
                load_details_bar(params.nodes[0]);
            }
        } else {
            hide_side_nav();
        }
    });


    $("#btn_close_sideNav").click(function() {
        hide_side_nav();
        $("#node_name").val("");
    })
});