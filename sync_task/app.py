import asyncio
import threading
import time
import muffin
from muffin_playground import Application, WebSocketHandler, ThreadSafeWebSocketWriter


app = Application()
app.register_special_static_route()


@app.register('/websocket/')
class WSHandler(WebSocketHandler):
    async def on_open(self):
        self.future = None
        self.writer = ThreadSafeWebSocketWriter(self.websocket)
        self.stop_event = threading.Event()

    async def on_message(self, msg):
        print(msg)
        if msg.data == 'start' and not self.future:
            loop = asyncio.get_event_loop()
            self.future = loop.run_in_executor(
                None, long_computation, self.writer, self.stop_event)
            self.future.add_done_callback(self.future_done_callback)
        elif msg.data == 'stop' and self.future:
            self.stop_event.set()

    def future_done_callback(self, future):
        print('done!')
        self.future = None
        self.stop_event.clear()


def long_computation(writer, stop_event):
    total = 150
    for i in range(1, total+1):
        if stop_event.is_set():
            return
        writer.write(type='progress', value=i, total=total)
        print(i)
        time.sleep(0.05)
