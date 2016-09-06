import asyncio


async def hello():
    print('Hello Task!')


coroutine = hello()
asyncio.get_event_loop().run_until_complete(coroutine)
