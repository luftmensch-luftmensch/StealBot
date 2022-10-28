"""Bot master source code."""
# Definizione dei moduli
import asyncio
import click
# import sys

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
from utilities import async_socket_server as async_server
# from utilities import database_handler as db


def init_handlers(hostname: str, port: int):
    """Inizializzazione degli handler (tastiera e porta in uso)."""
    bot_master.SignalHandler.__init__()  # Gestione del keyboard interrupt

    if (bot_master.port_validator(hostname, port) is True):
        bot_master.info(f"Al momento la porta {port} è in utilizzo!! Uscita dal programma in corso!", 3)  # Log Level: Error
    else:
        bot_master.info(f"Al momento la porta {port} è libera! Inizializzazione del server!", 1)


def main():
    """Funzione main eseguita all'avvio dello script."""
    bot_master.welcome_message("Steal Bot")


@click.command()
@click.option("--host", default='127.0.0.1', help="Host su cui deve essere esposto il service")
@click.option("--port", default=9090, type=int, help="Porta sulla quale deve mettersi in ascolto il service")
def start(host: str, port: int):
    """Funzione di esecuzione del server."""
    init_handlers(host, port)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_server.run_server(host, port))


if __name__ == "__main__":
    main()
    start()  # Di default verrà eseguito su localhost:9090. Per modificare il comportamento è possibile eseguire lo script con `python main.py --host='XXX.XXX.XXX.XXX' --port='XXXX'
    # database_handler = db.DatabaseHandler()  # Inizializzazione automatica del database
