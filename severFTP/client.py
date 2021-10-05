import socket
import hashlib
#from severFTP.server import BLOCK_SIZE

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SIZE = 1024
BLOCK_SIZE = 4096

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

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    x=8
    print("antes del while")
    while x<10:
        bienvenida = client.recv(BLOCK_SIZE).decode(FORMAT)
        
        print(bienvenida)
        print("entro al while")
        data = client.recv(BLOCK_SIZE).decode(FORMAT)
        
        print(data)
    
        if len(data) > 0:
            info = data.split(":")
            print(info)
            hash_val = info[1]
            print(hash_val +" hash")
            archivo = info[3]
            print(archivo + " archivo")
            tamano = info[5]
            print(tamano + "tamano")
            hash_compare = generateHash(archivo)
            print(hash_compare + "hash creado")
            if hash_val == hash_compare:
                print( "Entra a compare")
                client.send(f'Hash comparado exisosamente'.encode() )
            else:
                print("Entra a else")
                client.send(f'Hash no comparado'.encode() )

        
            x = x+2
        



if __name__ == "__main__":
    main()
