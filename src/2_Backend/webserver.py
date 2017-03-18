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

from application import *
import os
from aiohttp import web
import socketio

if os.name == 'nt':
    base_index = '..\\1_GUI\\'
else:
    base_index = '../1_GUI/'

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


async def index(request):
    """Serve the client-side application."""
    with open(base_index + 'index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('connect', namespace='')
def connect(sid, environ):
    print("connect ", sid)


@sio.on('chat message', namespace='')
async def message(sid, data):
    print("message ", data)
    await sio.emit('reply', room=sid)


@sio.on('disconnect', namespace='')
def disconnect(sid):
    print('disconnect ', sid)


app.router.add_static('/css', base_index + 'css')
app.router.add_static('/js', base_index + 'js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)
