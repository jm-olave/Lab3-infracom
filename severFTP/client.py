
import socket
IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


def main():
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    file = open("data/test.txt", "r")
    data = file.read()

    client.send("test.txt".encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)

    print(f"[LISTENING]: {msg}  Server is listening")

    client.send(data.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")
    #cerrar conexion
    file.close()
    client.close()



if __name__ == "__main__":
    main()   