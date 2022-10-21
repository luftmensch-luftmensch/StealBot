"""Implementazione delle funzioni asincrone per la gestione del client (bot slave)."""
# import time
import asyncio

HOST = "127.0.0.1"
PORT = 9999
__response_options = {"1": "OS-TYPE", "2": "RAM", "3": "DISK", "4": "USER", "5": "STATUS", "6": "IO-CONNECTED", "7": "NETWORK-INFO", "8": "DOWNLOAD-FILE"}


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
            print("Response match!")
            """
            In questo momento il client invia al loop una nuova richiesta da effettuare. In questo punto invece andrà effettuata l'invocazione corrispondente
            al metodo
            """
            writer.write(operation_keyword.encode())
        else:  # In caso contrario chiediamo al server di inviare una nuova risposta valida
            writer.write(operation_keyword.encode())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
