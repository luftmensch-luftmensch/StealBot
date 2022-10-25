"""Funzioni custom per il bot slave."""

import socket
# from time import sleep
from cpuinfo import get_cpu_info
import psutil
# import requests
import platform

# TODO: Aggiungere ai metodi il tipo di ritorno


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


def get_cpu_min_max_freq() -> str:
    """Recupero frequenza min/max della cpu."""
    min_cpu_freq = psutil.cpu_freq().min
    max_cpu_freq = psutil.cpu_freq().max
    return f"{min_cpu_freq:.2f}, {max_cpu_freq:.2f}"


def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format."""
    """e.g: 1253656 => '1.20MB' 1253656678 => '1.17GB'"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


# NB: È obbligatorio fare un loop per ottenere le info di ogni partizione
def get_partition_disk_info():  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni del disco."""
    # partition_usage = psutil.disk_usage(partition.mountpoint)
    # print(f"  Total Size: {get_size(partition_usage.total)}")
    # print(f"  Used: {get_size(partition_usage.used)}")
    # print(f"  Free: {get_size(partition_usage.free)}")
    # print(f"  Percentage: {partition_usage.percent}%")
    return psutil.disk_partitions()


def get_io_disk_statistics() -> str:
    """Recupero statistiche I/O del disco."""
    # get IO statistics since boot
    return f"Letture: {get_size(psutil.disk_io_counters().read_bytes)}, Scritture: {get_size(psutil.disk_io_counters().write_bytes)}"


def get_network_info() -> str:  # TODO: Controllare che funzioni anche con altri OS
    """Recupero informazioni sulla rete."""
    return psutil.net_if_addrs()


def get_sensors_statistics():
    """Recupero statistche sui sensori."""
    # TODO: Sfrutta le funzioni di psutil sensors_battery(), sensors_fan(), sensors_temperatures()


# TODO: Modificare o espandere
def get_hostname():
    """Recupero info hostname."""
    return socket.gethostname()


def get_operating_system() -> str:
    """Recupero informazioni del SO in esecuzione sulla macchina."""
    # simple_operating_system = platform.uname().system  # example: Linux
    # Ritorniamo il campo con il maggior numero di informazioni possibili
    # TODO: Da testare con altri OS
    # platform_operating_system = platform.platform()  # example: Linux-5.15.0-50-generic-x86-64-with-glib2.35
    return platform.platform()


# if __name__ == "__main__":
#     # TODO: Aggiungere anche un controllo sui tentativi?
#     while test_connection("127.0.0.1", 9999) is False:
#         print("Il server non è attualmente raggiungibile.")
#         sleep(1)
