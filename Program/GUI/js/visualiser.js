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
$(function () {
    // SETUP COMPONENTS
    $('#side_bar').sideNav({
        edge: 'right',
        closeOnClick: false,
        draggable: false
    });

    // SETUP NETWORK
    var nodeIds, nodeDetails, nodes, edgesArray, edges, network;
    nodeIds = [0];
    current_node_id = 0;
    current_x = 0;

    // create an array with nodes
    nodeDetails = [{
        id: 0,
        label: 'Server 1',
        shape: 'circle',
        type: 'S',
        color: node_color(1, 0)
    }, ];
    nodes = new vis.DataSet(nodeDetails);

    // create an array with edges
    edgesArray = [];
    edges = new vis.DataSet(edgesArray);

    // create a network
    var container = document.getElementById('firewall_network');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        "physics": {
            "enabled": false,
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

    $("#nav_btn_node_new").click(function () {
        $("#node_name").val("");
        $("#node_details_btn").text("Create");
        show_side_nav();
    });
    $("#nav_btn_node_del").click(function () {
        network.deleteSelected();
    })
    $("#form_node_new").submit(function () {
        name = $("#node_name").val();
        s = $("#node_type").val().includes('S');
        c = $("#node_type").val().includes('C');
        if ($("#node_details_btn").text() == 'Create') {
            var newId = ++current_node_id;
            current_x += 100;

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
            nodeIds.push(newId);
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

    network.on("click", function (params) {
        if (params.nodes.length == 1) {
            load_details_bar(params.nodes[0])
        } else {
            hide_side_nav();
        }
    });


    $("#btn_close_sideNav").click(function () {
        hide_side_nav();
        $("#node_name").val("");
    })
});