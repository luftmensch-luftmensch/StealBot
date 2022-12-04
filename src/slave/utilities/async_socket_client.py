"""
Codice sorgente per la gestione della connessione con il server (bot-client).

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import asyncio
import re
from . import bot_slave_utilities as bot_utils

__response_options = {"1": "OS-TYPE", "2": "CPU-STATS", "3": "RAM", "4": "PARTITION-DISK-INFO", "5": "PARTITION-DISK-STATUS",
                      "6": "NETWORK-INFO", "7": "USERS", "8": "DOWNLOAD-FILE", "9": "Content-Path", "q": "QUIT"}

__file_range_header = {1: "<Range-File>", 2: "<File-Name>"}

__buffer_size = 8192


# Passiamo alla funzione anche il writer in modo da poter ciclare sui vari oggetti (in particolare dischi e schede di rete)
async def command_to_execute(writer: asyncio.StreamWriter, case: str) -> None:
    """Gestione dell'operazione impartita dal master da eseguire."""
    match case:
        case 'OS-TYPE':
            writer.write(bot_utils.get_operating_system())  # Per semplicità andiamo a parametrizzare gli oggetti separandoli con gli __headers_type

        case 'CPU-STATS':
            writer.write(bot_utils.get_cpu_information())

        case 'RAM':
            writer.write(bot_utils.get_ram_size())

        case 'PARTITION-DISK-INFO':
            await bot_utils.get_partition_disk_info(writer)

        case 'PARTITION-DISK-STATUS':
            writer.write(bot_utils.get_io_disk_statistics())

        case 'NETWORK-INFO':
            await bot_utils.get_network_info(writer)

        case 'USERS':
            await bot_utils.get_users(writer)

        case _:
            return "NULL"


async def run_client(hostname: str, port: int) -> None:
    """Comunicazione con il server attraverso le socket. In base alle richieste impartite dal server il client esegue diverse operazioni."""
    reader, writer = await asyncio.open_connection(hostname, port)
    operation_keyword = "Operazione?"

    await asyncio.sleep(1)
    writer.write(operation_keyword.encode())
    await writer.drain()
    while True:
        response = await reader.read(__buffer_size)
        if not response:
            raise Exception("Socket closed!")
        print(f"Received from server: {response.decode()!r}")
        if response.decode() in __response_options.values():  # Controlliamo che il valore ottenuto matchi con qualche operazione presente nel dizionario
            """
            In base a quello ottenuto dal server il client effettuerà l'operazione corrispondente
            """
            # Nel caso in cui il server chieda di quittare inviamo la conferma di quit al server e interrompiamo il loop
            if response.decode() == "QUIT":
                writer.write(b"quit")
                await writer.drain()
                break
            else:
                await command_to_execute(writer, response.decode())
                await asyncio.sleep(1)
                writer.write(operation_keyword.encode())

        elif response.decode().startswith(__response_options["8"]):
            request = re.split(__response_options["8"], response.decode())[1]  # -> In questo punto facciamo stripping della request ricevuta dal server e controlliamo se esiste sul disco il file richiesto
            print(request)
            await bot_utils.send_file(request, __buffer_size, writer)  # Spostiamo la gestione del controllo di esistenza del file all'interno della funzione stessa
            writer.write(operation_keyword.encode())

        elif response.decode().startswith(__response_options["9"]):
            request = re.split(__response_options["9"], response.decode())[1]
            await bot_utils.send_dir_content(request, writer)
            writer.write(operation_keyword.encode())

        # Gestione del recupero di un range di file
        elif response.decode().startswith(__file_range_header[1]):
            request = re.split(__file_range_header[1], response.decode())
            print(f"Request before: {request}")
            while ("" in request):
                request.remove("")
            print(f"Request after: {request}, type: {type(request)}, len: {len(request)}")

            final_request = re.split(__file_range_header[2], request[0])  # TODO: Trovare un modo di fondere lo split

            print(f"Final Request before: {final_request}")
            while ("" in final_request):
                final_request.remove("")
            print(f"Final Request after: {final_request}")

            # TODO: Richiamare il recupero del file ciclando sulla lista final_request

            writer.write(operation_keyword.encode())
        else:  # In caso contrario chiediamo al server di inviare una nuova risposta valida
            writer.write(operation_keyword.encode())
