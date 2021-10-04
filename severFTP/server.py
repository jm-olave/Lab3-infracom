import socket
import os
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDRESS = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"


def handle_client(conn, add):
    print(f"[NEW CONNECTION] {add} conectado")
    conn.send("OK@Bienvenido al servidor".encode(FORMAT))
    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")

        cmd = data[0]

        if cmd == "LIST":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "El server esta vacio"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            name, text = data[1], data[2]
            filepath = os.path.join(SERVER_DATA_PATH, name)
            with open(filepath, "w") as f:
                f.write(text)

            send_data = "OK@UPLOAD exitosa."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "El directorio del servidor esta vacio"
            else:
                if filename in files:
                    os.system(f"Del {SERVER_DATA_PATH}\{filename}")
                    send_data += "Archivo eliminado."
                else:
                    send_data += "No se encontro el archivo."

            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break
        elif cmd == "HELP":
            data = "OK@"
            data += "LIST: Enlistar todos los archivos del servidor.\n"
            data += "UPLOAD <path>: Subir un archivo al servidor.\n"
            data += "DELETE <filename>: Eliminar un archivo del servidor.\n"
            data += "LOGOUT: Desconectarse del servidor.\n"
            data += "HELP: Enlistar los comandos."

            conn.send(data.encode(FORMAT))

    print(f"[DISCONNECTED] {add} desconectado")
    conn.close()


def main():
    print("The server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDRESS)
    server.listen()
    print("The server is listening")
    while True:
        conn, add = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, add))
        thread.start()


if __name__ == "__main__":
    main()
