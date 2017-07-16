"""
METHODS:

METHOD_NAME (PARAMS) : RETURNS

conntect
disconnect

create_node (node_id, firewall_type) : success
destroy_node (node_id) : success
connect_node_to_node (node_id, node_id, port(s)) : success

add_node_firewall_rule (node_id, firewall_rule) : rule_id
remove_node_firewall_rule (node_id, firewall_rule_id) : success

set_node_source_packets(node_id, source_type, frequency, purity [1-% corrupt packets]) : success

run_simulation (seconds) : success [done]
stop_simulation : success

save_results () : json results

"""

import logging
import socketio
from aiohttp import web
from application import *

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

active_users = {}


async def index(request):
    """Serve the client-side application."""
    with open(base_index + 'index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# ======================== CONTROL ========================

@sio.on('connect', namespace='')
def connect(sid, environ):
    logger.info("{} connected ".format(sid))
    active_users[sid] = Application()

@sio.on('disconnect', namespace='')
def disconnect(sid):
    logger.info('{} disconnected '.format(sid))
    active_users.pop(sid)

# ======================== NODES ========================
@sio.on('create-node', namespace='')
async def create_node(sid, data):
    logger.debug("Creating node.")
    try:
        check_user(sid)
        node_id = data
        active_users[sid].create_node(node_id)
    except Exception as e:
        return ["E", "Error creating node - "+str(e)]
    else:
        return ["S","Node Created"]

@sio.on('delete-node', namespace='')
async def delete_node(sid, data):
    logger.debug("Deleting node.")
    try:
        check_user(sid)
        node_id = data
        active_users[sid].destroy_node(node_id)
    except Exception as e:
        return ["E", "Error deleting node - "+str(e)]
    else:
        return ["S","Node deleted "]

@sio.on('add-edge', namespace='')
async def connect_nodes(sid, data):
    try:
        check_user(sid)
        active_users[sid].connect_nodes(data[0], data[1])
    except expression as identifier:
        return ["E", "Error connecting nodes - "+str(e)]
    else:
        return ["S","Nodes connected "]

@sio.on('update-status-table', namespace='')
async def update_status_table_def(sid, data):
    await update_status_table(sid)
    print(data)
    if data=="loud":
        return ["S","Table update triggered"]
    # Quite update
    return ["N"]

# ======================== FIREWALL ========================

@sio.on('get-firewall', namespace='')
async def get_firewall(sid, node_id):
    try:
        check_user(sid)
        firewall = active_users[sid].get_node_firewall(node_id)
        return ["S", "", firewall]
    except expression as identifier:
        return ["E", "Error getting firewall - "+str(e)]

@sio.on('delete-rule')
def delete_rule(sid, data):
    try:
        check_user(sid)
        node = data[0]
        rules = data[1]
        #TODO: Delete firewall = active_users[sid].get_node_firewall(node_id)
        return ["S", "Rules deleted"]
    except expression as identifier:
        return ["E", "Error deleting rules - "+str(e)]

async def update_status_table(sid):
    toreturn = []
    for node_id, node_data in active_users[sid].current_nodes.items():
        toreturn.append({
            "Node_ID": node_id,
            "Packets_In": '0',
            "Packets_In_Block": '0',
            "Packets_Out": '0',
            "Packets_Out_Block": '0',
        })
    await sio.emit('update-table', data=toreturn, room=sid)

def check_user(sid):
    if sid not in active_users:
        raise Exception("User not active")

app.router.add_static('/css', base_index + 'css')
app.router.add_static('/js', base_index + 'js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)
