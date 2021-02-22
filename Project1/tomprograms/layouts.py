import PySimpleGUI as sg

layout = [[sg.Text('Please enter username')],
          [sg.Text("Username", size=(15, 1)), sg.InputText()],
          [sg.Submit()],
          [sg.Output(size=(60, 20))],
          [sg.Button('Go'), sg.Button('Nothing'), sg.Button('Exit')]]

server_layout = [[sg.Output(size=(60, 20))],
                 [sg.Button('Go'), sg.Button('Client List'), sg.Button('Exit')]]

client_layout = [[sg.Text('Please enter username')],
                 [sg.Text("Username", size=(15, 1)), sg.InputText()],
                 [sg.Submit()],
                 [sg.Output(size=(60, 20))],
                 [sg.Button('Exit')]]


def delete_output(is_server, layout_used):
    if is_server:
        layout_used[0][0].__del__()
    else:
        layout_used[3][0].__del__()
