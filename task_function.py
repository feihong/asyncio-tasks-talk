import asyncio


async def long_task(writer):
    total = 100
    for i in range(1, total+1):
        writer.write(type='progress', value=i, total=total)
        print(i)
        await asyncio.sleep(0.05)


class Writer:
    def write(self, **kwargs):
        print(kwargs)


coroutine = long_task(Writer())
loop = asyncio.get_event_loop()
loop.run_until_complete(coroutine)
