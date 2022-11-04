"""
Codice sorgente contenente funzioni di supporto (networking) per il bot-slave.

Scritto da:
       Valentino Bocchetti, Valentina Annunziata
       Francesco Ciccarelli, Giulia Caputo
Copyright (c) 2022. All rights reserved.
"""
import psutil
from socket import AddressFamily
import typing
import ipaddress
# Librerie personali
from . import bot_slave_utilities as bot_utils


def get_net_ifname() -> dict:
    """Recupero lista ifname."""
    return [{key: value[0].address} for key, value in psutil.net_if_addrs().items()
            if value[0].family == AddressFamily.AF_INET and key != 'lo'][0]


def get_hosts(net: str) -> typing.List[str]:
    """Recupero di tutti gli indirizzi validi data una subnet."""
    print("Network to scan:", net)
    network = ipaddress.IPv4Network(net)
    hosts_obj = network.hosts()
    print("Prefix to scan:", network.prefixlen)
    hosts = []
    for i in hosts_obj:
        hosts.append(str(i))
    print(f"Number of hosts to scan: {len(hosts)}")
    return hosts


def get_list_active_hosts(hosts: list) -> list:
    """Recupero di tutti gli host attivi che accettano una connessione sulla porta richiesta."""
    active_hosts = []
    for host in hosts:
        # TODO: Velocizzare il testing (magari facendolo a batteria) e diminuendo il timeout
        if bot_utils.test_connection(host, 9090) is True:
            print(f"L'host {host} è raggiungibile sulla porta 9090")
            hosts.append(host)
        else:
            print(f"Socket non presente sull'host {host}")
    return active_hosts


def find_bot_master() -> None:
    """Funzione di wrapping per la ricerca del bot master sulla rete locale."""
    # TODO: Trovare un modo più pulito di ottenere l'ip + subnet da passare alla funzione get_hosts
    range = ''
    i = 0
    for ip in get_net_ifname().values():
        print(f"{ip.split('.')}")
        while i < 3:
            range += ip.split('.')[i] + '.'
            i += 1

    hosts = get_hosts(range + "0/24")
    active_hosts = get_list_active_hosts(hosts)
    print(active_hosts)
