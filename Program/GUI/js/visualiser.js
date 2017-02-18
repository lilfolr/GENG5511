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
    // SETUP MODALS
    $('#modal_node_new').modal({
        dismissible: true, // Modal can be dismissed by clicking outside of the modal
        opacity: .5, // Opacity of modal background
        startingTop: '4%', // Starting top style attribute
        endingTop: '10%', // Ending top style attribute
    });

    // SETUP NETWORK
    var nodeIds, nodesArray, nodes, edgesArray, edges, network;
    nodeIds = [2, 3, 4, 5];

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



    $("#nav_btn_node_new").click(function() {
        $('#modal_node_new').modal('open');
    });
    $("#nav_btn_node_del").click(function() {

    })
    $("#modal_form_node_new").submit(function() {
        var newId = (Math.random() * 1e7).toString(32);
        nodes.add({ id: newId, label: $("#new_node_name").val(), shape: 'circle', color: node_color($("#new_node_type").val().includes('S'), $("#new_node_type").val().includes('C')) });
        nodeIds.push(newId);
        $('#modal_node_new').modal('close');
        $("#new_node_name").val("");
        fitAnimated();
    });
});