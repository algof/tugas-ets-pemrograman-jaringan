from socket import *
import socket
import logging
from multiprocessing import Pool
from file_protocol import FileProtocol
fp = FileProtocol()

def proses_data(d):
    return fp.proses_string(d)

def handle_client(connection, address, pool):
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
                    result = pool.apply(proses_data, args=(d,))
                    response = result + "\r\n\r\n"
                    connection.sendall(response.encode())
                except Exception as e:
                    logging.error(f"Error handling client {address}: {e}")
                    break
            else:
                break
    logging.warning(f"Client {address} disconnected")

def run_server(ip='0.0.0.0', port=6666, max_workers=4):
    pool = Pool(processes=max_workers)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    logging.warning(f"Server running on {(ip, port)}")

    try:
        while True:
            conn, addr = server_socket.accept()
            logging.warning(f"Connection from {addr}")
            handle_client(conn, addr, pool)
    except KeyboardInterrupt:
        logging.warning("Server stopped by user")
    finally:
        server_socket.close()
        pool.close()
        pool.join()

if __name__ == '__main__':
    run_server()