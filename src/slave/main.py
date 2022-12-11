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
import uuid

# Librerie personali
from utilities import bot_slave_utilities as bot_slave
from utilities import async_socket_client as async_client
from utilities import network_utilities as net_utils

__dispatcher_buf_size = 150
bot_status = {1: "Connecting", 2: "Connected"}


@click.command()
@click.option("--host", default='127.0.0.1', help="Host su cui deve essere esposto il service")
@click.option("--port", default=9090, type=int, help="Porta sulla quale deve mettersi in ascolto il service")
@click.option("--finder", "-f", is_flag=True, help="Settiamo il client in finder mode in modo da poter ricercare sulla rete il master")
@click.option("--retrieve_port", "-r", is_flag=True, help="Recupero della porta da utilizzare per la connessione al server")
def start(host: str, port: int, finder: bool, retrieve_port: bool):
    """Funzione di esecuzione del client."""
    node = uuid.uuid4().hex  # Custom uuid for the client

    bot_slave.info(f"Identificativo della macchina {node}", 1)

    # Gestione recupero della porta alla quale il client dovrà collegarsi
    if retrieve_port:
        while True:
            if bot_slave.test_connection(host, port) is False:
                # print("Il server non è attualmente raggiungibile.")
                bot_slave.info(f"Il dispatcher ({host}:{port}) non è attualmente raggiungibile", 2)
                sleep(5)
            else:
                port = bot_slave.retrieve_port(host, port, node, __dispatcher_buf_size)  # Definiamo una nuova porta che il client dovrà utilizzare
                bot_slave.info(f"Porta assegnata dal dispatcher {port}", 1)
                break
    if finder:
        host = net_utils.find_bot_master(port)  # Ricerca automatica del server sulla rete locale

    current_status = bot_status.get(1)

    while True:
        if current_status == bot_status.get(1):
            if bot_slave.test_connection(host, port) is True:  # Controlliamo che il server sia in esecuzione
                current_status = bot_status.get(2)
            else:
                # print("Il server non è attualmente raggiungibile.")
                bot_slave.info(f"Il server ({host}:{port}) non è attualmente raggiungibile", 2)
                sleep(5)
        elif current_status == bot_status.get(2):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(async_client.run_client(host, port))  # Gestione della connessione con il server
            current_status = bot_status.get(1)
            sleep(4)


if __name__ == "__main__":
    start()  # Di default verrà eseguito su localhost:9090. Per modificare il comportamento è possibile eseguire lo script con `python main.py --host='XXX.XXX.XXX.XXX' --port='XXXX' -f/--finder --retrieve_port/-r
