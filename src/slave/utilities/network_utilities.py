"""Utilities per la gestione della network."""
# TODO: ettps://nmap.readthedocs.io/en/latest/
import psutil
from socket import AddressFamily
import nmap3


def get_net_ifname() -> dict:
    """Recupero lista ifname."""
    return [{key: value[0].address} for key, value in psutil.net_if_addrs().items()
            if value[0].family == AddressFamily.AF_INET and key != 'lo'][0]


def network_scan(ifname: dict):
    """Recupero degli ip presenti sulla stessa rete."""
    nmap = nmap3.NmapScanTechniques()
    print(nmap)
    """
    Dal dict prendiamo l'ip che deve essere splittato (otteniamo una lista) e con join la ricomponiamo escludendo l'ultimo carattere che verrà sostituito con 0/24 (in modo da poterci iterare con nmap)
    """
    # TODO: Calcolare la netmask a partire dal'ip e il corrispettivo range di valori possibili
