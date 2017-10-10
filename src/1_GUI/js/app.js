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
        simulation:{
            packets_loaded: false,
            simulation_run: false,
            template_data: "",
            results_packet: "",
            results_node: "",
            results_rule: ""
        },
        selected_node: {
            color:"",
            id:-1,
            label:"",
            shape:"",
            type: "",
            committed: false,
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
                    src_port:{
                        any: true,
                        value: ""
                    },
                    dst_port:{
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
                'UDP/IP':{
                    label: "UDP/IP",
                    value: "udpip"
                },                
                'ICMP':{
                    label: "ICMP",
                    value: "icmp"
                }
            }
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
            fileUpload: false,
            downloadFile: false,
            downloadResults: false,
            firewall: false,
            timeline: false
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
                            src_port:{
                                any: true,
                                value: ""
                            },
                            dst_port:{
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
            if (key=="2-1"){
                // New Node
                this.clear_selected_node();
                this.open_side_bar();
            }
            else if (key=="2-2"){
                // Delete node
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
            else if (key=="2-3"){
                // Timeline
                var selectedNode = this.selected_node;
                var id = selectedNode['id'];
                if (id==-1){
                    this.$notify({
                      title: 'Warning',
                      message: 'Select a node before viewing its timeline',
                      type: 'warning'
                  });
                }else{
                    if (!app.$data['simulation']["simulation_run"]){
                        app.$message({
                            message: 'Run simulation before attempting to download results',
                            type: 'error'
                          });
                    }else{
                        websocket_run('get-sim-results', "", (result)=>{
                            app.$data['simulation']["results_rule"]=result.rule;
                            app.$data['simulation']["results_node"]=result.node;
                            app.$data['simulation']["results_packet"]=result.packet;
                            app.$data['form_visible']['timeline']=true;
                            app.$data.loading=true;
                            setTimeout(() => {
                                var node_ip = app.tableData[app.selected_node.id].Node_Addr;
                                var container = document.getElementById('timeline');
                                container.innerHTML="";
                                var options = {zoomable:true, format:{
                                    minorLabels: {
                                        weekday:    'D',
                                }},showMinorLabels:false,showMajorLabels:false,selectable:false,showCurrentTime:false}
                                var items = new vis.DataSet([])
                                x = app.simulation.results_rule.split("\n");
                                base_start = new Date();;
                                for (var i = 1; i < x.length; i++) {
                                    var e = x[i].split(",");
                                    if (e[2]==node_ip){
                                        base_start.setDate(base_start.getDate()+ 1);
                                        items.add({
                                            id: i,
                                            content: "Packet " + e[1] +" - "+e[3] +" -> "+e[6],
                                            start: base_start.toISOString().split('T')[0]
                                        });
                                    }
                                }
                                var timeline = new vis.Timeline(container, items, options);
                                app.$data.loading=false;
                            }, 500);
                        });
                    }

                }
            }
            else if (key=="3-1"){
                //Download template
                websocket_run('download-sim-template', "", (d)=>{
                    app.$data['simulation']['template_data'] = d;
                    app.$data['form_visible']['downloadFile']=true;
                });
            }
            else if (key=="3-2"){
                // Upload sim file
                app.$data['form_visible']['fileUpload']=true;
            }
            else if (key=="3-3"){
                // Run simulation
                if (!app.$data['simulation']["packets_loaded"]){
                    app.$message({
                        message: 'Upload simulation file before attempting to run simulation',
                        type: 'error'
                      });
                }else{
                    websocket_run('run-simulation', "", ()=>{
                        app.$data['simulation']["packets_loaded"] = true;
                        app.$data['simulation']["simulation_run"] = true;
                    });
                }
            }
            else if (key=="3-4"){
                // Download results
                if (!app.$data['simulation']["simulation_run"]){
                    app.$message({
                        message: 'Run simulation before attempting to download results',
                        type: 'error'
                      });
                }else{
                    websocket_run('get-sim-results', "", (result)=>{
                        app.$data['simulation']["results_rule"]=result.rule;
                        app.$data['simulation']["results_node"]=result.node;
                        app.$data['simulation']["results_packet"]=result.packet;
                        app.$data['form_visible']["downloadResults"] = true
                    });
                }
            }
            else if (key=="4"){
                websocket_run('update-status-table', "loud", ()=>{});
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
            var nodeDetails = this.nodes;
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
                src: !new_rule.src.any && new_rule.src.value,
                dst: !new_rule.dst.any && new_rule.dst.value,
                src_port: !new_rule.src_port.any && new_rule.src_port.value,
                dst_port: !new_rule.dst_port.any && new_rule.dst_port.value,
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
        },
        submitUpload() {
            this.$refs.upload.submit();
        },
        beforeUploadEvent: function(file){
            var reader = new FileReader();
            reader.onload = (e)=>{
                websocket_run('upload-sim', e.target.result, function() {
                    app.$data['simulation']["packets_loaded"] = true;
                    app.$data['simulation']["simulation_run"] = false;
                    app.$data['form_visible']['fileUpload'] = false;
                }); 
            };
            reader.readAsText(file);
            return false;
        },
        download_template: function(){
            template_data = app.$data['simulation']['template_data'];
            if (template_data===""){
                this.$notify({
                    title: 'Warning',
                    message: 'No template data found. Please try again',
                    type: 'warning'
                });
            }else{
                var pom = document.createElement('a');
                pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(template_data));
                pom.setAttribute('download', "Packet_Template.csv");
            
                if (document.createEvent) {
                    var event = document.createEvent('MouseEvents');
                    event.initEvent('click', true, true);
                    pom.dispatchEvent(event);
                }
                else {
                    pom.click();
                }
            }
        },
        download_results_packet: function(){
            results = app.$data['simulation']['results_packet'];
            if (results===""){
                this.$notify({
                    title: 'Warning',
                    message: 'No results data found. Please run the simulation try again',
                    type: 'warning'
                });
            }else{
                var pom = document.createElement('a');
                pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(results));
                pom.setAttribute('download', "Packets_Results.csv");
            
                if (document.createEvent) {
                    var event = document.createEvent('MouseEvents');
                    event.initEvent('click', true, true);
                    pom.dispatchEvent(event);
                }
                else {
                    pom.click();
                }
            }
        },
        download_results_node: function(){
            results = app.$data['simulation']['results_node'];
            if (results===""){
                this.$notify({
                    title: 'Warning',
                    message: 'No results data found. Please run the simulation try again',
                    type: 'warning'
                });
            }else{
                var pom = document.createElement('a');
                pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(results));
                pom.setAttribute('download', "Node_Results.csv");
            
                if (document.createEvent) {
                    var event = document.createEvent('MouseEvents');
                    event.initEvent('click', true, true);
                    pom.dispatchEvent(event);
                }
                else {
                    pom.click();
                }
            }
        },
        download_results_rule: function(){
            results = app.$data['simulation']['results_rule'];
            if (results===""){
                this.$notify({
                    title: 'Warning',
                    message: 'No results data found. Please run the simulation try again',
                    type: 'warning'
                });
            }else{
                var pom = document.createElement('a');
                pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(results));
                pom.setAttribute('download', "Rule_Results.csv");
            
                if (document.createEvent) {
                    var event = document.createEvent('MouseEvents');
                    event.initEvent('click', true, true);
                    pom.dispatchEvent(event);
                }
                else {
                    pom.click();
                }
            }
        }
    },
});
