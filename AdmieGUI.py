import PySimpleGUI as sg

from AdmieDataCollector import AdmieDataCollector, DataFormatter
from AdmieDataCollector import IMPLEMENTED_FILETYPES, FREQ_TO_ALIAS, ALIAS_TO_FREQ


def admieGUI():
    sg.theme('Dark')
    fileType = None
    fromDate = None
    toDate = None

    filetypes_combobox = sg.Combo(values=IMPLEMENTED_FILETYPES, key='fileType', size=(50, 1), font='Lucida 12')
    resample_combobox = sg.Combo(values=list(FREQ_TO_ALIAS.keys()), default_value=ALIAS_TO_FREQ['M'], key='freq',
                                 size=(10, 1), font='Lucida 12')
    aggregation_combobox = sg.Combo(values=['sum', 'mean'], default_value='sum', key='aggregation',
                                    size=(10, 1), font='Lucida 12')
    default_filename = get_default_filename(fileType, fromDate, toDate, )
    layout = [
        [sg.Text('AdmieDataCollector', size=(40, 1), font='Lucida 16', justification='left')],
        [sg.Text('File Type', size=(10, 1), font='Lucida 12', justification='left'), filetypes_combobox],
        [sg.Text('From Date', size=(10, 1), font='Lucida 12', justification='left'),
         sg.InputText(key='fromDate', justification='left'),
         sg.CalendarButton("Select Date", close_when_date_chosen=True, target="fromDate", format='%Y-%m-%d',
                           size=(10, 1), font='Lucida 12')],
        [sg.Text('To Date', size=(10, 1), font='Lucida 12', justification='left'),
         sg.InputText(key='toDate', justification='left'),
         sg.CalendarButton("Select Date", close_when_date_chosen=True, target="toDate", format='%Y-%m-%d',
                           size=(10, 1), font='Lucida 12')],
        [sg.Push(), sg.Button('Download')],
        [sg.Text('Resample Data', size=(13, 1), font='Lucida 12', justification='left'),
         resample_combobox, aggregation_combobox, sg.Button('Resample')],
        [sg.Text('Save as', size=(13, 1), font='Lucida 12', justification='left'),
         sg.InputText(key='save', default_text=default_filename, size=(50, 1), font='Lucida 12', justification='left'),
         sg.Push(), sg.Button('Save')],

        [sg.Text('Plot Data:', size=(15, 1), font='Lucida 14', justification='left')],
        [sg.Text('Title:', size=(13, 1), font='Lucida 12', justification='left'),
         sg.InputText(key='plot_title', size=(50, 1), font='Lucida 12', justification='left')],
        [sg.Text('Filename:', size=(13, 1), font='Lucida 12', justification='left'),
         sg.InputText(key='plot_filename', size=(50, 1), font='Lucida 12', justification='left'),
         sg.Checkbox(key='plot_save', text='save', font='Lucida 12'),
         sg.Push(), sg.Button('plot')],

        [sg.Output(size=(90, 10), font='Lucida 12')],
        [sg.Push(), sg.Button('Exit', button_color=('white', 'firebrick3'))],

    ]

    window = sg.Window('Admie Data Collector', layout,
                       text_justification='r',
                       default_element_size=(15, 1),
                       font='Any 14')

    dataForm = None

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

            window['save'].update(get_default_filename(fileType, fromDate, toDate))
            print(f'Downloading {fileType} from {fromDate} to {toDate}...')
            window.refresh()

            dataForm = run_initDownload(startDate=fromDate, endDate=toDate, fileType=fileType,
                                        destDir=f'./{fileType}_{fromDate.replace("_", "")}_{toDate.replace("_", "")}')
            window.refresh()

        if event == 'Save':
            if dataForm is None or dataForm.data is None:
                print("Download the data first")
                window.refresh()
                continue

            fileName = values['save']
            run_save(dataForm, filename=fileName)
            print(f'File saved as {fileName}')
            window.refresh()

        if event == 'Resample':
            if dataForm is None or dataForm.data is None:
                print("Download the data first")
                window.refresh()
                continue

            freq = values['freq']
            aggregation = values['aggregation']
            dataForm.resample(freq=freq, aggregation=aggregation)

            print(f'New sampling frequency:  {freq}')
            print(f'Aggregation method:  {aggregation}')
            window.refresh()

        if event == 'plot':
            if dataForm is None or dataForm.data is None:
                print("Download the data first")
                window.refresh()
                continue

            plot_title = values['plot_title']
            plot_filename = ".".join([values['plot_filename'].split('.')[0], 'png']) if values['plot_filename'] else None
            plot_save = values['plot_save']
            dataForm.plot(title=plot_title, save=plot_save, fileName=plot_filename)
            if plot_save:
                print("Plot was saved successfully")


    window.close()


def get_default_filename(fileType, fromDate, toDate):
    return f'{fileType}_{fromDate.replace("-", "")}_{toDate.replace("-", "")}.xlsx' if fileType is not None else 'filetype_fromDate_toDate.xlsx'


def run_initDownload(startDate, endDate, destDir, fileType, ):
    admie = AdmieDataCollector(startDate, endDate, destDir, fileType)
    admie.run()
    dataForm = DataFormatter(fileType, destDir)
    dataForm.loadFiles()
    return dataForm


def run_save(dataForm, filename):
    dataForm.to_excel(fileName=filename)


if __name__ == '__main__':
    admieGUI()
