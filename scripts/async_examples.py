#
#   scraper_server.py
#   ~~~~~~~~~~~~~~~~~
#
#   Servers to periodically run collectors
#
import yaml
import asyncio
import time

async def main_sync():
    print('Hello ...')
    await asyncio.sleep(1)
    print('... World!')

# asyncio.run(main_sync())

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main_async():
    task1 = asyncio.create_task(say_after(1, 'hello'))

    task2 = asyncio.create_task(say_after(2, 'world'))

    print(f"finished at {time.strftime('%X')}")

    # Wait until both tasks are completed ~ 2s
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")

# asyncio.run(main_async())

if __name__ == "main":

    print('Syncronous')
    asyncio.run(main_sync())

    print('Asyncronous')
    asyncio.run(main_async())
