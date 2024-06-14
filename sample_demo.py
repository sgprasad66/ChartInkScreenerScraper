''' import PySimpleGUI as sg

layout = [
            [sg.Text('1. '), sg.In(key=1)],
            [sg.Text('2. '), sg.In(key=2)],
            [sg.Text('3. '), sg.In(key=3)],
            [sg.Text('4. '), sg.In(key=4)],
            [sg.Text('5. '), sg.In(key=5)],
            [sg.Button('Save'), sg.Button('Exit')]
         ]

window = sg.Window('To Do List Example', layout)
event, values = window.read() '''

import PySimpleGUI as sg

values_data = [['BANKNIFTY65', 'BUY'], ['BANKNIFTY65, Cell-1', 'BANKNIFTY65, Cell-2'],['BANKNIFTY65, Cell-1', 'BANKNIFTY65, Cell-2']]
layout = [[sg.Table(values=values_data,
                 headings=['Header 1', 'Header 2'],
                 key='table',
                 num_rows=3,
                 enable_events=True,
                 enable_click_events=True,
                 col_widths=[100, 100])]]

window = sg.Window('Table Example', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'table':
        data_selected = values['table'][0]
        print(values_data[data_selected])
        sg.popup(values_data[data_selected][1])
        #print('Row {} Column {}'.format(values['table'][0], values['table'][1]))

window.close()