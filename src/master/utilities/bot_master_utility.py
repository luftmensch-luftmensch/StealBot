"""Custom Handlers for various tasks."""
import signal
import sys
import socket
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


# Funzioni ausiliare

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
    print("Checking if PORT n° {:d} is valid for the user" .format(port))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        """If the port selected is not used the connect_ex return false"""
        return s.connect_ex((hostname, port)) == 0


def alert(msg):
    """Funzione di stampa in caso di errore."""
    print("\x1b[31m", msg, "\x1b[0m", file=sys.stderr)  # Stampiamo in rosso il messaggio di errore (in seguito resettiamo il colore a default)
    sys.exit(1)
