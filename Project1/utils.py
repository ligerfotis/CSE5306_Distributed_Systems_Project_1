import os
import PySimpleGUI as sg
from config import BUFFER_SIZE

"""
Server and Client GUI layouts
"""

server_layout = [[sg.Output(size=(60, 20))],
                 [sg.Button('Go'), sg.Button('Client List'), sg.Button('Exit')]]

client_layout = [[sg.Text('Please enter username')],
                 [sg.Text("Username", size=(15, 1)), sg.InputText()],
                 [sg.Submit()],
                 [sg.Output(size=(60, 20))],
                 [sg.Button('Exit')]]


def delete_output(is_server, layout_used):
    """
    Delete layout objects if request from server
    :param is_server:
    :param layout_used:
    """
    if is_server:
        layout_used[0][0].__del__()
    else:
        layout_used[3][0].__del__()


def send_file(c, file_name):
    """
    Sends file_name to connection c in BUFFER_SIZE packets
    :param c:
    :param file_name:
    :return:
    """
    # open and read file
    print('Sending', file_name)
    file = open(file_name, 'rb')
    data = file.read(BUFFER_SIZE)

    # send the file in BUFFER_SIZE packets
    while data:
        c.send(data)
        data = file.read(BUFFER_SIZE)
    # send EOF string to let the receiver know that the whole file has been sent
    c.send('<EOF>'.encode())
    print('Successfully sent \"{}\"'.format(file_name))


def receive_file(c, file_name):
    """
    Receive a file from connection c in BUFFER_SIZE packets and store it to file_name
    :param c:
    :param file_name:
    :return:
    """
    # check if the file to store packets exists and remove it if so
    if os.path.exists(file_name):
        os.remove(file_name)

    # save received packets to a file
    with open(file_name, 'w') as file:
        while 1:
            data = c.recv(BUFFER_SIZE).decode()
            # the whole file has been sent
            if data == '<EOF>':
                break
            file.write(data)
    print('Successfully received \"{}\"'.format(file_name))
