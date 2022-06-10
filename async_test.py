import asyncio
from datetime import datetime
from operator import rshift
import time
from turtle import back
import concurrent.futures
from typing import final


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def nested():
    return 42

async def main():
    task = asyncio.create_task(nested())
    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await(task)

    print(f"finished at {time.strftime('%X')}")

background_tasks = set()
for i in range(10):
    task = asyncio.create_task(nested(param=i))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

async def display_date():
    loop = asyncio.get_running_loop()
    end_time = loop.time() + 5.0
    while True:
        print(datetime.datetime.now())
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(1)

def blocking_io():
    with open('/dev/urandom', 'rb') as f:
        return f.read(100)

def cpu_bound():
    return sum(i * i for i in range(10 ** 7))

async def test_main():
    loop = asyncio.get_running_loop()

    result = await loop.run_in_executor(
        None, blocking_io)
    print('default thread pool', result)

    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, blocking_io)
        print('custom thread pool', result)
    
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
        pool, cpu_bound)
        print('custom process pool', result)

async def cancel_me():
    print('cancel_me(): before sleep')

    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print('cancel_me(): cancel sleep')
        raise
    finally:
        print('cancel_me()')

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    
    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client('Hello World'))


asyncio.run(main(), debug=True)
asyncio.run(display_date())
asyncio.run(test_main())


