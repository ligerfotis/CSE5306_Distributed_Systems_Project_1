import socket
import os
import time

# from tomprograms.gui import GUI

"""
https://github.com/TomPrograms/Simple-Python-File-Transfer-Server
"""

BUFFER_SIZE = 1024


class Client:
    def __init__(self):
        self.target_port = 60000
        self.target_ip = socket.gethostbyname(socket.gethostname())
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)
        self.connection_open = False
        # self.connect_to_server()

    def connect_to_server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.target_ip, int(self.target_port)))

    def reconnect(self):
        if not self.connection_open:
            self.connect_to_server()

    def login(self, username):
        attempt = 1
        max_attempts = 3
        # while True:

        self.s.send(username.encode())
        username_response = self.s.recv(BUFFER_SIZE).decode("utf-8")
        print(username_response)
        if username_response == "invalid username":
            # if attempt < max_attempts:
            #     attempt += 1
            # else:
            print("username: {} already taken.".format(username))
            print("Please choose another username")
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            return False

        elif username_response == "username ok":
            # break
            return True

    def main(self):
        # todo: make a file system for server and each client

        file_name = 'mytext.txt'

        # send file to be checked to server
        self.send_to_server(file_name)

        # receive spelling annotated file from server
        write_name = 'server_annotated_text.txt'
        self.receive_from_server(write_name)

        # close the connection to the server
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        self.connection_open = False

    def send_to_server(self, file_name):
        print('Sending', file_name)
        file = open(file_name, 'rb')
        data = file.read(BUFFER_SIZE)

        while data:
            self.s.send(data)
            data = file.read(BUFFER_SIZE)
        self.s.send('<EOF>'.encode())   # send EOF string

    def receive_from_server(self, write_name):
        if os.path.exists(write_name):
            os.remove(write_name)

        with open(write_name, 'w') as file:
            while 1:
                data = self.s.recv(BUFFER_SIZE).decode()
                if data == '<EOF>':
                    break

                file.write(data)
        print(write_name, 'successfully sent to client.')


# client = Client()
# client_gui_1 = GUI("Client", is_server=False)
# client_gui_1.run()
