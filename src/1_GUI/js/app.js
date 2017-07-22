Vue.directive('multiselect', {
    bind: function (el, binding, vnode) {
        var element = $("#"+el.id);
        element.val(binding.value);
        element.material_select();
    },
    update: function(el, binding, vnode){
        var element = $("#"+el.id);
        element.val(binding.value);
        element.material_select();
    }
});

app = new Vue({
    el: '#app',
    data: {
        connect_node_start: null,
        selected_node: {
            color:"",
            id:-1,
            label:"",
            shape:"",
            type: "",
            committed: false,
            packet_simulation:{
                network_protocol: "",
                application_protocol: "",
                source_port: 22,
                dest_port: 22,
                ttl: 3,
                corrupt: 0
            },
            firewall:{
                type: "",
                current_rules: [
                    {
                        id: "C1",
                        label: 'INPUT ',
                        children: [{
                            id: 4,
                            label: 'Rule 1',
                        },
                        {
                            id: 3,
                            label: 'Rule 2',
                            },
                        ]
                    }   
                ],
                new_rule: {
                    input_device:{
                        any: true,
                        value: ""
                    },
                    output_device:{
                        any: true,
                        value: ""
                    },
                    protocol:{
                        any: true,
                        value: ""
                    },
                    src:{
                        any: true,
                        value: ""
                    },
                    dst:{
                        any: true,
                        value: ""
                    },
                    chain: ""

                }
            }
        },
        nodes: [],
        edges: [],
        node_type_options:{
            'Server':{
                label: "Server",
                value: "S"
            },
            "Client":{
                label: "Client",
                value: "C"
            }
        },
        packet_options:{
            'Network_Layer':{
                'TCP/IP':{
                    label: "TCP/IP",
                    value: "tcpip"
                },
                'UDP/IP':{
                    label: "UDP/IP",
                    value: "udpip"
                },                
                'ICMP':{
                    label: "ICMP",
                    value: "icmp"
                }
            },
            'Application_Layer':[
                'HTTP',
                'HTTPS',
                'FTP',
                'SMTP',
                'DNS',
                'DHCP'    
            ]
        },
        firewall_options:{
            'type':[
                'IPTables',
                'PF',
                'NTFTables' 
            ]
        },
        loading:false,
        form_visible:{
            packet: false,
            firewall: false
        },
        tableData: [],
    },

    mounted : function()
    {
        this.get_nodes();
        this.get_edges();
    },

    methods: {
        get_nodes: function() {
            console.warn('unimplemented');
        },
        get_edges: function () {
            console.warn('unimplemented');
        },
        clear_selected_node: function () {
            this.selected_node={
                color:"",
                id:-1,
                label:"",
                shape:"",
                type: "",
                committed: false,
                packet_simulation:{
                    network_protocol: "",
                    application_protocol: "",
                    source_port: 22,
                    dest_port: 22,
                    ttl: 3,
                    corrupt: 0
                },
                firewall:{
                            type: "",
                            current_rules: [
                            ],
                        new_rule: {
                            input_device:{
                                any: true,
                                value: ""
                            },
                            output_device:{
                                any: true,
                                value: ""
                            },
                            protocol:{
                                any: true,
                                value: ""
                            },
                            src:{
                                any: true,
                                value: ""
                            },
                            dst:{
                                any: true,
                                value: ""
                            },
                            chain: ""
                        }
                    }
            }
            this.close_side_bar();
        },
        close_side_bar: function(){
            child=null;
            for (var i=0;i<app.$children.length;i++){
                if (app.$children[i].$el.id=="side_nav_el"){
                    child = app.$children[i];
                    break;
                }
            }
            if (child != null){
                child.$data.openedMenus=[]
            }
        },
        open_side_bar: function(){
            child=null;
            for (var i=0;i<app.$children.length;i++){
                if (app.$children[i].$el.id=="side_nav_el"){
                    child = app.$children[i];
                    break;
                }
            }
            if (child != null){
                child.$data.openedMenus=["1"];
            }
        },
        handleSelect: function(key, keyPath) {
            if (key=="3"){
                websocket_run('update-status-table', "loud", ()=>{});
            }
            if (key=="2-1"){
                this.clear_selected_node();
                this.open_side_bar();
            }
            else if (key=="2-2"){
                var selectedNode = this.selected_node;
                var id = selectedNode['id'];
                if (id==-1){
                    this.$notify({
                      title: 'Warning',
                      message: 'Select a node to delete',
                      type: 'warning'
                  });
                }else{
                    websocket_run('delete-node', id, function() {
                        network.deleteSelected();
                        this.nodes[id] = null;
                        websocket_run('update-status-table');
                    }); 
                }
                this.clear_selected_node();
            }
            else if (key=="2-3")
                if (network.getSelectedNodes().length == 1) {
                    this.connect_node_start = network.getSelectedNodes()[0];
                    this.$notify({
                      title: 'Connect nodes',
                      message: 'Select a node to connect to',
                      type: 'info'
                  });
                } else {
                    this.$notify({
                      title: 'Connect nodes',
                      message: 'Select a node first',
                      type: 'warning'
                  });
                }
            },
            load_packet_dialog: function(){
                var node_id = this.selected_node.id;
                if (node_id==-1){
                    this.$notify({
                      title: 'Select a node',
                      message: 'Select a node first',
                      type: 'warning'
                  });
                } else {
                    websocket_run('get-packet_gen', node_id, function(){
                        app.$data.form_visible.packet=true;
                    });
                }
            },
            load_firewall_dialog: function(){
                var node_id = this.selected_node.id;
                if (node_id==-1){
                    this.$notify({
                      title: 'Select a node',
                      message: 'Select a node first',
                      type: 'warning'
                  });
                } else {
                    websocket_run('get-firewall', node_id, function(firewall_data){
                        app.$data.selected_node.firewall.current_rules = firewall_data;
                        app.$data.form_visible.firewall=true;
                    });
                }
            },
        create_node: function(){
            var newId = current_node_id+1;
            var name = this.selected_node.label;
            var type = this.selected_node.type;
            var color = type=="S"?"#ff7b7b":"#7dff7b";
            var nodeDetails = this.nodes;
            websocket_run('create-node', newId, function(){
                var newId = ++current_node_id;
                var node_to_add = {
                    id: newId,
                    label: name,
                    shape: 'circle',
                    color: color,
                    type: type,
                    committed: true
                };
                nodeDetails.push(node_to_add);
                nodes.add(node_to_add);
                network.fit({
                    animation: {
                        easingFunction: "easeInQuad"
                    }
                });
                websocket_run('update-status-table');
            });
            this.clear_selected_node();
        },
        update_node: function() {
            var selectedNode = this.selected_node;
            var name = selectedNode.label;   // Needs to be manually set to avoid race
            var id = selectedNode.id;        // Needs to be manually set to avoid race
            var type = selectedNode.type;
            var color = type=="S"?"#ff7b7b":"#7dff7b";
            websocket_run('update-node', id, function() {
                nodes.update({
                    id: id,
                    label: name,
                    color: color
                });
                nodeDetails[id]['label'] = name;
                nodeDetails[id]['type'] = selectedNode.type;
                network.unselectAll();
                network.fit({
                    animation: {
                        easingFunction: "easeInQuad"
                    }
                });
            });
            network.fit({
                    animation: {
                        easingFunction: "easeInQuad"
                    }
                });
            this.clear_selected_node();
        },
        delete_firewall_rule: function(rule_id){
            node_id = app.$data.selected_node.id;
            checked_nodes = app.$refs.tree.getCheckedNodes().map((a)=>{return a.$treeNodeId}) // Array of ids [could inc chain]
            rules = [];
            for (i=0;i<app.$refs.tree.data.length;i++){
                chain = app.$refs.tree.data[i];
                for(j=0;j<chain.children.length; j++)
                    if (checked_nodes.indexOf(chain.children[j].$treeNodeId) >= 0)
                        rules.push([chain.id, chain.children[j].id]);
            }
            if (rules.length===0)
                this.$notify({
                      title: 'Warning',
                      message: 'No rules checked to delete.',
                      type: 'warning'
                  });
            else
            websocket_run("delete-rule",[node_id, rules], ()=>{
               app.load_firewall_dialog();
            })
        },
        add_firewall_rule: function(){
            node_id = app.$data.selected_node.id;
            new_rule = app.$data.selected_node.firewall.new_rule;
            rule_data = {
                chain: new_rule.chain,
                dst: !new_rule.dst.any && new_rule.dst.value,
                src: !new_rule.src.any && new_rule.src.value,
                input_device: !new_rule.input_device.any && new_rule.input_device.value,
                output_device: !new_rule.output_device.any && new_rule.output_device.value,
                protocol: !new_rule.protocol.any && new_rule.protocol.value,
            }
            if (app.$refs.tree.getCheckedNodes().filter((e)=>{return typeof e.children !=="undefined"}).length !== 1)
                this.$notify({
                      title: 'Warning',
                      message: 'Select 1 chain to append to',
                      type: 'warning'
                  });
            else {
                websocket_run("add-rule", [node_id, app.$refs.tree.getCheckedNodes().filter((e)=>{return typeof e.children !=="undefined"})[0].id, rule_data], ()=>{
                app.load_firewall_dialog();
                });
            }
        }
    },
});
