"""Bot master source code."""

# Definizione dei moduli
import sys

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
# from database import database_handler as db

# Definzione variabili globali
hostname = "localhost"  # TODO: Da sostituire in prod
PORT = 9090  # TODO: Da cambiare in corso d'opera (?)


def init_handlers():
    """Inizializzazione degli handler (tastiera e porta in uso)."""
    bot_master.SignalHandler.__init__()  # Gestione del keyboard interrupt

    if (bot_master.port_validator(hostname, PORT) is True):
        print("Currently PORT n° ", PORT, "is used!", "\nExiting the program!")
        sys.exit(1)
    else:
        print("Currently PORT n° ", PORT, "is not used yet!",
              "\nStarting the web server!")


def socket_setup():
    """Gestione e controlli pre/post della socket."""


def main():
    """Funzione main eseguita all'avvio dello script."""
    bot_master.welcome_message("Steal Bot")


if __name__ == "__main__":
    main()
    # database_handler = db.DatabaseHandler()  # Inizializzazione automatica del database
