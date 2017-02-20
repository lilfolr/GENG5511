#!/usr/bin/env python

import asyncio
import websockets
import json
from random import randint

async def run(websocket, path):
    while True:
        msg = await websocket.recv()
        print ("< "+msg)
        if msg == 'ack':
            print ("> ack")
            await websocket.send('ack')
            continue
        if msg == 'poll_status':
            print ("> node data")
            node_data = {'id': 1,
                         'p_in': randint(10,90),
                         'p_in_b': randint(0,9),
                         'p_out': randint(10,90),
                         'p_out_b': randint(0,9)}
            await websocket.send(json.dumps(node_data))

start_server = websockets.serve(run, 'localhost', 9998)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
