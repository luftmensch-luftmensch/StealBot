"""
Codice sorgente per la gestione della connessione con il server (bot-client).

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import asyncio
from datetime import datetime as dt
from . import bot_slave_utilities as bot_utils
# from functools import partial  # Per comodità leggiamo il file da inviare in chunk di dati

__response_options = {"1": "OS-TYPE",
                      "2": "CPU-STATS",
                      "3": "RAM",
                      "4": "PARTITION-DISK-INFO",
                      "5": "PARTITION-DISK-STATUS",
                      "6": "IO-CONNECTED",
                      "7": "NETWORK-INFO",
                      "8": "USERS",
                      "9": "DOWNLOAD-FILE",
                      "q": "QUIT"}


# Passiamo alla funzione anche il writer in modo da poter ciclare sui vari oggetti (in particolare dischi e schede di rete)
async def command_to_execute(writer: asyncio.StreamWriter, case: str) -> None:
    """Gestione dell'operazione impartita dal master da eseguire."""
    match case:
        case 'OS-TYPE':
            writer.write(bot_utils.get_operating_system().encode())
        case 'CPU-STATS':
            writer.write(bot_utils.get_cpu_information().encode())
        case 'RAM':
            writer.write(bot_utils.get_ram_size().encode())
        case 'PARTITION-DISK-INFO':
            for partition in bot_utils.get_partition_disk_info():
                if not partition.device.startswith("/dev/loop"):  # In questo modo escludiamo i mount point di snap
                    info_disk = f"{partition.device}, {partition.mountpoint}, {partition.fstype}"
                    writer.write(info_disk.encode())
                await asyncio.sleep(1)
        case 'PARTITION-DISK-STATUS':
            writer.write(bot_utils.get_io_disk_statistics().encode())
        case 'NETWORK-INFO':
            for i_name, interface_addresses in bot_utils.get_network_info().items():
                for i_addr in interface_addresses:
                    info_net = f"Intefaccia: {i_name}, IP: {i_addr.address}, Netmask: {i_addr.netmask}, Broadcast IP: {i_addr.broadcast}"
                    writer.write(info_net.encode())
                    await asyncio.sleep(1)
        case 'USERS':
            for user in bot_utils.get_users():
                user_data = f"Nome: {user.name}, Attivo da: {dt.fromtimestamp(user.started)}"
                writer.write(user_data.encode())
                await asyncio.sleep(1)
        case 'DOWNLOAD-FILE':
            await bot_utils.send_file("test.png", 8192, writer)  # TODO: Generalizza file
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
        response = await reader.read(8192)
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
        else:  # In caso contrario chiediamo al server di inviare una nuova risposta valida
            writer.write(operation_keyword.encode())
