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

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
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
        to_return = []
        firewall = active_users[sid].get_node_firewall(node_id)
        for chain, rules in firewall.chains.items():
            chain = str(chain)
            chain = {
                "id" : chain,
                "label": chain,
                "children": []
            }
            i = 0
            for rule in rules:
                child = {
                    "id": i,
                    "label": "-i {} -o {} -p {} -s {} -d {} -j {}".format(rule.input_device, rule.output_device, 
                                                                          rule.protocol, rule.src, rule.dst, rule.match_chain).replace("None", "Any")
                }
                chain["children"].append(child)
                i += 1
            to_return.append(chain)
        return ["S", "", to_return]
    except expression as identifier:
        return ["E", "Error getting firewall - "+str(e)]

@sio.on('delete-rule')
def delete_rule(sid, data):
    try:
        check_user(sid)
        node_id = data[0]
        rules = data[1]  
        for r in rules:
            chain, rule = r
            logger.info("Deleting {} from {} - node {}".format(rule, chain, node_id))
            active_users[sid].get_node_firewall(node_id).remove_chain_rule(chain, rule)
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

@sio.on('add-rule')
def add_rule(sid, data):
    try:
        check_user(sid)
        node = data[0]
        rule = data[1]  # False = Any
        chain = "a"
        raise
        logger.debug("Adding rule to {0} - {1}".format(node, rule))
        #TODO: add firewall = active_users[sid].get_node_firewall(node_id)
        return ["S", "Rule added"]
    except expression as identifier:
        return ["E", "Error adding rule - "+str(e)]

def check_user(sid):
    if sid not in active_users:
        raise Exception("User not active")

app.router.add_static('/css', base_index + 'css')
app.router.add_static('/js', base_index + 'js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)
