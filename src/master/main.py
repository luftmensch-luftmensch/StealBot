"""Bot master source code."""
# Definizione dei moduli
import asyncio
# import sys

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
from utilities import async_socket_server as async_server
# from utilities import database_handler as db

# Definzione variabili globali
HOST = "127.0.0.1"  # TODO: Da sostituire in prod
PORT = 9999  # TODO: Da cambiare in corso d'opera (?)


def init_handlers():
    """Inizializzazione degli handler (tastiera e porta in uso)."""
    bot_master.SignalHandler.__init__()  # Gestione del keyboard interrupt

    if (bot_master.port_validator(HOST, PORT) is True):
        bot_master.info(f"Al momento la porta {PORT} è in utilizzo!! Uscita dal programma in corso!", 3)  # Log Level: Error
    else:
        bot_master.info(f"Al momento la porta {PORT} è libera! Inizializzazione del server!", 1)


def main():
    """Funzione main eseguita all'avvio dello script."""
    bot_master.welcome_message("Steal Bot")


def start():
    """Funzione di esecuzione del server."""
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_server.run_server(HOST, PORT))


if __name__ == "__main__":
    main()
    init_handlers()
    start()
    # database_handler = db.DatabaseHandler()  # Inizializzazione automatica del database
