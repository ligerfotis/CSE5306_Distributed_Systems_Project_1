"""
@author: Fotios Lygerakis
@UTA ID: 1001774373
"""
import os
import PySimpleGUI as sg
from config import BUFFER_SIZE, lexicon_file

"""
Server and Client GUI layouts
"""

server_layout = [[sg.Output(size=(60, 20))],
                 [sg.Button('Go'), sg.Button('Client List'), sg.Button('Exit')]]

client_layout = [[sg.Text('Please enter username')],
                 [sg.Text("Username", size=(15, 1)), sg.InputText(), sg.Button("Login")],
                 [sg.Button("Send File")],
                 [sg.Output(size=(60, 20))],
                 [sg.Text("Add lexicon entry", size=(15, 1)), sg.InputText()],
                 [sg.Button("Add")],
                 [sg.Button('Exit')]]


def delete_output(is_server, layout_used):
    """
    Delete layout objects if request from server
    :param is_server: Boolean. If is is used by a server is true
    :param layout_used: the type of PySimpleGUI that is used
    """
    if is_server:
        layout_used[0][0].__del__()
    else:
        layout_used[3][0].__del__()


def send_file(c, file_name):
    """
    Sends file_name to connection c in BUFFER_SIZE packets
    :param c: connection
    :param file_name: file name string
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
    :param c: connection
    :param file_name: file name string
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


def spelling_check(file_to_checked, username):
    """
    Checks a file for spelling errors against lexicon.txt.
    ASSUMPTION: There is only one period at the end of each line.
    :param username: username string
    :param file_to_checked: file name to be spelling-checked
    :return: a file with [] around the misspelled word
    """
    # open the lexicon file
    with open('server_files/{}'.format(lexicon_file)) as lex_file:
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
