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
            type: ['S'],
            committed: false,
            packet_simulation:{
                network_protocol: "",
                application_protocol: ""
            },
            firewall:{
                type: "",
                current_rules: "-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT<br/>-A FORWARD -i eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT <br/>-A FORWARD -i eth1 -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT <br/>-A OUTPUT -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT ",
                clear_current: "Clear",
                new_rules: ""
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
        tableData: [{
            Node_ID: '0',
            Node_Name: 'Client 1',
            Packets_In: '100',
            Packets_In_Block: '30',
            Packets_Out: '30',
            Packets_Out_Block: '2',
          }, {
            Node_ID: '1',
            Node_Name: 'Client 2',
            Packets_In: '10',
            Packets_In_Block: '0',
            Packets_Out: '30',
            Packets_Out_Block: '2',
          }, {
            Node_ID: '2',
            Node_Name: 'Server 1',
            Packets_In: '10',
            Packets_In_Block: '3',
            Packets_Out: '30',
            Packets_Out_Block: '0',
          }, {
            Node_ID: '3',
            Node_Name: 'Server 2',
            Packets_In: '300',
            Packets_In_Block: '20',
            Packets_Out: '360',
            Packets_Out_Block: '0',
          }]
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
                type: ['S'],
                committed: false
            }
        },
        handleSelect: function(key, keyPath) {
            if (key=="2-1"){
                this.clear_selected_node();
                show_side_nav();
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
                        this.$notify({
                          title: 'Node deleted',
                          message: 'Node has been removed',
                          type: 'info'
                      });
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
                    websocket_run('get-firewall', node_id, function(){
                        app.$data.form_visible.firewall=true;
                    });
                }
            }
        }
    });
