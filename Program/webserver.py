from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    with open('GUI/index.html') as f:
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

app.router.add_static('/css', 'GUI/css')
app.router.add_static('/js', 'GUI/js')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)