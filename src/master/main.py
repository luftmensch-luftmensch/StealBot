"""Bot master source code."""
# Definizione dei moduli
import sys

# Import di funzioni di libreria personale
from utilities import bot_master_utility as bot_master
# from database import database_handler as db

# Definzione variabili globali
hostname = "localhost"  # TODO: Da sostituire in prod
PORT = 9090  # TODO: Da cambiare in corso d'opera (?)
# global_response_options = ("OS-TYPE", "RAM", "DISK", "USER", "STATUS", "IO-CONNECTED", "NETWORK-INFO", "DOWNLOAD-FILE")



def print_msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    lines = msg.split('\n')
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)


def init_handlers():
    """Inizializzazione degli handler (tastiera e porta in uso)."""
    bot_master.SignalHandler.__init__()  # Gestione del keyboard interrupt

    if (bot_master.port_validator(hostname, PORT) is True):
        print("Al momento la porta {PORT} è in utilizzo!!", "\nUscita dal programma in corso!")
        sys.exit(1)
    else:
        print("Al momento la porta {PORT} è libera!",
              "\nInizializzazione del server!")


def main():
    """Funzione main eseguita all'avvio dello script."""
    bot_master.welcome_message("Steal Bot")


if __name__ == "__main__":
    main()

    # database_handler = db.DatabaseHandler()  # Inizializzazione automatica del database
