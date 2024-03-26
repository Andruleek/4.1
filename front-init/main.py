from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
from datetime import datetime
import json
import os
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            username = data.get('username', [''])[0]
            message = data.get('message', [''])[0]
            self.save_message(username, message)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def save_message(self, username, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data = {
            timestamp: {
                "username": username,
                "message": message
            }
        }
        if not os.path.exists('storage'):
            os.makedirs('storage')
        with open('storage/data.json', 'a+') as file:
            file.seek(0)
            try:
                data_list = json.load(file)
            except json.decoder.JSONDecodeError:
                data_list = {}
            data_list.update(data)
            file.seek(0)
            json.dump(data_list, file, indent=4)

def socket_server():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        data = data.decode('utf-8').split(',')
        RequestHandler().save_message(data[0], data[1])

def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    # Start socket server in a separate thread
    import threading
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.start()
    # Start HTTP server
    run()
