"""
@author: Fotios Lygerakis
@UTA ID: 1001774373
"""
import socket
import threading
import PySimpleGUI as sg
from client import Client
from utils import server_layout, client_layout, delete_output
from server import Server

"""
Code based on https://pysimplegui.readthedocs.io/en/latest/cookbook/
"""


class GUI:
    def __init__(self, name, is_server=False):
        self.is_server = is_server

        # chose the appropriate layout for the server and the client
        if is_server:
            self.layout = server_layout
            self.host = Server()
        else:
            self.layout = client_layout
            self.host = Client()
        self.logged_in = False

        # create a window
        self.window = sg.Window(name, self.layout)

    def run(self):
        """
        Function for handling the GUI
        """

        while True:
            # read the events on the gui and their values
            event, values = self.window.read()
            # exit gui when window is closed or Exit button is pressed
            if event == sg.WIN_CLOSED or event == 'Exit':
                # delete server's layout components
                delete_output(is_server=self.is_server, layout_used=self.layout)
                if self.is_server:
                    self.host.s.shutdown(socket.SHUT_RD)
                break
            # Client's gui
            if not self.is_server:
                # connect to the server
                self.host.reconnect()
                # on submit button take the username that has been entered
                if event == 'Submit':
                    # try to log in with the given username
                    print("Trying to log in: {}".format(values[0]))
                    self.logged_in = self.host.login(values[0])
                # if client has been logged in, start a thread with its functionality
                if self.logged_in:
                    print('You are logged in')
                    thread = threading.Thread(target=self.host.main)
                    thread.start()
                else:
                    print("Could not login")
            # Server's gui
            else:
                # start a thread for the server when the Go button is pressed
                if event == 'Go':
                    # deactivate Go button
                    self.window.FindElement('Go').Update(disabled=True)
                    thread = threading.Thread(target=self.host.accept_connections)
                    thread.start()
                # when "Client List" button is pressed the online usernames are being printed on the gui
                elif event == 'Client List':
                    print("Client List Online: {}".format(self.host.online_user_list))
                # otherwise print the values in the gui
                else:
                    print(values)
        self.window.close()


