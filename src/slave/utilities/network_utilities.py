"""Utilities per la gestione della network."""
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


def get_list_active_hosts(range: typing.List[str]) -> list:
    """Recupero di tutti gli host attivi che accettano una connessione sulla porta richiesta."""
    # TODO: Velocizzare il testing (magari facendolo a batteria)
    for host in range:
        if bot_utils.test_connection(host, 9090) is True:
            print(f"L'host {host} è raggiungibile sulla porta 9090")
        else:
            print(f"Socket non presente sull'host {host}")


if __name__ == "__main__":
    for ip in get_net_ifname().values():
        print(ip)
    # get_list_active_hosts(get_hosts(get_net_ifname()))
