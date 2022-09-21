import socket
import signal
import sys
import threading
import os

import http.server # Our http server handler for http requests
import socketserver # Establish the TCP Socket connections


## Handler per la gestione del segnale di  KeyboardInterrupt ##
class SignalHandler:
  def keyboard_handler(signal, frame):
      print('\nkeyboardInterrupt detected!')
      print('\nStopping the service...')
      sys.exit(0)

  @classmethod
  def __init__(self):
      signal.signal(signal.SIGINT, self.keyboard_handler)

## Handler per la gestione della porta in fase di creazione della socket ##

class SocketChecker:
  def is_port_in_use(hostname: str, port: int) -> bool:
      import socket
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          return s.connect_ex((hostname, port)) == 0

## Handler per la richiesta HTTP effettuata da un client al server ##


class CustomHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    #def do_GET(self):
    #    self.path = 'index.html'
    #    print("PATH" + self.path)
    #    return http.server.SimpleHTTPRequestHandler.do_GET(self)

  #handle GET command  
  def do_GET(self):  
    
    print("Current directory " , os.getcwd())
    #rootdir = '../site/' # TODO: Modificare la posizione in modo da essere dinamica
    rootdir = os.getcwd() + '/src/site/'
    print("ROOTDIR " , rootdir)
    try:  

      print("SONO QUI ", rootdir + self.path)
      if self.path.endswith('.html'):  
        f = open(rootdir + self.path) #open requested file
        print("FILE " , f)
  
        #send code 200 response  
        #self.send_response(200)  
  
        ##send header first  
        #self.send_header('Content-type','text-html')  
        #self.end_headers()  
  
        #send file content to client  
        self.wfile.write(f.read())  
        f.close()  
        #return  
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    

    except IOError:  
      self.send_error(404, 'file not found')
