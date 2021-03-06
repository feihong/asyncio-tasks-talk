import asyncio
import muffin
from muffin_playground import Application, WebSocketWriter


app = Application()
app.register_special_static_route()


@app.register('/websocket/')
async def websocket(request):
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)

    writer = WebSocketWriter(ws)

    async for msg in ws:
        print(msg.data)
        if msg.data == 'start':
            coroutine = long_task(writer)
            task = asyncio.ensure_future(coroutine)
            await task
            print('Finished task')

    return ws


async def long_task(writer):
    total = 100
    for i in range(1, total+1):
        writer.write(type='progress', value=i, total=total)
        print(i)
        await asyncio.sleep(0.05)
