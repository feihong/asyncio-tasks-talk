import asyncio

async def add(x, y):
    await asyncio.sleep(2)
    return x + y

async def main():
    return_value = await add(4, 7)
    print(return_value)

asyncio.get_event_loop().run_until_complete(main())
