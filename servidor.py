import socket
import threading
import ssl
import win32com.client
import os
import hashlib
import pika

HOST = '127.0.0.1'
PUERTO = 6401

#hostname = 'www.python.org'
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(certfile="myapp.crt", keyfile="myapp.key")

server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=True) 

server.bind((HOST, PUERTO))
server.listen()


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
cha = channel.queue_declare(queue='chat_queue')
result = cha.method.queue

clients = []
nicknames = []

def broadcast(message):
    print("Este es el mensaje a enviar: ",message)
    for client in clients:
        # Enviar algunos mensajes a la cola
        channel.basic_publish(exchange='', routing_key='chat_queue', body=message)
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

        nickname = f"Cliente-{address[1]}\n"
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nombre de el cliente es {nickname}\n")
        mensajes = channel.basic_consume(queue=result, on_message_callback=receive, auto_ack=True)
        broadcast(f"{nickname} \n".encode('utf-8'))
        #client.send(mensajes)
        client.send(nickname.encode('utf-8'))  


        handle_thread = threading.Thread(target=handle, args=(client,))
        handle_thread.start()



print("Servidor corriendo")
receive()