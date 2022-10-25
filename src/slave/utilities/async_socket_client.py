"""Implementazione delle funzioni asincrone per la gestione del client (bot slave)."""
# import time
import asyncio
import bot_slave_utilities as bot_utils


HOST = "127.0.0.1"
PORT = 9999
__response_options = {"1": "OS-TYPE",
                      "2": "RAM",
                      "3": "PROCESSOR-NAME",
                      "4": "CORES-NUMBER",
                      "5": "CPU-FREQ",
                      "6": "PARTITION-DISK-INFO",
                      "7": "PARTITION-DISK-STATUS",
                      "8": "IO-CONNECTED",
                      "9": "NETWORK-INFO",
                      "10": "SENSORS",
                      "15": "DOWNLOAD-FILE"}


# Passiamo alla funzione anche il writer in modo da poter ciclare sui vari oggetti (in particolare dischi e schede di rete)
async def command_to_execute(writer: asyncio.StreamWriter, case: str) -> None:
    """Gestione dell'operazione impartita dal master da eseguire."""
    match case:
        case 'OS-TYPE':
            writer.write(bot_utils.get_operating_system().encode())
        case 'RAM':
            return bot_utils.get_ram_size()
        case 'PROCESSOR-NAME':
            writer.write(bot_utils.get_processor_name().encode())
        case 'CORES-NUMBER':
            writer.write(bot_utils.get_cores_number().encode())
        case 'CPU-FREQ':
            writer.write(bot_utils.get_cpu_min_max_freq().encode())
        case 'PARTITION-DISK-INFO':
            for partition in bot_utils.get_partition_disk_info():
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
        case _:
            return "NULL"


async def run() -> None:
    """Comunicazione con il server attraverso le socket. In base alle richieste impartite dal server il client esegue diverse operazioni."""
    reader, writer = await asyncio.open_connection(HOST, PORT)
    operation_keyword = "Operazione?"

    await asyncio.sleep(1)
    writer.write(operation_keyword.encode())
    await writer.drain()
    while True:
        response = await reader.read(1024)
        if not response:
            raise Exception("Socket closed!")
        print(f"Received from server: {response.decode()!r}")
        if response.decode() in __response_options.values():  # Controlliamo che il valore ottenuto matchi con qualche operazione presente nel dizionario
            """
            In questo momento il client invia al loop una nuova richiesta da effettuare. In questo punto invece andrà effettuata l'invocazione corrispondente
            al metodo
            TODO: Aggiungere CASE STATEMENT
            """
            await command_to_execute(writer, response.decode())
            await asyncio.sleep(1)
            writer.write(operation_keyword.encode())
        else:  # In caso contrario chiediamo al server di inviare una nuova risposta valida
            writer.write(operation_keyword.encode())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
