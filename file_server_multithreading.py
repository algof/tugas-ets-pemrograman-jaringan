import time
import sys
from socket import *
import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from file_protocol import  FileProtocol
fp = FileProtocol()

def handle_client(connection, address):
    logging.warning(f"Handling client {address}")
    with connection:
        while True:
            data = b''
            while not data.endswith(b'\r\n'):
                part = connection.recv(1)
                if not part:
                    break
                data += part
            if data:
                try:
                    d = data.decode().strip()
                    hasil = fp.proses_string(d)
                    hasil = hasil + "\r\n\r\n"
                    connection.sendall(hasil.encode())
                except Exception as e:
                    logging.error(f"Error while handling client {address}: {e}")
                    break
            else:
                break
    logging.warning(f"Client {address} disconnected")

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_workers=10):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"Server running on {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        try:
            while True:
                try:
                    conn, addr = self.my_socket.accept()
                    logging.warning(f"Connection from {addr}")
                    self.executor.submit(handle_client, conn, addr)
                except OSError:
                    break  
        except KeyboardInterrupt:
            logging.warning("Server stopped by user (KeyboardInterrupt)")
        finally:
            logging.warning("Shutting down thread pool and closing socket...")
            self.my_socket.close()
            self.executor.shutdown(wait=True)

def main():
    svr = Server(ipaddress='0.0.0.0', port=46666, max_workers=5)
    svr.start()
    svr.join()

if __name__ == "__main__":
    main()