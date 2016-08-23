import asyncio
import threading
import json

import aiohttp


class WebSocketClient:
    def __init__(self, url, *, timeout=None):
        self.url = url
        self.timeout = timeout
        self._connect_event = threading.Event()
        self._close_event = asyncio.Event()

    def write(self, **kwargs):
        data = json.dumps(kwargs).encode('utf-8')
        print(data)
        self.loop.call_soon_threadsafe(self._write, data)

    def connect(self):
        def thread_main():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._loop_main())

        self.thread = threading.Thread(target=thread_main)
        self.thread.start()
        self._connect_event.wait(timeout=self.timeout)

    def close(self):
        # Notify event loop thread that connection should be closed.
        self.loop.call_soon_threadsafe(self._close_event.set)
        self.thread.join()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    async def _loop_main(self):
        session = aiohttp.ClientSession()
        ws = await session.ws_connect(self.url)
        self.ws = ws

        # Notify main thread that connection has been established.
        self._connect_event.set()

        # Wait for close event to be set.
        await self._close_event.wait()

        await ws.close()
        await session.close()

    def _write(self, data):
        self.ws.send_bytes(data)
