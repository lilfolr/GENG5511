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
            committed: false
        },
        nodes: [],
        edges: [],
        packet_options:{
            'Network_Layer': [
            'TCP/IP',
            'UDP/IP',
            'ICMP'
            ],
            'Data_Type':[
            'HTTP',
            'HTTPS',
            'FTP',
            'SMTP',
            'DNS',
            'DHCP'    
            ]
        }
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
            }
        }
    });
