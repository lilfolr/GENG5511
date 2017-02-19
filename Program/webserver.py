#!/usr/bin/env python

import asyncio
import websockets

async def run(websocket, path):
    while True:
        name = await websocket.recv()
        print("< {}".format(name))
        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

start_server = websockets.serve(run, 'localhost', 9998)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
