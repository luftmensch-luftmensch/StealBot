"""Funzioni custom per il bot slave."""

import socket
from time import sleep


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


if __name__ == "__main__":
    test_connection("127.0.0.1", 9999)
