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
        data_received=""
        while True:
            # data = sock.recv(10240) # 10MB
            # data = sock.recv(4096) # 4MB
            data = sock.recv(51200) # 50MB
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
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
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(dest_file,'wb+')
        fp.write(isifile)
        fp.close()
        # print(hasil)
        print(f"{namafile} berhasil di download ke direktori lokal anda")
        return True
    else:
        print("Gagal")
        return False

def thread_function(index):
    command = "remote_download"
    print(f"[Thread-{index}] Starting {command}")
    start = time.time()
    # success = remote_download("file_10mb.txt", "hasildownload_10mb.txt")
    success = remote_download("file_50mb.txt", "hasildownload_50mb.txt")
    success = remote_download("file_50mb.txt", "hasildownload_100mb.txt")
    # remote_list()
    # isi_file = get_binary_from_file("file_10mb.txt") # works 1,5
    # isi_file = get_binary_from_file("file_50mb.txt") # works 1 worker
    # isi_file = get_binary_from_file("file_100mb.txt") # works 1 worker
    # remote_upload("stress_test_10mb.txt", isi_file)
    end = time.time()
    print(f"[Thread-{index}] Finished {command}")
    print(f"Waktu eksekusi: {end - start} detik")
    return success
    
def get_binary_from_file(nama_file=""):
    with open(f'{nama_file}', 'r', encoding='utf-8') as file:
        text_data = file.read()
        
    text_bytes = text_data.encode('utf-8')
    
    encoded_bytes = base64.b64encode(text_bytes)

    return encoded_bytes

if __name__ == '__main__':
    server_address = ('172.16.16.101', 46666)
    num_of_workers = 50
    
    start_time = time.time()
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        
        futures = [executor.submit(thread_function, i) for i in range(num_of_workers)]

        # Tunggu semua task selesai
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1

    end_time = time.time()
    print(f"\nSemua thread selesai. Total waktu eksekusi: {end_time - start_time:.2f} detik")
    print(f"Jumlah thread yang berhasil dijalankan: {success_count} dari {num_of_workers}")