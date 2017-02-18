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
$(function() {
    // SETUP COMPONENTS
    $('#side_bar').sideNav({
        edge: 'right',
        closeOnClick: false,
        draggable: true
    });

    // SETUP NETWORK
    var nodeIds, nodesArray, nodes, edgesArray, edges, network;
    nodeIds = [1];
    current_node_id = 1;
    current_x = 0;

    // create an array with nodes
    nodesArray = [
        { id: 1, label: 'Server 1', shape: 'circle', type: 'S', color: node_color(1, 0) },
    ];
    nodes = new vis.DataSet(nodesArray);

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
        network.fit({ animation: options });
    }

    function load_details_bar(node_id) {
        my_node = null;
        type_array = [];
        x = network.nodes;
        for (i = 0; i < nodesArray.length; i++) {
            if (nodesArray[i].id == node_id) {
                my_node = nodesArray[i]
            }
        }
        if (my_node !== null) {
            $("#node_name").val(my_node.label);
            $("#node_type").val(my_node.type.split(','));
            $("#node_type").material_select();
            $('#side_bar').sideNav('show');
        }
    }


    $("#nav_btn_node_new").click(function() {
        $("#node_name").val("");
        $('#side_bar').sideNav('show');
    });
    $("#nav_btn_node_del").click(function() {
        network.deleteSelected();
    })
    $("#form_node_new").submit(function() {
        var newId = ++current_node_id;
        current_x += 100;
        s = $("#node_type").val().includes('S');
        c = $("#node_type").val().includes('C');
        node_to_add = {
            id: newId,
            label: $("#node_name").val(),
            shape: 'circle',
            color: node_color(s, c),
            type: s ? c ? 'S,C' : 'S' : 'C',
            x: current_x
        };
        nodesArray.push(node_to_add)
        nodes.add(node_to_add);
        nodeIds.push(newId);
        $("#node_name").val("");
        fitAnimated();
    });

    network.on("click", function(params) {
        if (params.nodes.length == 1) {
            load_details_bar(params.nodes[0])
        }
    });


    $("#btn_close_sideNav").click(function() {
        $('#side_bar').sideNav('hide');
        $("#node_name").val("");
    })
});