import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import ssl

host = '127.0.0.1'
puerto = 6400


class Client:
    def __init__(self, host, port):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        context.load_cert_chain(certfile="myapp.crt", keyfile="myapp.key")

        self.sock = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=False, server_hostname="127.0.0.1")
        self.sock.connect((host, port))

        self.nickname = self.sock.recv(1024).decode('utf-8')  # Recibir el nombre asignado

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="#303030")  # Color de fondo más oscuro

        self.chat_label = tkinter.Label(self.win, text="Chat", bg="#303030", fg="#FFFFFF", font=("Arial", 16, "bold"))  # Texto blanco
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, bg="#404040", fg="#FFFFFF")  # Fondo gris más oscuro y texto blanco
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Mensaje", bg="#303030", fg="#FFFFFF", font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3, bg="#404040", fg="#FFFFFF")  # Fondo gris más oscuro y texto blanco
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Enviar", command=self.write, bg="#008CBA", fg="white", font=("Arial", 12))  # Botón azul claro con texto blanco
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    pass  # No se necesita aquí, ya que el nombre se recibe en __init__
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

client = Client(host, puerto)