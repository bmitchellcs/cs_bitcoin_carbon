import pandas as pd
import pygsheets as p


class Hardware(object):
   
    '''
    a class to represent ASIC hardware
    ...
    Attributes
    ----------
    hardware : a dataframe of each ASIC product from each manufacturer
    
    Methods
    ---------
    prep_hardware: pulls the total units in current use, hash rate, and efficiency for each ASIC product from each manufacturer
    
    prod_calculation(failure): caculates the functional units for each ASIC product through 2021 Dec, given monthly production and annualized failure rates
    '''

    def __init__(self, hardware, start_date, end_date):
        '''
        Constructs all the necessary attributes for the hardware object.
        Parameters
        ----------
            hardware : dataframe
                structure of hardware database (as of 2020 Jan when this was developed)
        '''
        self.hardware = hardware
        self.start_date = start_date
        self.end_date = end_date

    def prep_hardware(self):
        '''
        Creates a subset of fields and formats the database for calculation.
        
        Result
        --------
        Updated dataframe of hardware database as of 2020 Jan
        Fields: ASIC product name, manufacturer name, Units in use as of 2020 Jan, Hash rate per product, and efficiency (GH/J)
        
        
        '''
        
        #self.hardware.columns = self.hardware.iloc[0]
        self.hardware = self.hardware[['Hardware ID',
                            'Unit Name',
                            'Manufacturer',
                            'Total Units in Current Use',
                            'Hash Rate per Unit (TH/s)',
                            'GH/J']].copy()
        self.hardware = self.hardware.drop([0])
        self.hardware['Total Units in Current Use'] = self.hardware['Total Units in Current Use'].map(lambda x : float(str(x).replace(',','')))
        self.hardware['GH/J'] = self.hardware['GH/J'].map(lambda x : float(str(x).replace(',','')))
        self.hardware['Hash Rate per Unit (TH/s)'] = self.hardware['Hash Rate per Unit (TH/s)'].map(lambda x : float(str(x).replace(',','')))
    
    def prod_calculation(self, failure, production):
        '''
        Calculates the functional units for each ASIC product through 2021 Dec, given monthly production and annualized failure rates
        
        Parameters
        ----------
        failure : Series, mandatory
            Passes the annual failure rate of each ASIC product
            Fields: ASIC product, failure rate
            
        Calculation
        -----------
        Assigns monthly production rates of each ASIC product in the hardware database, then adds produced units and subtracts failed units for each month until 2021 Dec.
        
        Result
        --------
        Dataframe of functional units for each ASIC product
        Fields: Hardware ID, Date , Units Produced, Total Failed Units, and Total Functional Units
        '''
        
        start = self.hardware[['Hardware ID', 'Total Units in Current Use', 'Unit Name']]
        start['Date'] = pd.datetime(2019,12,31)
        #len(hardware['Unit Name'].values)

        date_range = pd.date_range(self.start_date, self.end_date, freq='M')

        all_figures = []
        counter = 1
        for d in date_range:
            df = start.copy()
            df['Date'] = d
            df = pd.merge(df, failure, on= ['Hardware ID'])
            df = pd.merge(df, production, on= ['Hardware ID'])
            df['Total Failed Units'] = (df['Total Units in Current Use'] * (df['Annual Failure Rate']/12))
            df['Total Functional Units'] = (df['Total Units in Current Use'])
            counter += 1
            all_figures.append(df)

        df = pd.concat(all_figures)[['Hardware ID', 'Date','Total Units in Current Use', 'Monthly Units Produced','Total Failed Units', 'Total Functional Units','Annual Failure Rate']]
        units = df['Hardware ID'].unique()

        all_functional = []
        for i in units:
            u = df[df['Hardware ID'] == i]
            for d in date_range:
                u['Total Functional Units'] = (u.shift(1, fill_value = u['Total Units in Current Use'].iloc[0])['Total Functional Units'] + u['Monthly Units Produced']) * (1 - (u['Annual Failure Rate']/12))
                u['Total Failed Units'] = (u.shift(1, fill_value = u['Total Failed Units'].iloc[0])['Total Functional Units'] + u['Monthly Units Produced']) * ((u['Annual Failure Rate']/12))
            all_functional.append(u)

        self.functional_units = pd.concat(all_functional)[['Hardware ID', 'Date', 'Monthly Units Produced','Total Failed Units', 'Total Functional Units']]