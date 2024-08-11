import urllib.parse
import json
import logging
import mimetypes
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from datetime import datetime

BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_HOST = '0.0.0.0'
HTTP_PORT = 3000
SOCKET_HOST='127.0.0.1'
SOCKET_PORT=5000
STORAGE = 'storage/data.json'

class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        if route.path == '/':
                self.send_html('index.html')
        elif route.path == '/message':
                self.send_html('message.html')
        else:
             file = BASE_DIR.joinpath(route.path[1:])
             if file.exists():
                 self.send_static(file)
             else:
                  self.send_html('error.html', status_code=404)        

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()        

    def send_html(self, filemame, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filemame, 'rb') as file:
            self.wfile.write(file.read())
    def send_static(self, filename, status_code=200):
         self.send_response(status_code)
         mime_type, _ = mimetypes.guess_type(filename)
         if mime_type:
             self.send_header('Content-Type', mime_type)
         else:
              self.send_header('Content-Type', 'text/plain')
         self.end_headers()
         with open(filename, 'rb') as file:
             self.wfile.write(file.read())

def save_message_data(data):
   # print(data)
    parse_data = urllib.parse.unquote_plus(data.decode())
   # print(parse_data)
    try:
            parser_dict ={key:value for key, value in [el.split('=')for el in parse_data.split('&')]}
            #date_to_save = {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'): parser_dict}
            load_data[datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]= parser_dict

            with open(STORAGE, 'w', encoding='utf-8') as file:
                json.dump(load_data, file, ensure_ascii=False, indent=2)
    except ValueError as e:
        logging.error(e)
    except OSError as err:
            logging.error(err)   

def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info(f'Started socket server')
    try:
        while True:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            save_message_data(data)
    except socket.error as e:
        logging.error(f'Error in socket: {e}')
    except KeyboardInterrupt:
         logging.info(f'quit')
    finally:
        server_socket.close()


def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, MyHTTPHandler)
    logging.info(f'Started http server')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()

def check_storage(storage:str)->dict:
     global load_data
     path = Path(storage)
     load_data = {}
     if not path.exists():
        Path('storage').mkdir(parents=True, exist_ok=True)
        logging.info(f'storage added')
     else:
        if path.stat().st_size > 0:
            try:
                with open(storage, 'r', encoding='utf-8') as file:
                    load_data = json.load(file)
            except json.JSONDecodeError as e:
                logging.error(f'Error {e}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    check_storage(STORAGE)
    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()
    socket_server = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    socket_server.start()


    