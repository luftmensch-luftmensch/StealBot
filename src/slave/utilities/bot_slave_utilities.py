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
    attempt = 5
    result_connection_status = False
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tester:
            try:
                if attempt > 0:
                    if (tester.connect_ex((hostname, port)) == 0):
                        print(f"Il server {hostname} sulla porta {port} è attualmente raggiungibile")
                        result_connection_status = True
                        break
                    print(f"Il server {hostname} sulla porta {port} non è attualmente raggiungibile. Tentativo {attempt} di 5")
                    attempt -= 1
                else:
                    print(f"Il server {hostname} sulla porta {port} non è attualmente raggiungibile. Riprovo da 5 sec")
                    sleep(5)
            except Exception as e:
                print(e)
    return result_connection_status

#Retrevial information machine
def get_processor_name():
    cpu_info = get_cpu_info() #json with processor information
    return cpu_info['brand_raw'] #return only cpu name

def get_ram_size():
    ram_size_byte = psutil.virtual_memory() #get ram size in byte
    ram_size_gb = (ram_size_byte / 1024**3) #convert byte -> Gb
    return round(ram_size_gb) #round example: 15.65GB -> 16GB

def get_core_number():
    logical_core = psutil.cpu_count()
    physical_core = psutil.cpu_count(logical=False)
    return str(physical_core), str(logical_core)

def get_hostname():
    return socket.gethostname()

def get_public_ip():
    return requests.get('https:/api.ipify.org').text

def get_operating_system():
    simple_operating_system = platform.uname().system #example: Linux
    platform_operating_system = platform.platform() #example: Linux-5.15.0-50-generic-x86-64-with-glib2.35
    return simple_operating_system, platform_operating_system






if __name__ == "__main__":
    test_connection("127.0.0.1", 9999)
