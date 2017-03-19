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
        }
    }

});