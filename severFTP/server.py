import socket
import os
import threading
import time
from datetime import datetime
import hashlib

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDRESS = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data/"
clients = []
log = []
BLOCK_SIZE = 4096


def handle_client(conn, ip, port, filename, number_clients):
    print(f"[NEW CONNECTION] {(ip, port)} conectado")
    conn.send("OK@Bienvenido al servidor".encode(FORMAT))
    x = True
    while x:

        if len(clients) == number_clients:
            hash_value = generateHash(filename)
            filesize = os.path.getsize(filename)
            conn.sendall(f'HASH:{hash_value}:FILE:{filename}:SIZE:{filesize}'.encode())
            start_time = time.time()
            with open(f"{filename}", "r") as f:
                file = f.read()
            print("Is it alive")
            conn.send(file.encode(FORMAT))
            finish_time = time.time()
            tiempo = finish_time - start_time
            log.append([ip, port, tiempo])
            print(log)

            x = False
    print("should be the end for thread")
    conn.close()


def main():
    print("The server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Que archivo desea utilizar:\n1. 100MB\n2. 250MB\n")
    archivo = int(input("Ingrese el número del archivo que desea enviar: "))
    filename = SERVER_DATA_PATH
    if archivo == 1:
        filename += "100MB.txt"
    elif archivo == 2:
        filename += "250MB.txt"
    number_clients = int(input("Elija el numero de clientes simultaneos: "))

    server.bind(ADDRESS)
    server.listen()
    print("The server is listening")
    while True:

        conn, (ip, port) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, ip, port, filename, number_clients))
        thread.start()
        clients.append([ip, port])
        time.sleep(1)
        if len(clients) == number_clients:
            print("Writing Log")
            writeLog(filename)


def writeLog(filename):
    fecha = datetime.now()
    filesize = os.path.getsize(filename)
    waitForThreads = True
    while waitForThreads:
        waitForThreads = len(log) != len(clients)
    log_name = f"{fecha.year}-{fecha.month}-{fecha.day}-{fecha.hour}-{fecha.minute}-{fecha.second}-log.txt"
    file_log = open(f"logs/{log_name}", "x")


    file_log.write(f"LOG {fecha}\n\n")
    file_log.write(f"Nombre del archivo: {filename.split('/')[1]}\n")
    file_log.write(f"Tamaño del archivo: {filesize} bytes\n")
    file_log.write(f"Número de clientes: {len(log)}\n\n")
    file_log.write(f"Información de clientes: \n")

    for data in log:
        file_log.write(f"\tIP: {data[0]}\n")
        file_log.write(f"\tPUERTO: {data[1]}\n")
        file_log.write(f"\tTIEMPO: {data[2] * 1000}\n")
        file_log.write(f"\n")

    file_log.close()


def generateHash(filename):
    # Cálculo del hash del archivo
    file_hash = hashlib.sha256()
    with open(filename, 'rb') as f:
        fb = f.read(BLOCK_SIZE)  # Read from the file. Take in the amount declared above
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    f.close()
    return file_hash.hexdigest()


if __name__ == "__main__":
    main()
