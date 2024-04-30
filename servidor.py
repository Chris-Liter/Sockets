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
channel.exchange_declare(exchange='logs', exchange_type='fanout')
result = channel.queue_declare(queue='chat_queue')
queue_name = result.method.queue
channel.queue_bind(exchange='logs', queue=queue_name)

clients = []
nicknames = []
mensajes = []

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
            mensajes.append(message)
            broadcast(message)
        except Exception as e:
            print(f"Error al manejar cliente: {e}")
            break

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
        print(f"Nombre del cliente: {nickname}\n")
        broadcast(f"{nickname} se ha conectado\n".encode('utf-8'))

        client.send(f"Bienvenido, {nickname}".encode('utf-8'))  

         

        # Consumir mensajes de la cola y enviarlos al cliente recién conectado
        def consume_and_send():
            for method_frame, properties, body in channel.consume(queue=queue_name, inactivity_timeout=1):
                if body is not None:
                    message = body.decode('utf-8')
                    print("Mensaje recibido de RabbitMQ: ", message)
                    client.send(message.encode('utf-8'))

                # Si hay una desconexión del cliente, detener el consumo de la cola
                if client.fileno() == -1:
                    channel.cancel()
                    break

        consume_thread = threading.Thread(target=consume_and_send)
        consume_thread.start()




print("Servidor corriendo")
receive()