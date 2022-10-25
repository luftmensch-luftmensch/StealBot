"""Funzioni custom per il bot slave."""

import socket
from time import sleep
from cpuinfo import get_cpu_info
import psutil
import requests
import platform


def test_connection(hostname: str, port: int) -> bool:
    """Funzione di controllo per lo stato del server (in ascolto o meno)."""
    """Variante della funzione port_validator."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tester:
        try:
            if (tester.connect_ex((hostname, port)) == 0):
                print(f"Il server {hostname} sulla porta {port} è attualmente raggiungibile")
                return True
            else:
                print(f"Il server {hostname} sulla porta {port} non è attualmente raggiungibile.")
                return False
        except Exception as e:
            print(e)


def get_processor_name():
    """Recupero informazioni della macchina."""
    cpu_info = get_cpu_info()  # json with processor information
    return cpu_info['brand_raw']  # return only cpu name


def get_ram_size():
    """Recupero informazioni ram della macchina."""
    ram_size_byte = psutil.virtual_memory()  # get ram size in byte
    ram_size_gb = (ram_size_byte / 1024**3)  # convert byte -> Gb
    return round(ram_size_gb)  # round example: 15.65GB -> 16GB


def get_core_number():
    """Recupero informazioni sui core della macchina."""
    logical_core = psutil.cpu_count()
    physical_core = psutil.cpu_count(logical=False)
    return str(physical_core), str(logical_core)


# TODO: Modificare o espandere
def get_hostname():
    """Recupero info hostname."""
    return socket.gethostname()


# Da eliminare: Lo otteniamo attraverso la connessione diretta con le socket
def get_public_ip():
    """Recupero ip della macchina."""
    return requests.get('https:/api.ipify.org').text


def get_operating_system():
    """Recupero informazioni del SO in esecuzione sulla macchina."""
    simple_operating_system = platform.uname().system  # example: Linux
    platform_operating_system = platform.platform()  # example: Linux-5.15.0-50-generic-x86-64-with-glib2.35
    return simple_operating_system, platform_operating_system


if __name__ == "__main__":
    # TODO: Aggiungere anche un controllo sui tentativi?
    while test_connection("127.0.0.1", 9999) is False:
        print("Il server non è attualmente raggiungibile.")
        sleep(1)
    for key, value in get_cpu_info().items():
        print("{0}: {1}".format(key, value))
