import asyncio
import muffin
from muffin_playground import Application, WebSocketHandler, WebSocketWriter


app = Application()
app.register_special_static_route()


@app.register('/websocket/')
class WSHandler(WebSocketHandler):
    async def on_open(self):
        self.task = None
        self.writer = WebSocketWriter(self.websocket)

    def task_done_callback(self, future):
        self.task = None

    async def on_message(self, msg):
        print(msg)
        if msg.data == 'start' and not self.task:
            coroutine = long_task(self.writer)
            self.task = asyncio.ensure_future(coroutine)
            self.task.add_done_callback(self.task_done_callback)
        elif msg.data == 'stop' and self.task:
            self.task.cancel()


async def long_task(writer):
    total = 150
    for i in range(1, total+1):
        writer.write(type='progress', value=i, total=total)
        print(i)
        await asyncio.sleep(0.05)
