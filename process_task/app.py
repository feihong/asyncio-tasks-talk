import muffin
from muffin_playground import Application, WebSocketWriter


app = Application()


# @app.register('/')
# async def index(request):
#     results = await fetch(0)
#     return app.render('index.plim', results=results, page_size=PAGE_SIZE)


@app.register('/report/')
async def websocket(request):
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)
    print('connected')
    async for msg in ws:
        print(msg.data)
    return ws


app.register_static_resource()
