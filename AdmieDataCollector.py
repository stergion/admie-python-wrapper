import csv
import datetime
import os
import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
from tqdm import tqdm

import admie_fileparsers

IMPLEMENTED_FILETYPES = ['DailyEnergyBalanceAnalysis']

FREQ_TO_ALIAS = {
    "week": 'W',
    "month": 'M',
    "quarter": "Q",
    "year": 'Y',
}

ALIAS_TO_FREQ = {
    'W': 'week',
    'M': "month",
    'Q': 'quarter',
    'Y': 'year,'
}

ALL_FILETYPES = ['AdhocISPResults', 'CurrentLineOutages', 'CurrentProtectionOutages',
                 'CurrentSubstationOutages', 'DailyAuctionsSpecificationsATC',
                 'DailyEnergyBalanceAnalysis',
                 'DayAheadLoadForecast', 'DayAheadRESForecast', 'DayAheadSchedulingRealTimeDeviations',
                 'DayAheadSchedulingRequirements', 'DayAheadSchedulingUnitAvailabilities', 'Devit',
                 'Devnor', 'DispatchSchedulingResults', 'ExPostImbalancePricingResults', 'HVCUSTCONS',
                 'IMBABE', 'InterconnectionsMaintenanceSchedule', 'IntraDayDispatchSchedulingResults',
                 'ISP1DayAheadLoadForecast', 'ISP1DayAheadRESForecast', 'ISP1ISPResults',
                 'ISP1Requirements',
                 'ISP1UnitAvailabilities', 'ISP2DayAheadLoadForecast', 'ISP2DayAheadRESForecast',
                 'ISP2ISPResults',
                 'ISP2Requirements', 'ISP2UnitAvailabilities', 'ISP3IntraDayLoadForecast',
                 'ISP3IntraDayRESForecast',
                 'ISP3ISPResults', 'ISP3Requirements', 'ISP3UnitAvailabilities', 'ISP4Requirements',
                 'ISPWeekAheadLoadForecast', 'LTPTRsNominationsSummary', 'MonthlyLoadForecast',
                 'MonthlyNTC',
                 'MonthlySIPResults', 'ProvisionalLineOutages', 'ProvisionalProtectionOutages',
                 'ProvisionalSubstationOutages', 'RealTimeSCADAImportsExports', 'RealTimeSCADARES',
                 'RealTimeSCADASystemLoad', 'recovery_cost', 'ReservoirFillingRate', 'RESMV',
                 'RESMVLVPROD',
                 'SignificantEvents', 'SYSBOUNDS', 'SystemEstimationsCorrections',
                 'SystemRealizationSCADA',
                 'UA_ANALYSIS', 'UnitAvailabilities', 'UnitProduction', 'UnitsMaintenanceSchedule',
                 'WeekAheadLoadForecast', 'WeekAheadWaterUsageDeclaration', 'YearlyLoadForecast',
                 'YearlyWaterUsageDeclaration']


