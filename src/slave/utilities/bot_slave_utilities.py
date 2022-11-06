"""
Codice sorgente contenente funzioni di supporto per il bot-slave.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
# Librerie globali
import socket
from cpuinfo import get_cpu_info
import psutil
import platform
import asyncio
# from functools import partial  # Per comodità leggiamo il file da inviare in chunk di dati -> Sostituito con un iteratore
# from time import sleep

# Definiamo degli header custom per identificare il tipo di dato inviato al server
__headers_type = {"1": b"<File-Name>", "2": b"<File-Content>", "3": b"<OS-type>", "4": b"<CPU-stats>", "5": b"<Ram-usage>",
                  "6": b"<Partition-disk-info>", "7": b"<Partition-disk-status>", "8": b"<IO-connected>", "9": b"<Network-info>", "10": b"<Users>"}


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


def get_cpu_information() -> str:
    """Recupero informazioni sulla cpu della macchina."""
    # cpu_info = get_cpu_info()  # json with processor information
    # CPU Brand
    cpu_brand = get_cpu_info()['brand_raw']
    # Core info
    logical_core = psutil.cpu_count()
    physical_core = psutil.cpu_count(logical=False)

    # CPU Freq info
    min_cpu_freq = psutil.cpu_freq().min
    max_cpu_freq = psutil.cpu_freq().max
    # return platform.system()  #   # return only cpu name
    return f"CPU: {cpu_brand}, CPU count: {physical_core}, CPU count (logical): {logical_core}, Min freq: {min_cpu_freq:.2f}, Max freq: {max_cpu_freq:.2f}"


async def send_file(request: str, size: int, writer: asyncio.StreamWriter):
    """Invio di uno specifico file dal client al server."""
    # Calcoliamo una dimensione che rispetti il pacchetto che stiamo inviando al client (TODO per Valentino: Spostarlo in un posto migliore e passarlo direttamente alla funzione!)
    size_after = size - len(__headers_type["1"]) - len(__headers_type["2"]) - (len(request))
    with open(request, 'rb') as filename:
        for chunk in iter(lambda: filename.read(size_after), ""):
            if chunk:
                # L'ogetto che riceverà il client sarà del tipo <File-Name>NOME_FILE<File-Content>CONTENUTO_FILE
                writer.write(__headers_type["1"] + request.encode() + __headers_type["2"] + chunk)
                await asyncio.sleep(2)  # Controllare se sia possibile diminuire lo sleep (o se sia invece obbligatorio aumentarlo)
                print(f"Sent: {len(chunk)} bytes")
            else:
                break


def get_ram_size() -> str:
    """Recupero informazioni ram della macchina."""
    total_mem = psutil.virtual_memory().total
    used_mem = psutil.virtual_memory().used
    return f"Ram used: {get_size(used_mem)} / {get_size(total_mem)}"


def get_size(bytes, suffix="B") -> str:
    """Conversione di bytes in un formato Human readable."""
    """e.g: 1253656 => '1.20MB' 1253656678 => '1.17GB'"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


# NB: È obbligatorio fare un loop per ottenere le info di ogni partizione
def get_partition_disk_info() -> list:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni del disco."""
    return psutil.disk_partitions()


def get_io_disk_statistics() -> str:
    """Recupero statistiche I/O del disco."""
    # get IO statistics since boot
    return f"Letture: {get_size(psutil.disk_io_counters().read_bytes)}, Scritture: {get_size(psutil.disk_io_counters().write_bytes)}"


def get_network_info() -> str:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni sulla rete."""
    return psutil.net_if_addrs()


# TODO: Modificare o espandere
def get_hostname() -> str:
    """Recupero info hostname."""
    return socket.gethostname()


def get_users() -> list:
    """Recupero della lista degli utenti presenti sulla macchina ospite."""
    return psutil.users()


def get_operating_system() -> str:
    """Recupero informazioni del SO in esecuzione sulla macchina."""
    # TODO: Da testare con altri OS
    # Ritorniamo il campo con il maggior numero di informazioni possibili
    return platform.platform()  # example: Linux-5.15.0-50-generic-x86-64-with-glib2.35
