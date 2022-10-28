"""Bot slave source code."""
# Definizione dei moduli
import asyncio
import click
from time import sleep

from utilities import bot_slave_utilities as bot_slave
from utilities import async_socket_client as async_client


@click.command()
@click.option("--host", default='127.0.0.1', help="Host su cui deve essere esposto il service")
@click.option("--port", default=9090, type=int, help="Porta sulla quale deve mettersi in ascolto il service")
def start(host: str, port: int):
    """Funzione di esecuzione del client."""
    while bot_slave.test_connection(host, port) is False:
        print("Il server non è attualmente raggiungibile.")
        sleep(1)  # TODO: Trovare un modo di ritornare nel loop nel caso in cui venga chiusa la connessione per permettere la riconnessione
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_client.run_client(host, port))


if __name__ == "__main__":
    start()  # Di default verrà eseguito su localhost:9090. Per modificare il comportamento è possibile eseguire lo script con `python main.py --host='XXX.XXX.XXX.XXX' --port='XXXX'
