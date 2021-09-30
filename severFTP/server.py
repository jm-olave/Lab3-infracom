import socket
IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
def main():
    #SOCKET_STREAM significa usar el modelo de tcp para la conexion
    print("[STARTING]  Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[LISTENING]  Server is listening")

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected ")

        filename = conn.recv(SIZE).decode(FORMAT)
        #recibir el archivo desde el cliente
        print("[RECV]"+filename+"FILENAME RECEIVED")
        file = open("server_data/"+filename, "w")
        conn.send("Filename received".encode(FORMAT))
        #verifica contenido de los datos 
        data = conn.recv(SIZE).decode(FORMAT)
        print(f"[RECV] file data received" )
        file.write(data)
        conn.send("File data received".encode(FORMAT))

        file.close()
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnnected") 



if __name__ == "__main__":
    main()