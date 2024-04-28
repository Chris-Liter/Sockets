import socket
import threading
import ssl

HOST = '127.0.0.1'
PUERTO = 6400

#hostname = 'www.python.org'
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(certfile="myapp.crt", keyfile="myapp.key")



server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=True) 

server.bind((HOST, PUERTO))
server.listen()



clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Conectado con {str(address)}!")

        # Asignar un nombre automáticamente
        nickname = f"Cliente-{address[1]}"
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nombre de el cliente es {nickname}")
        broadcast(f"{nickname} conectado al servidor \n".encode('utf-8'))
        client.send(nickname.encode('utf-8'))  # Enviar el nombre al cliente

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Servidor corriendo")
receive()
