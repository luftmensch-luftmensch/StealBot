"""Example async task to read file."""
import asyncio

from concurrent.futures import ThreadPoolExecutor

e = ThreadPoolExecutor()


async def read_file(file_):
    """Lettura file."""
    loop = asyncio.get_event_loop()

    with open(file_) as f:

        return (await loop.run_in_executor(e, f.read))


ret = asyncio.run(read_file('/etc/passwd'))

print(ret)
