# Using Tasks in Your Asyncio Web App
## ChiPy
## August 11, 2016
### Feihong Hsu
### github.com/feihong

---

# What

In this talk, I will be talking about starting, stopping, and displaying incremental data from long-running tasks in an asyncio-based web application.

The examples for this talk were made to run on [muffin](https://github.com/klen/muffin), a high-level web framework built on top of [aiohttp](https://github.com/KeepSafe/aiohttp).

---
# Why

You could just run tasks in Celery, so why bother with asyncio?

Well, depending on your circumstances, using asyncio can result in simpler code and better performance.

---
# Three types of tasks

- Asynchronous
- Synchronous (via ThreadExecutor)
- Inside web socket handler

---
# Asynchronous task

- Put everything in web socket handler
- Use a class as the handler since there are callbacks involved
- Functionality:
  - Start
  - Stop
  - Send messages to browser

---
# Task function

```python
async def long_task(writer):
    total = 150
    for i in range(1, total+1):
        writer.write(type='progress', value=i, total=total)
        print(i)
        await asyncio.sleep(0.05)
```

---
# Launching the task

```python
coroutine = long_task(WebSocketWriter(websocket))
task = asyncio.ensure_future(coroutine)
task.add_done_callback(done_cabllback)
```

---
# The on_message() method

```python
async def on_message(self, msg):
    print(msg)
    if msg.data == 'start' and not self.task:
        coroutine = long_task(WebSocketWriter(self.websocket))
        self.task = asyncio.ensure_future(coroutine)
        self.task.add_done_callback(self.done_callback)
    elif msg.data == 'stop' and self.task:
        self.task.cancel()
        self.task = None

def done_callback(self, future):
    self.task = None
```

---
# Demo

- Show entire Python program
- Run program: `muffin app run`

---
# Client code

```python
class MyClient(WsClient):
    url = '/websocket/'
    auto_dispatch = True

    def on_progress(self, obj):
        print(obj)
        percent = obj['value'] / obj['total'] * 100
        jq('progress').val(percent)
        jq('.percent').text(str.format('{}%', percent.toFixed(0)))
```

---
# Using the native API

```python
ws = WebSocket('ws://' + document.location.host + '/websocket/')

ws.onopen = def(evt):
  print('Websocket opened')

ws.onclose = def(evt):
  print('Websocket closed')

ws.onmessage = def(evt):
  obj = JSON.parse(evt.data)
  print(obj)
```

---
# Synchronous task

We'll do everything we did for the asynchronous task, except that our task function this time is a normal Python function.

---
# Task function

```python
def long_task(writer, stop_event):
    total = 150
    for i in range(1, total+1):
        if stop_event.is_set():
            return
        writer.write(type='progress', value=i, total=total)
        print(i)
        time.sleep(0.05)
```

---
# Launching the task

```python
stop_event = threading.Event()
loop = asyncio.get_event_loop()
coroutine = loop.run_in_executor(
  None,
  long_task,
  ThreadSafeWebSocketWriter(websocket),
  stop_event)
task = asyncio.ensure_future(coroutine)
task.add_done_callback(done_callback)
```

---
# The on_message() method

```python
async def on_message(self, msg):
    print(msg)
    if msg.data == 'start' and not self.task:
        self.task = self.execute_task(
            long_task,
            ThreadSafeWebSocketWriter(self.websocket),
            self.stop_event)
        self.task.add_done_callback(self.done_callback)
    elif msg.data == 'stop' and self.task:
        self.stop_event.set()
```

---
# Another demo

```
muffin app run
```

---
# Client code

The web socket code is exactly the same! Take a look at the button click handling code:

```python
jq = window.jQuery

jq('button.start').on('click', def(evt):
    client.send_text('start')
)
jq('button.stop').on('click', def(evt):
    client.send_text('stop')
)
```

---
# Web socket handler as a task

The web socket handler is essentially a task, since it runs for as long as the server maintains a `ws://` connection with the browser.

If you don't need the task to keep running after the web socket is closed, then this is a good solution.

---
# Task function

```python
async def fetch(page):
    if page >= 11:
        return None
    start = (page - 1) * PAGE_SIZE + 1
    end = start + PAGE_SIZE
    await asyncio.sleep(1)
    return [i for i in range(start, end)]
```

---
# The request handler function

```python
@app.register('/')
async def index(request):
    results = await fetch(1)
    return app.render('index.plim', results=results)
```

---
# The web socket handler function

```python
@app.register('/websocket/')
async def websocket(request):
    # ...
    page = 2
    while not ws.closed:
        results = await fetch(page)
        if results is None:
            break
        writer.write(type='results', value=results)
        page += 1
    # ...
```

---
# The last demo

```
muffin app run
```

---
# Client code

```python
class MyClient(WsClient):
    url = '/websocket/'
    auto_dispatch = True

    def on_results(evt, obj):
        print(obj)
        row = jq('<div class="result-row">').appendTo('.results')
        for v in obj['value']:
            jq('<div class="result">').text(v).appendTo(row)
```

---
# Some notes about the examples

- I'm using a project called [muffin-playground](https://github.com/feihong/muffin-playground), which provides convenience classes that reduce boilerplate code.
- Muffin-playground supports auto-compilation of these languages:
  - RapydScript Python-to-JavaScript compiler (.pyj)
  - Plim template engine (.plim)
  - Stylus CSS preprocessor (.styl)

---
# Conclusion

- Asyncio makes it easy to work with tasks and web sockets
- Asyncio web app frameworks are ready for primetime (probably)
- Python in the browser is in an interesting place right now
