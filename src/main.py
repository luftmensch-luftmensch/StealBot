"""Basic web server written in python."""
from handlers import custom_handlers as handler

# import socket
# import signal
import sys
# import threading
# import os

# import http.server # Our http server handler for http requests
# import socketserver # Establish the TCP Socket connections

# Generate welcome message with ASCII text
# More at https://github.com/pwaller/pyfiglet
import pyfiglet

PORT = 9090


def welcome_message(message: str):
    """Welcome message function with pyfiglet."""
    print(pyfiglet.figlet_format(message))


def check_before_run(hostname: str, port: int):
    """Check if the requisite are respected."""
    print("Checking hardware requisite availability...")
    checker = handler.SocketChecker
    if (checker.is_port_in_use(hostname, port) is True):
        print("Currently PORT n° ", port, "is used!", "\nExiting the program!")
        sys.exit(1)
    else:
        print("Currently PORT n° ", port, "is not used yet!",
              "\nStarting the web server!")


# with socketserver.TCPServer(("", PORT), Handler) as httpd:
#     print("Http Server Serving at port", PORT)
#     httpd.serve_forever()


if __name__ == "__main__":
    welcome_message("Welcome !")
    try:
        PORT = int(input("Please enter the PORT to start the server : "))
    except Exception:
        print("The PORT number must be valid!")
        sys.exit(1)

    check_before_run('localhost', PORT)

    # Starting the handler to catch keyboard interrupt
    # in order to stop it gracefully
    handler.SignalHandler.__init__()
    # Handler = hrh.CustomHttpRequestHandler
