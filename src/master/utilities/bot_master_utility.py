"""Custom Handlers for various tasks."""
import signal
import sys
import socket
import asyncio
import os
# import socketserver # Establish the TCP Socket connections

# Generate welcome message with ASCII text
# More at https://github.com/pwaller/pyfiglet
import pyfiglet


class SignalHandler:
    """Classe Handler per la gestione dei segnali."""

    def keyboard_handler(signal, frame):
        """Gestione del segnale di  KeyboardInterrupt."""
        print('\nkeyboardInterrupt detected!')
        print('\nStopping the service...')
        sys.exit(0)

    @classmethod
    def __init__(self):
        """Init class."""
        signal.signal(signal.SIGINT, self.keyboard_handler)


"""
Funzioni ausiliare
"""

"""
TODO: Ampliare i values (sono quelli tra le parentesi []) con quelli specifici per MacOS (che dovrebbero essere in parte simili a quelli di Linux)
TODO: Per la gestione di recupero dati da win: https://stackoverflow.com/questions/13184414/how-can-i-get-the-path-to-the-appdata-directory-in-python
Struttura: key: [Linux, Win, MacOS]
"""
__filesystem_hierarchy = {"1": ["/", "C:/"],  # Da utilizzare in maniera non ricorsiva, ma per avere le info generali sulle directory possibili
                          "2": [f"/home/{os.getlogin()}/", "C:/NON_SO_IL_PATH"],
                          "3": [],  # SSH KEYS (Potrebbe risultare interessante copiare queste informazioni)
                          "4": [],  # Recupero immagini (?)
                          }


# Messaggio di benvenuto
def welcome_message(message: str):
    """Messaggio di benvenuto con pyfiglet."""
    print(pyfiglet.figlet_format(message))


# Funzione per il controllo di validità della porta
def port_validator(hostname: str, port: int) -> bool:
    """Controllo dei requisiti."""
    """
    Cannot bind to ports below 1024 without
    the CAP_NET_BIND_SERVICE capability.
    """
    print("Controllo che la porta n° {:d} sia valida per l'utente" .format(port))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        """If the port selected is not used the connect_ex return false"""
        return s.connect_ex((hostname, port)) == 0


def alert(msg):
    """Funzione di stampa in caso di errore."""
    print("\x1b[31m", msg, "\x1b[0m", file=sys.stderr)  # Stampiamo in rosso il messaggio di errore (in seguito resettiamo il colore a default)
    sys.exit(1)


def print_menu(dictionary: dict, title: str, width=int) -> None:
    """Menu di scelta per l'operazione da effettuare."""
    north_box = f'╔{"═" * width}╗'  # upper_border
    south_box = f'╚{"═" * width}╝'  # lower_border
    print(north_box)
    print(f"║ {title}")
    for item in dictionary.keys():
        print("║\t", item, '--', dictionary[item])
    print(south_box)


def receive_file(filename: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Funzione di ricezione file inviati dal client."""


def get_directory_list(parent_path: str):
    """Recupero info del contenuto delle directory."""
    for current_dir in os.listdir(parent_path):
        # Controlliamo di avere i permessi necessari per leggere nella directory
        if os.access(f"{parent_path}{current_dir}", os.R_OK) is True:
            print(f"Contenuto di {parent_path}{current_dir}:")
            content = os.listdir(f"{parent_path}{current_dir}")
            print(content)
        else:
            print(f"Per mancanza di permessi non viene mostrato il contenuto di {parent_path}{current_dir}")


# Da preferire in quanto non restituisce nulla nel caso in cui si stia cercando di leggere una directory senza permessi
def get_path_content(current_position: str):
    """Recupero info su directory e file."""
    for path, dirs, files in os.walk(current_position):
        for filename in files:
            print(os.path.join(path, filename))


def file_system_navigator():
    """Funzione per la navigazione delle directory presenti sul client."""
