"""Implementazione delle funzioni asincrone per la gestione del server (bot master)."""
import asyncio  # Non è necessario importare anche socket (asyncio lo fa da solo)
from aioconsole import ainput  # Async console per asyncio
import aiofiles


HOST = "127.0.0.1"
PORT = 9999
__response_options = {"1": "OS-TYPE", "2": "RAM", "3": "DISK", "4": "USER", "5": "STATUS", "6": "IO-CONNECTED", "7": "NETWORK-INFO", "8": "DOWNLOAD-FILE"}


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
    while response != stop_key.encode():  # Eseguiamo fin tanto che non riceviamo dal client "quit"
        response = await reader.read(1024)
        if not response:
            test_addr, test_port = writer.get_extra_info("peername")
            print(f"Il client {test_addr}:{test_port} ha effettuato una connessione di test per la verifica dello stato del server")
            break
        if response == b"Operazione?":  # Se la response è vuota eseguiamo un comando da inviare al client che si tradurrà in una operazione
            print_menu(__response_options, "Operazioni disponibili:", 32)
            request = await ainput(">>> ")  # TODO: al momento non la usiamo -> Punto ad aggiungere una serie di funzioni/cases per la richiesta da effettuare al client
            if request in __response_options.keys():
                print(f"Opzione scelta: {request}")
                chosen_operation = __response_options.get(request)
                writer.write(chosen_operation.encode())
                await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
            else:
                chosen_operation = "OPERATION_NOT_SUPPORTED"  # Testing nel caso in cui niente di quello inserito dall'utente matchi
                writer.write(chosen_operation.encode())
                await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
        else:
            msg = response.decode()
            addr, port = writer.get_extra_info("peername")
            print(f"Message from {addr}:{port}: {msg!r}")  # Sfruttiamo il Literal String Interpolation (F-String)
            writer.write(msg.encode())
            await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    writer.close()
    await writer.wait_closed()  # Attendiamo che il client sia chiuso prima di stoppare


async def run_server() -> None:
    """Esecuzione del loop di gestione della connessione con il client."""
    server = await asyncio.start_server(handle_bot_client, HOST, PORT)

    async with server:
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_server())
