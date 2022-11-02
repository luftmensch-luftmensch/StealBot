"""Utilities per la gestione della network."""
# TODO: https://nmap.readthedocs.io/en/latest/
import psutil
from socket import AddressFamily
import nmap3
import re


def get_net_ifname() -> dict:
    """Recupero lista ifname."""
    return [{key: value[0].address} for key, value in psutil.net_if_addrs().items()
            if value[0].family == AddressFamily.AF_INET and key != 'lo'][0]


def network_scan(ifname: dict):
    """Recupero degli ip presenti sulla stessa rete."""
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    nmap = nmap3.NmapScanTechniques()
    """
    Dal dict prendiamo l'ip che deve essere splittato (otteniamo una lista) e con join la ricomponiamo escludendo l'ultimo carattere che verrà sostituito con 0/24 (in modo da poterci iterare con nmap)
    """
    result = nmap.nmap_ping_scan('192.168.1.0/24')  # TODO: Modificare e rendere generalizzato
    for key, value in result.items():
        if(re.search(regex, key) and value.get('state').get('state') == 'up'):  # Visto che nmap è un dizionario ricorsivo recuperiamo soltanto gli host che sono attivi
            print(f"Key -> {key}, Value: {value.get('state').get('state')}")
