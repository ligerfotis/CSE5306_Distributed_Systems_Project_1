import socket
import threading
import os
import select

# from tomprograms.gui import GUI
import time

"""
https://github.com/TomPrograms/Simple-Python-File-Transfer-Server
"""
TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024


def send_to_client(c, write_name):
    print('Sending', write_name)
    file = open(write_name, 'rb')
    data = file.read(BUFFER_SIZE)

    while data:
        c.send(data)
        data = file.read(BUFFER_SIZE)
    c.send('<EOF>'.encode())  # send EOF string


def receive_from_client(c, write_name):
    with open(write_name, 'w') as file:
        while 1:
            data = c.recv(BUFFER_SIZE).decode()
            if data == '<EOF>':
                break

            file.write(data)
    print(write_name, 'successfully uploaded to server.')


class Server:
    def __init__(self):
        self.online_user_list = []
        self.threads = []

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.settimeout(3)

        # self.accept_connections()

    def accept_connections(self):
        ip = socket.gethostbyname(socket.gethostname())
        # port = int(input('Enter desired port --> '))
        port = 60000
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.s.bind((ip, port))
        self.s.listen(100)

        print('Running on IP: ' + ip)
        print('Running on port: ' + str(port))

        while 1:
            try:
                c, addr = self.s.accept()
            except OSError as exc:
                # print('child  exception  %s' % exc)
                return

            if c:
                username = self.user_login(c, addr)
                print('Got connection from {}. Have also: {}'.format(username, self.online_user_list))

                thread = threading.Thread(target=self.handle_client, args=(c, addr, username))
                thread.start()
                self.threads.append(thread)

    def user_login(self, conn, addr):
        # while True:
        username = conn.recv(BUFFER_SIZE).decode("utf-8")
        print("username:{}".format(username))
        if username in self.online_user_list:
            print("Failed connection trial from {}: username already in use".format(addr))
            message = b"invalid username"
            conn.send(message)
            # conn.shutdown(socket.SHUT_RDWR)
            # conn.close()
            # print("closed connection with {}".format(username))
        else:
            message = b"username ok"
            conn.send(message)
            self.online_user_list.append(username)
            # break

        return username

    def handle_client(self, c, addr, username):
        # todo: make a file system for server and each client

        client_file = 'client_file.txt'

        # check if file exists already and erase it if so
        if os.path.exists(client_file):
            os.remove(client_file)

        # start receiving file from the user and saving it
        receive_from_client(c, client_file)

        # check client's file for spelling mistakes against the lexicon
        checked_file_name = spelling_check('client_file.txt')

        # time delay to check username inconsistencies
        time.sleep(10)

        # send back translated text
        send_to_client(c, checked_file_name)

        self.online_user_list.remove(username)
        c.shutdown(socket.SHUT_RDWR)
        c.close()
        print("closed connection with {}".format(username))


def spelling_check(file_to_checked):
    # assume that there is a period at the end of each line only
    with open('lexicon.txt') as lex_file:
        lex_array = lex_file.readline().split(" ")

    with open(file_to_checked) as file:
        text = file.readlines()

    array_checked_text = []
    lower_lex_array = [word.lower() for word in lex_array]
    upper_lex_array = [word.upper() for word in lex_array]
    cap_lex_array = [word.capitalize() for word in lower_lex_array]
    for line in text:
        # convert string to array of words while removing periods, commas and next line special chars
        line_array = line.strip("\n.,").split(" ")
        # substitute a word in the word array if it is in the lower/upper/capitalized lexicon word array
        corrected_array = ['[' + word_i + ']'
                           if word_i in lower_lex_array or word_i in upper_lex_array or word_i in cap_lex_array
                           else word_i
                           for word_i in line_array]

        array_checked_text.append(corrected_array)

    # convert word arrays into strings and add period at the end
    string_checked_text = []
    for line in array_checked_text:
        string_checked_text.append(" ".join(line) + '.')

    checked_file_name = "checked_text.txt"
    with open(checked_file_name, 'w') as chked_file:
        chked_file.writelines(string_checked_text)
    return checked_file_name

# server = Server()
# server_gui = GUI("server", is_server=True)
# server_gui.run()
