app = new Vue({
    el: '#app',
    data: {
        selected_node: {
            id: 0,
            label: 'Client 1',
            shape: 'circle',
            type: 'C',
        },
        nodes: []
    }
})