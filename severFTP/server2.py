import hashlib
import logging
import math
import socket
import threading
import numpy as np
import traceback
from _thread import *
import time
from datetime import datetime
from tqdm import tqdm


# host = socket.gethostbyaddr("54.162.149.119")[0]
host  = '0.0.0.0'
port = 60002
BUFFER_SIZE = 1024

File_path = "server_data/"
Log_path = "logs/"

file_100MB = '100MB.txt'
file_250MB = '250MB.txt'
files_names = {1: file_100MB, 2: file_250MB}

# open in binary

SYN = 'Hola'
AKN_READY = 'Listo'
AKN_NAME = 'Nombre'
AKN_OK = 'Ok'
AKN_HASH = 'HashOk'
AKN_COMPLETE = 'SendComplete'
ERROR = 'Error'


def threadsafe_function(fn):
    
    lock = threading.Lock()

    def new(*args, **kwargs):
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            lock.release()
        return r

    return new


class ServidorProtocolo:

    def __init__(self, clients_number, file_name):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread_count = 0
        self.clients_number = clients_number
        self.file_name = file_name
        self.ready_clients = 0
        self.failed_connections = 0
        self.all_ready_monitor = threading.Event()
        self.file_size = self.obtener_tamano_archivo()
        self.running_times = np.zeros(clients_number)
        self.completed_connections = np.zeros(clients_number)
        self.success_connections = np.zeros(clients_number)
        self.packages_sent = np.zeros(clients_number)
        self.bytes_sent = np.zeros(clients_number)

        try:
            self.server_socket.bind((host, port))
        except socket.error as e:
            print(str(e))

        print('Waitiing for a Connection..')
        self.server_socket.listen(5)


        
        now = datetime.now()
        dt_string = now.strftime("%Y-%d-%m %H:%M:%S")
        dt_string2 = now.strftime("%Y-%d-%m-%H-%M-%S")

        logging.basicConfig(filename="logs/{}.log".format(dt_string2), level=logging.INFO)
        logging.info(dt_string)
        logging.info("File name: {}; file size: {} B".format(self.file_name, self.file_size))

    def send_file_to_client(self, connection, thread_id):
        while True:
            try:
                respuesta = self.recibir_desde_cliente(connection)
                self.verificar_respuesta(respuesta, SYN)

                self.enviar_al_cliente(connection, SYN, "Servidor responde: Respuesta desde el cliente {} received".format(thread_id), thread_id)

                self.enviar_al_cliente(connection, f'{thread_id};{self.clients_number}',
                                    "Servidor responde: Sent id to client {}".format(thread_id),
                                    thread_id)

                respuesta = self.recibir_desde_cliente(connection)
                self.verificar_respuesta(respuesta, AKN_READY)

                self.actualizar_clientes_listos()

                while not self.clientes_listos(thread_id):
                    print('Servidor responde: client {} is put in wait for the rest of clients'.format(thread_id))
                    self.all_ready_monitor.wait()


                self.enviar_al_cliente(connection, self.file_name, "Servidor responde: Sending file name ({}) to client "
                                                           "{}".format(self.file_name, thread_id), thread_id)

                respuesta = self.recibir_desde_cliente(connection)

                self.verificar_respuesta(respuesta, AKN_NAME)

                hash = self.hash_file()
                self.enviar_al_cliente(connection, hash,
                                    "Servidor responde: Sending file hash ({}) to client {}".format(hash, thread_id), thread_id)
                respuesta = self.recibir_desde_cliente(connection)

                self.verificar_respuesta(respuesta, AKN_OK)

                size = str(self.file_size)

                self.enviar_al_cliente(connection, size,
                                    "Servidor responde: Sending file size ({}) to client {}".format(size, thread_id), thread_id)

                start_time = time.time()

                self.send_file(connection, thread_id)

                respuesta = self.recibir_desde_cliente(connection)

                self.running_times[thread_id - 1] = time.time() - start_time

                self.verificar_respuesta(respuesta, AKN_COMPLETE)

                respuesta = connection.recv(BUFFER_SIZE).decode('utf-8')
                self.verificar_respuesta(respuesta, AKN_HASH)

                print("Servidor responde: File integrity verified by  client {}".format(thread_id))

                connection.close()
                self.completed_connections[thread_id - 1] = 1
                self.success_connections[thread_id-1] = 1
                self.log_info()
                break

            except Exception as err:
                self.update_failed_connections()
                connection.close()
                print("Servidor responde: error durante la transmision {}: {} \n".format(thread_id, str(err)))
                self.completed_connections[thread_id - 1] = 1
                self.log_info()
                break

    def recibir_desde_cliente(self, connection):
        return connection.recv(BUFFER_SIZE).decode('utf-8')

    def enviar_al_cliente(self, connection, segment, print_message, thread_id):
        b = connection.send(str.encode(segment))
        self.bytes_sent[thread_id-1] += int(b)
      

        print("\n", print_message)

    def verificar_respuesta(self, received, expected):
        if not expected == received:
            raise Exception("Error en protocolo:expected{}; received {}".format(expected, received))



    @threadsafe_function
    def clientes_listos(self, thread_id):

        all_ready = self.clients_number - self.ready_clients == 0

        if all_ready:
            print("Servidor responde: todos los clientes listos {}".format(thread_id))

        return all_ready


    def send_file(self, connection, thread_id):

        progress = tqdm(range(self.file_size), f'Transferir al cliente{thread_id}', unit="B",
                        unit_scale=True,
                        unit_divisor=BUFFER_SIZE)


        with open(File_path + self.file_name, 'rb') as file:

            while True:
                
                chunk = file.read(BUFFER_SIZE)

                if chunk == b'':
                    break

                b = connection.send(chunk)
                self.bytes_sent[thread_id-1] += int(b)

                progress.update(len(chunk))

            self.packages_sent[thread_id - 1] = self.file_size/BUFFER_SIZE
            print("Servidor responde: Archivo correctamente enviado {}".format(thread_id))
            file.close()


    def obtener_tamano_archivo(self):
        with open(File_path + self.file_name, 'rb') as file:
            packed_file = file.read()
        return int(len(packed_file))

    def hash_file(self):
        file = open(File_path + self.file_name, 'rb') 
        h = hashlib.sha1()
        chunk = 0
        while chunk != b'':
            chunk = file.read(BUFFER_SIZE)
            h.update(chunk)
        file.close()
        return h.hexdigest()

    def close(self):
        self.server_socket.close()

    @threadsafe_function
    def actualizar_clientes_listos(self):
        self.ready_clients += 1

        if self.clients_number - self.ready_clients == 0:
            self.all_ready_monitor.set()

    @threadsafe_function
    def update_failed_connections(self):
        self.failed_connections += 1

    def completados(self):
        return self.completed_connections.sum() == self.clients_number


    def log_info(self):
        if self.completados():
            logging.info('')
            logging.info('Conexiones exitosas:')
            d = {1: 'Si', 0: 'no'}

            for n in range(self.clients_number):
                logging.info('Cliente{}: {}'.format(n + 1, d[self.success_connections[n]]))

            logging.info(
                '_____________________________________________________________________________________________________')
            logging.info('Tiempo de ejecucion:')
            for n in range(self.clients_number):
                logging.info('Client{}: {} s'.format(n + 1, self.running_times[n]))

            logging.info(
                '_____________________________________________________________________________________________________')
            logging.info('Bytes enviados:')
            for n in range(self.clients_number):
                logging.info('Client{}: {} B'.format(n + 1, self.bytes_sent[n]))

            logging.info(
                '_____________________________________________________________________________________________________')
            logging.info('Paquetes enviados:')
            for n in range(self.clients_number):
                logging.info('Client{}: {}'.format(n + 1, self.packages_sent[n]))

    def run(self):

        while True:
            print('Escuchando', self.server_socket.getsockname())

            Client, address = self.server_socket.accept()
            self.thread_count += 1

            print('Conectado a: ' + address[0] + ':' + str(address[1]))

            logging.info('Conexion a cliente{} ({}:{})'.format(self.thread_count, address[0], str(address[1])))

            if self.thread_count <= self.clients_number:
                start_new_thread(self.send_file_to_client, (Client, self.thread_count))



            print('Thread Number: ' + str(self.thread_count))

def main():

    fn = int(input("IIndicar el numero de clientes para enviar archivo:: \n1. 100 MB\nType 2. 250 MB  \n"))
    file_name = files_names[fn]

    nc = int(input("Indicar el numero de clientes para enviar archivo: \n"))

    s = ServidorProtocolo(nc, file_name)
    s.run()


if __name__ == "__main__":
    main()