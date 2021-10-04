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
    print(f"[NEW CONNECTION] {add} connected")
    conn.send("OK@Welcome to the Server".encode(FORMAT))


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
