"""
@author: Fotios Lygerakis
@UTA ID: 1001774373
"""
import socket

from config import BUFFER_SIZE, port, client_file
from utils import send_file, receive_file

"""
Code based on : https://github.com/TomPrograms/Simple-Python-File-Transfer-Server/blob/master/client.py
"""


class Client:
    def __init__(self):
        self.target_port = port
        self.target_ip = socket.gethostbyname(socket.gethostname())
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)
        self.connection_open = False # if connection is open is True
        self.username = None

    def connect_to_server(self):
        """
        Connection to the server
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.target_ip, int(self.target_port)))

    def reconnect(self):
        """
        If connection is not open it connects to the server
        """
        if not self.connection_open:
            self.connect_to_server()

    def login(self, username):
        """
        Attempts to log in client with the given username
        :param username: username string
        :return: True if connection established, False if the username got rejected by the server
        """
        # send to the server the username
        self.s.send(username.encode())

        # retrieve server's response for the username | "username ok" or "invalid username"
        username_response = self.s.recv(BUFFER_SIZE).decode("utf-8")

        # invalid username
        if username_response == "invalid username":
            print("username: {} already taken.".format(username))
            print("Please choose another username")
            self.username = None

            # shutting down the socket
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            return False
        # valid username
        elif username_response == "username ok":
            print("Connected to the server with username \"{}\"".format(username))
            self.username = username
            return True

    def main(self):
        """
        Main function of the client
        """
        print("before send msg")
        self.s.send('data'.encode())
        print("after send msg")
        # path to the client files
        path = "client_files/"

        # file to be checked by the server
        file_name = path + client_file

        # send file to be checked to server
        send_file(self.s, file_name)

        # receive spelling annotated file from server
        write_name = path + 'server_annotated_text_{}.txt'.format(self.username)
        receive_file(self.s, write_name)

    def close_connection(self):
        # close the connection to the server
        print("connection closed")
        self.s.send('exit'.encode())
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        self.connection_open = False
