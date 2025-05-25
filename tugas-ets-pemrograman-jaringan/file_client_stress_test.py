import socket
import json
import base64
import logging
import threading
import concurrent.futures
import time

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n").encode())
        # sock.sendall(command_str.encode()) # old version
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        print(hasil)
        return True
    else:
        print("Gagal")
        return False

def remote_delete(filename=""):
    command_str=f"DELETE {filename}"
    hasil = send_command(command_str)
    if(hasil['status'] == 'OK'):
        print(f"file '{filename}' berhasil di delete")
        print(hasil['message'])
    else:
        print("Gagal")

def remote_upload(filename="", isifile=""):
    command_str=f"UPLOAD {filename} {isifile}"
    hasil = send_command(command_str)
    if hasil and hasil.get('status') == 'OK':
        print(hasil['data'])
    else:
        print("Gagal")

def remote_download(filename="", dest_file=""):
    command_str=f"DOWNLOAD {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        namafile= hasil['data_namafile']
        # s_split = namafile.split(".")
        # result = f"{s_split[0]}_download.{s_split[1]}"
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(dest_file,'wb+')
        fp.write(isifile)
        fp.close()
        print(hasil)
        print(f"{namafile} berhasil di download ke direktori lokal anda")
        return True
    else:
        print("Gagal")
        return False

def thread_function(index):
    print(f"[Thread-{index}] Starting remote_list")
    start = time.time()
    # remote_list()
    isi_file = get_binary_from_file("file_10mb.txt")
    remote_upload("stress_test_10mb.txt", isi_file)
    end = time.time()
    print(f"[Thread-{index}] Finished remote_list")
    print(f"Waktu eksekusi: {end - start} detik")

# Jumlah thread yang ingin dijalankan secara bersamaan
# NUM_THREADS = 5
# if __name__=='__main__':
#     server_address=('172.16.16.101', 46666)
#     threads = []
#     for i in range(NUM_THREADS):
#         t = threading.Thread(target=thread_function, args=(i,))
#         threads.append(t)
#         t.start()

#     # Tunggu semua thread selesai
#     for t in threads:
#         t.join()

#     print("Semua thread telah selesai.")

def get_binary_from_file(nama_file=""):
    with open(f'{nama_file}', 'r', encoding='utf-8') as file:
        text_data = file.read()
        
    text_bytes = text_data.encode('utf-8')
    
    encoded_bytes = base64.b64encode(text_bytes)

    return encoded_bytes

if __name__ == '__main__':
    server_address = ('172.16.16.101', 46666)
    num_of_workers = 5  # Jumlah thread / worker yang ingin dijalankan

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        # Kirim semua task ke thread pool
        futures = [executor.submit(thread_function, i) for i in range(num_of_workers)]

        # Tunggu semua task selesai
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Bisa menangkap exception jika ada

    end_time = time.time()
    print(f"\nSemua thread selesai. Total waktu eksekusi: {end_time - start_time:.2f} detik")