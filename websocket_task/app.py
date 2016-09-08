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

        # The following won't work, because you are not allowed to make
        # concurrent calls to ws.receive()!
        # await asyncio.wait([ws.receive(), asyncio.sleep(0.05)], timeout=0.05)

    await ws.close()
    return ws
