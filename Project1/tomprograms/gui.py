"""
https://pysimplegui.readthedocs.io/en/latest/cookbook/
"""
import PySimpleGUI as sg
import time
import threading, socket

from tomprograms.client import Client
from tomprograms.layouts import server_layout, client_layout, delete_output
from tomprograms.server import Server


class GUI:
    def __init__(self, name, is_server=False):
        self.is_server = is_server

        if is_server:
            self.layout = server_layout
            self.host = Server()
        else:
            self.layout = client_layout
            self.host = Client()
        self.loged_in = False

        self.window = sg.Window(name, self.layout)

    def run(self):
        while True:  # Event Loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                print("here")
                delete_output(is_server=self.is_server, layout_used=self.layout)
                if self.is_server:
                    self.host.s.shutdown(socket.SHUT_RD)
                break
            # client
            if not self.is_server:
                self.host.reconnect()
                if event == 'Submit':
                    print("Trying to log in: {}".format(values[0]))
                    self.loged_in = self.host.login(values[0])
                if self.loged_in:
                    print('You are logged in')
                    # print('About to go to call my long function')
                    # self.host.main()
                    thread = threading.Thread(target=self.host.main)
                    thread.start()
                    # print('Long function has returned from starting')
                else:
                    print("Could not login")
            # server
            else:
                if event == 'Go':
                    self.window.FindElement('Go').Update(disabled=True)
                    # print('About to go to call my long function')
                    thread = threading.Thread(target=self.host.accept_connections)
                    thread.start()
                    # print('Long function has returned from starting')
                elif event == 'Client List':
                    print("Client List Online: {}".format(self.host.online_user_list))
                elif event == '-THREAD DONE-':
                    print('Your long operation completed')
                else:
                    print(values)
        self.window.close()

    def print_to_output(self, text, key):
        self.window.write_event_value(key=key, value=text)

# server = GUI("server", is_server=True)
# client = GUI("client", is_server=False)
# server.run(long_function)
# client.run(long_function())
