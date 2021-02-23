import socket
import threading
import os
import time

from config import BUFFER_SIZE, port, sleep_time
from utils import send_file, receive_file

"""
Code based on https://github.com/TomPrograms/Simple-Python-File-Transfer-Server
"""


class Server:
    def __init__(self):
        # list to keep track of the connected usernames
        self.online_user_list = []
        # create a socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def accept_connections(self):
        """
        Start accepring actions
        """
        # use localhost IP
        ip = socket.gethostbyname(socket.gethostname())

        # set up the socket, bind it and start listening
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((ip, port))
        self.s.listen(100)
        print('Running on IP: ' + ip)
        print('Running on port: ' + str(port))

        while 1:
            # accept connections
            try:
                c, addr = self.s.accept()
            # catches OSError when closing the socket
            except OSError:
                break

            # if connection is up
            if c:
                # check username
                username = self.user_login(c, addr)
                # valid username
                if username is not None:
                    print('Got connection from {}. Have also: {}'.format(username, self.online_user_list))

                    # create and start a thread for that client
                    thread = threading.Thread(target=self.handle_client, args=(c, username))
                    thread.start()

    def user_login(self, conn, addr):
        """
        Tries once to log the user and sends to the user "username ok" if the username is not being used by another
        client or "invalid username" in a different case.
        :param conn: connection
        :param addr: address
        :return: username or None if connection closed due to username unavailability
        """
        username = conn.recv(BUFFER_SIZE).decode("utf-8")
        print("username:{}".format(username))
        if username in self.online_user_list:
            print("Failed connection trial from {}: username already in use".format(addr))
            message = b"invalid username"
            conn.send(message)
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            print("closed connection with {}".format(username))
            return None
        else:
            message = b"username ok"
            conn.send(message)
            self.online_user_list.append(username)
            return username

    def handle_client(self, c, username):
        """
        Main functionality ot the server
        :param c: connection
        :param username: username string
        """
        path = "server_files/"
        client_file = path + 'client_file_{}.txt'.format(username)

        # check if file exists already and erase it if so
        if os.path.exists(client_file):
            os.remove(client_file)

        # start receiving file from the user and saving it
        receive_file(c, client_file)

        # check client's file for spelling mistakes against the lexicon
        checked_file_name = spelling_check(client_file, username)

        # time delay to check username inconsistencies
        time.sleep(sleep_time)

        # send back translated text
        send_file(c, checked_file_name)

        self.online_user_list.remove(username)
        c.shutdown(socket.SHUT_RDWR)
        c.close()
        print("closed connection with {}".format(username))


def spelling_check(file_to_checked, username):
    """
    Checks a file for spelling errors against lexicon.txt.
    ASSUMPTION: There is only one period at the end of each line.
    :param file_to_checked:
    :return: a file with [] around the misspelled word
    """
    # open the lexicon file
    with open('server_files/lexicon.txt') as lex_file:
        lex_array = lex_file.readline().split(" ")

    # open the file to be checked
    with open(file_to_checked) as file:
        text = file.readlines()

    array_checked_text = []
    # array of lower cased lexicon words
    lower_lex_array = [word.lower() for word in lex_array]
    # array of upper cased lexicon words
    upper_lex_array = [word.upper() for word in lex_array]
    # array of first letter upper cased and the rest lower cased lexicon words
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
        string_checked_text.append(" ".join(line) + '.\n')

    # write the annotated text to a file
    checked_file_name = "server_files/checked_text_{}.txt".format(username)
    with open(checked_file_name, 'w') as chked_file:
        chked_file.writelines(string_checked_text)

    return checked_file_name
