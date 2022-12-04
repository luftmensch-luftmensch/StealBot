"""
Esecuzione del bot-slave.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
# Definizione dei moduli
import asyncio
import click
from time import sleep

# Librerie personali
from utilities import bot_slave_utilities as bot_slave
from utilities import async_socket_client as async_client
from utilities import network_utilities as net_utils

bot_status = {1: "Connecting", 2: "Connected"}


@click.command()
@click.option("--host", default='127.0.0.1', help="Host su cui deve essere esposto il service")
@click.option("--port", default=9090, type=int, help="Porta sulla quale deve mettersi in ascolto il service")
@click.option("--finder", "-f", is_flag=True, help="Settiamo il client in finder mode in modo da poter ricercare sulla rete il master")
def start(host: str, port: int, finder: bool):
    """Funzione di esecuzione del client."""
    if finder:
        net_utils.find_bot_master(port)  # Ricerca automatica del server sulla rete locale
    else:
        current_status = bot_status.get(1)

        while True:
            # TODO: Convertirlo utilizzando il match case -> https://stackoverflow.com/questions/72638083/python-match-case-dictionary-keys
            if current_status == bot_status.get(1):
                if bot_slave.test_connection(host, port) is True:
                    current_status = bot_status.get(2)
                else:
                    print("Il server non è attualmente raggiungibile.")
                    sleep(5)
            elif current_status == bot_status.get(2):
                loop = asyncio.new_event_loop()
                loop.run_until_complete(async_client.run_client(host, port))
                current_status = bot_status.get(1)
                sleep(4)  # TODO: In produzione controllare che le sleep abbiano un tempo sufficiente


if __name__ == "__main__":
    start()  # Di default verrà eseguito su localhost:9090. Per modificare il comportamento è possibile eseguire lo script con `python main.py --host='XXX.XXX.XXX.XXX' --port='XXXX'