class AdmieDataCollector:

    def __init__(self, startDate: str, endDate: str, destDir: str | Path, fileType, file=None):
        # API query variables
        self.startDate = datetype(startDate)
        self.endDate = datetype(endDate)
        self.destDir = Path(destDir)
        self.fileType = fileType
        self.file = file

        self.baseQueryURL = 'https://www.admie.gr/getOperationMarketFilewRange'
        self.fileInfoURL = 'https://www.admie.gr/getFiletypeInfo'
        self.all_filetypes = ALL_FILETYPES
        self.downloadedFiles = {'date': [], 'filepath': [], 'description': []}

        # # Initialize argument parser
        # self.parser = argparse.ArgumentParser(description='Wraps the ADMIE data collection API',
        #                                       prog='ADMIE API Wrapper')
        # self.parser.add_argument('-s', '--startDate', type=str,
        #                          help='''Select start date for the query, date format: YYYY-MM-DD''')
        # self.parser.add_argument('-e', '--endDate', type=str,
        #                          help='''Select end date for the query, date format: YYYY-MM-DD''')
        # self.parser.add_argument('-d', '--destDir', help='''Select directory to save the data''')
        # self.parser.add_argument('-f', '--file', help='''Select a file as input for executing batch API queries.
        # The file should be CSV file with have the following format:
        #  startDate1,endDate1,filetype1
        #  startDate2,endDate2,filetype2
        #  ...
        #  startDateN,endDateN,filetypeN
        #  ''')
        # self.parser.add_argument('-t', '--type',
        #                          help='Select file type from the available file types according to the ADMIE API:',
        #                          choices=self.all_filetypes + ['info'])
        #
        # self.parser.add_argument('--version', action='version', version='%(prog)s  1.0')
        # self.args = self.parser.parse_args()
        # Apply argument constrains
        # self.checkArgConstrains()

    # Executes the API queries
    def run(self, ):
        if self.file and os.path.isfile(self.file):
            self.executeBatchQuery()
        else:
            self.executeQuery()

    # Query process
    def executeQuery(self, params={}):
        if not params:
            params = {'dateStart': self.startDate,
                      'dateEnd': self.endDate,
                      'FileCategory': self.fileType}

        if 'info' in params['FileCategory']:
            self.showAllFileTypes()
        else:
            self.checkApiParams(params)
            req = requests.get(self.baseQueryURL, params=params)
            self.downloadFiles(req)

            # Batch query process

    def executeBatchQuery(self, ):
        with open(self.file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for i, row in enumerate(csv_reader, start=1):
                try:
                    params = {'dateStart': row[0],
                              'dateEnd': row[1],
                              'FileCategory': row[2]}
                    self.executeQuery(params=params)
                except:
                    # self.parser.error('\nATTENTION: Error in CSV file format in line %s' % i)
                    print('\nATTENTION: Error in CSV file format in line %s' % i)

    # Check query parameters constrains
    def checkApiParams(self, params):
        # datetype(params['dateStart'])
        # datetype(params['dateEnd'])
        if params['FileCategory'] not in self.all_filetypes:
            raise Exception()

    # Check argument constrains
    # def checkArgConstrains(self, ):
    #     if self.args.file:
    #         self.checkConfigFileConstains()
    #
    #     if self.args.startDate or self.args.endDate:
    #         self.checkDateConstains()
    #
    #     if list(self.args.__dict__.values()) == [None, None, None, None, None]:
    #         self.parser.error('\nATTENTION: No arguments were selected')

    # Check date argument constrains
    def checkDateConstains(self, ):
        if self.startDate and not self.endDate:
            self.parser.error('\nATTENTION: -e/--endDate is required when -s/--startDate is set.')
        if self.endDate and not self.startDate:
            self.parser.error('\nATTENTION: -s/--startDate is required when -e/--endDate is set.')
        if self.endDate < self.startDate:
            self.parser.error('\nATTENTION: Start date cannot be after end date')

    # Check input file argument constrains
    def checkConfigFileConstains(self, ):
        if self.startDate or self.endDate or self.type:
            self.parser.error(
                '\nATTENTION: Only destination (-d|--destDir) argument is needed with input file (-f|--file) argument')
        if not os.path.isfile(self.file):
            self.parser.error('\nATTENTION: File does not exist')

    # Display all file types and available information
    def showAllFileTypes(self, ):
        # Fetch request
        jsonResp = requests.get(self.fileInfoURL).json()
        print('Available file types:')
        for element in jsonResp:
            filetype = element['filetype']
            time_gate = element['EN'][0]['time_gate']

            publication_frequencyGR = element['GR'][0]['publication_frequency']
            publication_frequencyEN = element['EN'][0]['publication_frequency']

            data_typeGR = element['GR'][0]['data_type']
            data_typeEN = element['EN'][0]['data_type']

            print('''
         * type: "%s"
            - description: %s %s / %s %s
            - when: %s

         ''' % (filetype,
                publication_frequencyGR, data_typeGR,
                publication_frequencyEN, data_typeEN,
                time_gate))

    # Download query results
    def downloadFiles(self, req):
        # Begin counting
        start_time = time.time()

        jsonResp = req.json()
        # Create destination path
        destDir = self.destDir
        if not os.path.exists(destDir):
            os.makedirs(destDir)

        if len(jsonResp) == 0:
            print('No results found for request: %s' % req.url)
        else:
            print('Starting files downloading...')
            processBar = tqdm(jsonResp)
            for element in processBar:
                try:
                    # element attributes
                    url = element['file_path']
                    description = element['file_description']

                    # file destination
                    filename = url.split('/')[-1]
                    filepath = os.path.join(destDir, filename)

                    # initiate file request
                    processBar.set_description("  Downloading file: %s" % filename)
                    req = requests.get(url, allow_redirects=True)

                    # save file locally
                    with open(filepath, 'wb') as f:
                        f.write(req.content)
                        self.downloadedFiles['filepath'].append(filepath)
                        self.downloadedFiles['description'].append(description)
                        self.downloadedFiles['date'].append(filename.split('_')[0])

                except Exception as e:
                    print('Error in request: %s' % str(e))
        print("--- Finished in %s seconds ---" % round(time.time() - start_time, 2))


# Handle date type arguments
def datetype(dateString):
    try:
        date = datetime.datetime.strptime(dateString, '%Y-%m-%d')  # accept only dates with specific format
    except ValueError:
        print(
            'Error for value %s. -s/--startDate and -e/--endDate arguments have to '
            'follow the format YYYY-MM-DD' % dateString)
        exit(1)
    return date


FILE_PARSER_MAP = {
    "DailyEnergyBalanceAnalysis": admie_fileparsers.dailyEnergyBalanceAnalysis_parser
}


class DataFormatter:
    def __init__(self, fileType: str, basePath: str | Path = ".", exportPath: str | Path = "."):
        self.data_freqAlias = 'D'
        self.data_freq = 'Day'
        self.data_aggr = 'sum'
        self.data: pd.DataFrame | None = None
        self.fileType = fileType
        self.basePath = Path(basePath)
        self.exportPath = Path(exportPath)
        self.fileParser = FILE_PARSER_MAP[self.fileType]

    def getFilePaths(self) -> list[Path]:
        filePaths = []
        filePaths.extend(
            list(Path(self.basePath).glob(f'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_{self.fileType}_01.xls')))
        filePaths.extend(
            list(Path(self.basePath).glob(f'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_{self.fileType}_01.xlsx')))
        return filePaths

    def loadFiles(self):
        filePaths = self.getFilePaths()
        df_list = [self.fileParser(filePath) for filePath in filePaths]
        self.data = pd.concat(df_list)

    def resample(self, freq, aggregation='sum'):
        if freq in FREQ_TO_ALIAS.keys():
            _freq = freq
            _freqAlias = FREQ_TO_ALIAS[freq]
        elif freq in ALIAS_TO_FREQ.keys():
            _freqAlias = freq
            _freq = ALIAS_TO_FREQ[freq]
        else:
            raise ValueError(f"freq must be one of {list(FREQ_TO_ALIAS.keys()) + list(ALIAS_TO_FREQ.keys())}")

        if aggregation == 'sum':
            self.data = self.data.resample(_freqAlias).sum()
            self.data_aggr = 'sum'
        elif aggregation == 'mean':
            self.data = self.data.resample(_freqAlias).mean()
            self.data_aggr = 'mean'
        else:
            raise ValueError(f"freq must be one of ['sum', 'mean']")

        self.data_freq = _freq
        self.data_freqAlias = _freqAlias

    def plot(self, title=None, save=False, fileName=None, figsize=(10, 6)):
        ax = self.data.plot(figsize=figsize)
        ax.set_ylabel('MWh', fontsize='large')
        title = title if title else f'{self.fileType} {self.data_aggr} over {self.data_freq}'
        ax.set_title(title, fontsize='xx-large')
        ax.legend(bbox_to_anchor=(1, 1))

        if save:
            fileName = f"{self.fileType}.png" if not fileName else fileName
            plt.savefig(fileName, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()

    def to_excel(self, fileName=None):
        if self.data is None:
            raise TypeError(f"Expected DataFrame, got None instead."
                            f"Try running self.loadFiles() first.")

        filename = f"{self.fileType}.xlsx" if fileName is None else fileName
        self.data.to_excel(filename)

# if __name__ == "__main__":
#     print("main Admie")
#     # fetch files
#     run_admieDataCollector()
