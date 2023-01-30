import PySimpleGUI as sg

from AdmieDataCollector import IMPLEMENTED_FILETYPES, run_admieDataCollector
import PySimpleGUI as sg

from AdmieDataCollector import IMPLEMENTED_FILETYPES, run_admieDataCollector


def admieGUI():
    sg.theme('Dark')

    combobox = sg.Combo(values=IMPLEMENTED_FILETYPES, size=(50, 1), key='fileType', font='Lucida 12')
    layout = [
        [sg.Text('AdmieDataCollector', size=(40, 1), font='Lucida 12', justification='left')],
        [sg.Text('File Type'), combobox],
        [sg.Text('From Date', size=(15, 1), justification='left'), sg.InputText(key='fromDate', justification='left'),
         sg.CalendarButton("Select Date", close_when_date_chosen=True, target="fromDate", format='%Y-%m-%d',
                           size=(10, 1), font='Lucida 12')],
        [sg.Text('To Date', size=(15, 1), justification='left'), sg.InputText(key='toDate', justification='left'),
         sg.CalendarButton("Select Date", close_when_date_chosen=True, target="toDate", format='%Y-%m-%d',
                           size=(10, 1), font='Lucida 12')],

        [sg.Button('Exit', button_color=('white', 'firebrick3')), sg.Push(), sg.Button('Download')],
        [sg.Output(size=(90, 10), font='Lucida 12')],

    ]

    window = sg.Window('Admie Data Collector', layout,
                       text_justification='r',
                       default_element_size=(15, 1),
                       font='Any 14')

    while True:
        event, values = window.read()
        if event in ('Exit', None):
            break  # exit button clicked

        if event == 'Download':
            fileType = values['fileType']
            fromDate = values['fromDate']
            toDate = values['toDate']

            if not fileType:
                print("Please select a File Type")
                window.refresh()
                continue
            if not fromDate:
                print("Please select a fromDate")
                window.refresh()
                continue
            if not toDate:
                print("Please select a toDate")
                window.refresh()
                continue

            print(f'Downloading {fileType} from {fromDate} to {toDate}...')
            window.refresh()

            run_admieDataCollector(startDate=fromDate, endDate=toDate, fileType=fileType, destDir=f'./{fileType}')
            window.refresh()

    window.close()


if __name__ == '__main__':
    admieGUI()
