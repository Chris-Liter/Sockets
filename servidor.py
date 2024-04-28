import socket
import threading
import ssl
import win32com.client
import os
import hashlib

HOST = '127.0.0.1'
PUERTO = 6400

#hostname = 'www.python.org'
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(certfile="myapp.crt", keyfile="myapp.key")

name = 'Chris'

server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=True) 

server.bind((HOST, PUERTO))
server.listen()



clients = []
nicknames = []

def broadcast(message):
    print("Este es el mensaje a enviar: ",message)
    for client in clients:
        
        cola = win32com.client.Dispatch("MSMQ.MSMQQueueInfo")
        cola.FormatName = f"direct=os:{name}\\Private$\\ChatQueue"  # Cambia esto al nombre de tu cola privada

        print(f"Ruta de acceso de la cola: {cola.PathName}")
        colaa = cola.Open(2, 0)  # 1 para abrir para recibir, 0 para abrir en modo de lectura
        valor = message
        msg = win32com.client.Dispatch("MSMQ.MSMQMessage")
        msg.Label = "Mensaje"
        msg.Body = valor
        msg.Send(colaa)

        # Enviar algunos mensajes a la cola

        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            print(f"Mensaje recibido: {message}")
            broadcast(message)
        except Exception as e:
            print(f"Error al manejar cliente: {e}")
            break

    # Cuando el cliente se desconecta, eliminarlo de la lista de clientes
    try:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames[index]
        nicknames.remove(nickname)
        client.close()
        broadcast(f"{nickname} se ha desconectado\n".encode('utf-8'))
    except ValueError:
        pass

def receive():
    while True:
        client, address = server.accept()
        print(f"Conectado con {str(address)}!")

        # Asignar un nombre automáticamente
        nickname = f"Cliente-{address[1]}\n"
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nombre de el cliente es {nickname}\n")
        broadcast(f"{nickname} \n".encode('utf-8'))
        client.send(nickname.encode('utf-8'))  # Enviar el nombre al cliente

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()



print("Servidor corriendo")
receive()