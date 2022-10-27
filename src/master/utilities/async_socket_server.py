"""Implementazione delle funzioni asincrone per la gestione del server (bot master)."""
import asyncio  # Non è necessario importare anche socket (asyncio lo fa da solo)
from aioconsole import ainput  # Async console per asyncio
import aiofiles

# Librerie personali
from . import bot_master_utility as bot_master_utils


HOST = "127.0.0.1"
PORT = 9999
__response_options = {"1": "OS-TYPE",
                      "2": "CPU-STATS",
                      "3": "RAM",
                      "4": "PARTITION-DISK-INFO",
                      "5": "PARTITION-DISK-STATUS",
                      "6": "IO-CONNECTED",
                      "7": "NETWORK-INFO",
                      "8": "USERS",
                      "15": "DOWNLOAD-FILE"}


async def handle_bot_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Gestione della connessione e delle richieste da effettuare al client."""
    response = None
    stop_key = "quit"
    while response != stop_key.encode():  # Eseguiamo fin tanto che non riceviamo dal client "quit"
        response = await reader.read(8192)  # Per ridurre i tempi di attesa aumentiamo il buffer
        if not response:
            test_addr, test_port = writer.get_extra_info("peername")
            print(f"Il client {test_addr}:{test_port} ha effettuato una connessione di test per la verifica dello stato del server")
            break
        if response == b"Operazione?":  # Se la response è vuota eseguiamo un comando da inviare al client che si tradurrà in una operazione
            await ask_operation(writer)
        else:
            # msg = response.decode()
            await handle_response(response)  # NB: Adesso il server scriverà tutto in un file hardcodato. Valentino poi pensa a fixare (so già come fare dw)
            # await bot_master_utils.receive_file("./test.txt", msg)
            # addr, port = writer.get_extra_info("peername")
            # print(f"Message from {addr}:{port}: {msg!r}")  # Sfruttiamo il Literal String Interpolation (F-String)
            # writer.write(msg.encode())
            # await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    writer.close()
    await writer.wait_closed()  # Attendiamo che il client sia chiuso prima di stoppare


async def handle_response(response: str) -> None:
    """Funzione di test."""
    async with aiofiles.open("test.png", "ab+") as file:
        # print(f"{msg}")
        await file.write(response)


async def ask_operation(writer: asyncio.StreamWriter) -> None:
    """Funzione di richiesta dell'operazione da inviare al client da parte del server."""
    bot_master_utils.print_menu(__response_options, "Operazioni disponibili:", 32)
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


async def run_server(hostname: str, port: int) -> None:
    """Esecuzione del loop di gestione della connessione con il client."""
    server = await asyncio.start_server(handle_bot_client, HOST, PORT)

    async with server:
        async with server:
            await server.serve_forever()
