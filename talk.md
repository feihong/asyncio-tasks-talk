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

The examples for this talk were made to run on [Muffin](https://github.com/klen/muffin), a high-level web framework built on top of [aiohttp](https://github.com/KeepSafe/aiohttp).

^ The Muffin API, especially for defining routes and request handlers, seems to be modeled after the Flask API. But everything that works in aiohttp still works in Muffin.

---
# Why

You could just run tasks in Celery or Django Channels, so why bother with asyncio?

Depending on your circumstances, using asyncio can lead to

- A simpler architecture
- Less code
- Better performance

^ Simpler architecture: With Celery, you'd also also need to set up RabbitMQ and the Celery task runner. With Django Channels, you need to set up Redis.

^ Less code: You don't need to worry about interprocess communication and serialization. Tasks are just functions, and can accept any kind of argument.

^ Better performance: Asyncio tasks are much more scalable than threads. Because asyncio network operations don't block, you can have many more simultaneously open connections.

---
# Overview of asyncio concepts

- Coroutine object
- Coroutine function (async function)
- Task

---
# What is a coroutine object?

An "object [representing] a computation or an I/O operation (usually a combination) that will complete eventually"

Originally, coroutine objects were essentially glorified generators. Python 3.5 introduced native coroutine objects, which are created by coroutine functions using the `async def` syntax.

^ Source: https://docs.python.org/3/library/asyncio-task.html

^ Source: https://www.python.org/dev/peps/pep-0492/#rationale-and-goals

---
# What is a coroutine function?

Coroutine functions are functions that define a coroutine, using either the `async def` syntax or the `@asyncio.coroutine` decorator.

If you don't need to worry about backwards compatibility, you should almost always use  new-style coroutine functions that return native coroutine objects.

^ New-style coroutine functions are more readable and more explicit. The `@asyncio.coroutine` decorator doesn't actually enforce anything, and can be successfully applied to a non-coroutine function. You'll only find out the hard way when your program crashes.

---
# A very simple coroutine function

```python
import asyncio

async def hello():
    print('Hello Task!')

coroutine = hello()
asyncio.get_event_loop().run_until_complete(coroutine)
```

^ If the `hello` function was not defined with `async def`, it would implicitly return `None`. Instead, it returns a coroutine object.

---
# Return values of coroutine functions

```python
import asyncio

async def add(x, y):
    await asyncio.sleep(2)
    return x + y

async def main():
    return_value = await add(4, 7)
    print(return_value)

asyncio.get_event_loop().run_until_complete(main())
```

^ You can only access the return value of a coroutine function inside another coroutine function, and only via the use of an `await` expression.

---
# What is a task?

In an event-loop-based program, you primarily use tasks instead of threads to implement concurrency.

"Don’t directly create Task instances: use the `ensure_future()` function or the `AbstractEventLoop.create_task()` method."

^ Source: https://docs.python.org/3/library/asyncio-task.html#task

^ The `asyncio.Task` class has a very similar API to that of the `concurrent.futures.Future` class.

---
# A simple task

```python
import asyncio

async def hello():
    print('Hello Task!')

asyncio.ensure_future(hello())
asyncio.get_event_loop().run_forever()
```

^ Here, the `asyncio.ensure_future()` function schedules the execution of the given coroutine object, wraps it in a task, and returns the task.

^ You should generally use `asyncio.ensure_future()` over `AbstractEventLoop.create_task()` since the former accepts any awaitable object, while the latter only accepts coroutine objects.

---
# Types of tasks we'll talk about today

- Asynchronous
- Synchronous (using ThreadExecutor)
- Inside web socket handler
- Inside a separate process

^ Note that from this point on, when we refer to a "task", we are talking about the general sense of the word, i.e. a long-running operation, as opposed to an instance of the `asyncio.Task` class.

---
# Asynchronous task

The default type of task that asyncio supports. You define it using a coroutine function, and schedule it using the `asyncio.ensure_future()` function.

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
