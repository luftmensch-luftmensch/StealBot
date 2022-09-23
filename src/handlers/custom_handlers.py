"""Custom Handlers for various tasks."""
import signal
import sys
import os
# import socket
# import threading

import http.server  # Our http server handler for http requests
# import socketserver # Establish the TCP Socket connections


class SignalHandler:
    """Classe Handler per la gestione dei segnali."""

    def keyboard_handler(signal, frame):
        """Gestione del segnale di  KeyboardInterrupt."""
        print('\nkeyboardInterrupt detected!')
        print('\nStopping the service...')
        sys.exit(0)

    @classmethod
    def __init__(self):
        """Init class."""
        signal.signal(signal.SIGINT, self.keyboard_handler)


class CustomHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler per la richiesta HTTP effettuata da un client al server."""

    # def do_GET(self):
    #     self.path = 'index.html'
    #     print("PATH" + self.path)
    #     return http.server.SimpleHTTPRequestHandler.do_GET(self)
    """
    Mapping incoming request:
    https://stackoverflow.com/questions/18346583/how-do-i-map-incoming-path-requests-when-using-httpserver
    """
    def do_GET(self):
        """Get homepage."""
        rootdir = os.getcwd() + '/src/site/'
        try:
            if os.path.exists(os.path.join(rootdir, "index.html")):
                # Open file as bytes-like object
                f = open(os.path.join(rootdir, "index.html"), 'rb')
                self.send_response(200)

                self.send_header('Content-type', 'text-html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return  # http.server.SimpleHTTPRequestHandler.do_GET(self)
                # for filename in os.listdir(rootdir):
                #     print(os.path.join(rootdir, filename))
                # if self.path.endswith('.html'):
                #     f = open(rootdir + self.path)  # open requested file
                #     print("FILE ", f)

                #     # send code 200 response
                #     # self.send_response(200)

                #     # send header first
                #     # self.send_header('Content-type','text-html')
                #     # self.end_headers()

                #     # send file content to client
                #     self.wfile.write(f.read())
                #     f.close()
                #     # return
                #     return http.server.SimpleHTTPRequestHandler.do_GET(self)
        except IOError:
            self.send_error(404, 'file not found')
