"""Server socket with asyncio."""
import asyncio  # Non è necessario importare anche socket (asyncio lo fa da solo)
from aioconsole import ainput  # Async console per asyncio


HOST = "127.0.0.1"
PORT = 9999
__response_options = {1: "OS-TYPE", 2: "RAM", 3: "DISK", 4: "USER", 5: "STATUS", 6: "IO-CONNECTED", 7: "NETWORK-INFO", 8: "DOWNLOAD-FILE"}


def print_menu(dictionary: dict, title: str, width=int) -> None:
    """Menu di scelta per l'operazione da effettuare."""
    north_box = f'╔{"═" * width}╗'  # upper_border
    south_box = f'╚{"═" * width}╝'  # lower_border
    print(north_box)
    print(f"║ {title}")
    for item in dictionary.keys():
        print("║\t", item, '--', dictionary[item])
    print(south_box)


async def handle_bot_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Gestione della connessione e delle richieste da effettuare al client."""
    response = None
    stop_key = "quit"
    # while request != b"quit":
    while response != stop_key.encode():  # Eseguiamo fin tanto che non riceviamo dal client "quit"
        response = await reader.read(1024)
        if response == b"Operazione?":  # Se la response è vuota eseguiamo un comando da inviare al client che si tradurrà in una operazione
            print_menu(__response_options, "Operazioni disponibili:", 32)
            request = await ainput(">>>")  # TODO: al momento non la usiamo -> Punto ad aggiungere una serie di funzioni/cases per la richiesta da effettuare al client
            writer.write(request.encode())
        msg = response.decode()
        addr, port = writer.get_extra_info("peername")
        print(f"Message from {addr}:{port}: {msg!r}")  # Sfruttiamo il Literal String Interpolation (F-String)

        writer.write(msg.encode())
        await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    writer.close()
    await writer.wait_closed()  # Attendiamo che il client sia chiuso prima di stoppare


async def run_server() -> None:
    """TODO."""
    server = await asyncio.start_server(handle_bot_client, HOST, PORT)

    async with server:
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_server())
