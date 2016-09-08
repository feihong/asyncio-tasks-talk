import random
import asyncio
import muffin
from muffin_playground import Application, WebSocketWriter


NAMES = ['mario', 'luigi', 'toadstool', 'peach', 'bowser', 'koopa', 'goomba']


app = Application()
app.register_special_static_route()
app.sockets = set()
app.task_id = 1


@app.register('/start-task/')
async def start_task(request):
    name = '%s-%d' % (random.choice(NAMES), app.task_id)
    app.task_id += 1

    proc = await asyncio.create_subprocess_exec(
        'python', 'long_task.py', 'ws://localhost:5000/collect/', name)

    return str(proc)


@app.register('/progress/')
async def websocket(request):
    "Add and remove web socket objects for app.sockets."
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)
    app.sockets.add(ws)

    async for msg in ws:
        pass

    app.sockets.remove(ws)
    return ws


@app.register('/collect/')
async def websocket(request):
    "Collect messages from task processes and send them to browser clients."
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        for ws in app.sockets:
            ws.send_str(msg.data)
    return ws
