import asyncio
import threading
import muffin
from muffin_playground import Application, WebSocketWriter


app = Application()
app.register_special_static_route()


@app.register('/websocket/')
async def websocket(request):
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)
    writer = WebSocketWriter(ws)

    total = 150
    for i in range(1, total+1):
        writer.write(type='progress', value=i, total=total)
        print(i)
        await asyncio.sleep(0.05)

    await ws.close()
    return ws
