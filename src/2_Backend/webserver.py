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

import os, sys
import logging
import socketio
from aiohttp import web
from application import *

if os.name == 'nt':
    base_index = '..\\1_GUI\\'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "..\\iptables\\")))
else:
    base_index = '../1_GUI/'
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], "../iptables/")))

# import iptables_sim_interface as ip

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

active_users = {}


async def index(request):
    """Serve the client-side application."""
    with open(base_index + 'index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('connect', namespace='')
def connect(sid, environ):
    logger.info("{} connected ".format(sid))
    active_users[sid] = Application()


@sio.on('chat message', namespace='')
async def message(sid, data):
    print("message ", data)
    if data == 'er':
        await sio.emit('error', data="Test", room=sid)
    else:
        await sio.emit('reply', room=sid)


@sio.on('create-node', namespace='')
async def create_node(sid, data):
    logger.debug("Creating node.")
    try:
        check_user(sid)
        node_id = data
        new_node_id = active_users[sid].create_node(node_id)
    except Exception as e:
        return "Error creating node - "+str(e)
    else:
        return 'Success'


@sio.on('disconnect', namespace='')
def disconnect(sid):
    logger.info('{} disconnected '.format(sid))
    active_users.pop(sid)


def check_user(sid):
    if sid not in active_users:
        raise Exception("User not active")


app.router.add_static('/css', base_index + 'css')
app.router.add_static('/js', base_index + 'js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)
