# Using Tasks in Your Asyncio Web App

## ChiPy
## September 8, 2016
### Feihong Hsu
### github.com/feihong

---

This talk can be found online at the repo github.com/feihong/asyncio-tasks-talk, which includes

- Slides
- Notes
- Example programs

---
# What

In this talk, I will be talking about starting, stopping, and displaying incremental data from long-running tasks in an asyncio-based web application.

The examples for this talk were made to run on [muffin](https://github.com/klen/muffin), a high-level web framework built on top of [aiohttp](https://github.com/KeepSafe/aiohttp).

^ The Muffin API, especially for defining routes and request handlers, seems to be modeled after the Flask API. But everything that works in aiohttp still works in aiohttp.

---
# Why

You could just run tasks in Celery or Django Channels, so why bother with asyncio?

Depending on your circumstances, using asyncio can lead to

- A simpler architecture
- Less code
- Better performance

^ Simpler architecture: With Celery, you'd also also need to set up RabbitMQ and the Celery task runner. With Django Channels, you need to setup Redis. Asyncio tasks run within the same process.

^ Less code: You don't need to worry about interprocess communication. Tasks are just functions, and can accept any kind of argument.

^ Better performance: Asyncio tasks are much more scalable than threads. Because asyncio I/O operations don't block, you can have many more simultaneously open connections.

---
# Types of tasks we'll talk about today

- Asynchronous
- Synchronous (using ThreadExecutor)
- Inside web socket handler
- Inside a separate process

---
# Asynchronous task

We'll start the task in a web socket handler. This makes the most sense if we want the browser to receive messages from the task.

If you don't need the task to communicate with the browser, then using an Ajax call would be fine.

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

^ The async and await keywords were introduced in Python 3.5.

^ The thing to remember about async functions is that when you call them, you don't get back the value that you return in the function. Instead, you will get a coroutine object, which is pretty much useless unless you have an event loop running.

---
# Scheduling the task function

```python
coroutine = long_task(writer)
asyncio.ensure_future(coroutine)

asyncio.get_event_loop()run_forever()
```

---
# The web socket handler

```python
@app.register('/websocket/')
async def websocket(request):
    ws = muffin.WebSocketResponse()
    await ws.prepare(request)
    writer = WebSocketWriter(ws)

    async for msg in ws:
        if msg.data == 'start':
            coroutine = long_task(WebSocketWriter(ws))
            task = asyncio.ensure_future(coroutine)

    return ws
```

---
# Demo

- Show entire Python program
- Run program: `muffin app run`

---
# Client code

```python
ws = new WebSocket('ws://localhost:5000/websocket/')
ws.onmessage = def(evt):
    obj = JSON.parse(evt.data)
    print(obj)
    percent = obj['value'] / obj['total'] * 100
    jq('progress').val(percent)
    jq('.percent').text(str.format('{}%', percent.toFixed(0)))
```

^ The client code here was written in Python, and compiled with [RapydScript](https://github.com/kovidgoyal/rapydscript-ng), a Python-to-JavaScript compiler. Note the anonymous function, which is a special syntax that the RapydScript compiler supports. The `jq` variable references the jQuery function.

---
# Adding the ability to cancel the task



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
