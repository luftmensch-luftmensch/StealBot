"""Bot master source code."""

# Definizione dei moduli
import sys

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
from database import database_handler as db

# Definzione variabili globali
hostname = "localhost"  # TODO: Da sostituire in prod
PORT = 9090  # TODO: Da cambiare in corso d'opera (?)


if __name__ == "__main__":
    bot_master.welcome_message("Benvenuto!")
    bot_master.SignalHandler.__init__()  # Gestione del keyboard interrupt

    if (bot_master.port_validator(hostname, PORT) is True):
        print("Currently PORT n° ", PORT, "is used!", "\nExiting the program!")
        sys.exit(1)
    else:
        print("Currently PORT n° ", PORT, "is not used yet!",
              "\nStarting the web server!")

    database_handler = db.DatabaseHandler()  # Inizializzazione automatica del database
