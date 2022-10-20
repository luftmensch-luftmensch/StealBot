"""TODO."""
import time
import asyncio

HOST = "127.0.0.1"
PORT = 9999


async def run_client() -> None:
    """Comunicazione con il server attraverso le socket. In base alle richieste impartite dal server il client esegue diverse operazioni."""
    reader, writer = await asyncio.open_connection(HOST, PORT)

    writer.write(b"Hello world")
    await writer.drain()

    messages = 5
    while True:
        data = await reader.read(1024)
        if not data:
            raise Exception("socket closed")

        print(f"Received: {data.decode()!r}")
        if messages > 0:
            await asyncio.sleep(1)
            writer.write(f"{time.time()}".encode())
            await writer.drain()
            messages -= 1
        else:
            writer.write(b"quit")
            await writer.drain()
            break

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_client())
