"""Basic web server written in python."""
from handlers import custom_handlers as handler

import socket
# import signal
import sys
# import socketserver
# import threading
# import os
from http.server import HTTPServer

# import http.server # Our http server handler for http requests
# import socketserver # Establish the TCP Socket connections

# Generate welcome message with ASCII text
# More at https://github.com/pwaller/pyfiglet
import pyfiglet

hostname = "localhost"
PORT = 9090


def welcome_message(message: str):
    """Welcome message function with pyfiglet."""
    print(pyfiglet.figlet_format(message))


def port_validator(hostname: str, port: int) -> bool:
    """Check if the requisite are respected."""
    """
    Cannot bind to ports below 1024 without
    the CAP_NET_BIND_SERVICE capability.
    """
    print("Checking if PORT n° {:d} is valid for the user" .format(PORT))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        """If the port selected is not used the connect_ex return false"""
        return s.connect_ex((hostname, port)) == 0


if __name__ == "__main__":
    welcome_message("Welcome !")
    try:
        PORT = int(input("Please enter the PORT to start the server : "))
        if (1 < PORT < 1024):
            raise Exception
    except Exception:
        print("The PORT number must be valid!")
        sys.exit(1)

    # Starting the handler to catch keyboard interrupt
    # in order to stop it gracefully
    handler.SignalHandler.__init__()

    if (port_validator(hostname, PORT) is True):
        print("Currently PORT n° ", PORT, "is used!", "\nExiting the program!")
        sys.exit(1)
    else:
        print("Currently PORT n° ", PORT, "is not used yet!",
              "\nStarting the web server!")

    webServer = HTTPServer((hostname, PORT), handler.CustomHttpRequestHandler)
    print("Http Server serving at http://%s:%d" % (hostname, PORT))
    webServer.serve_forever()
    # with socketserver.TCPServer(("", PORT), HTTPHandler) as httpd:
    #     print("Http Server Serving at port", PORT)
    #     httpd.serve_forever()
