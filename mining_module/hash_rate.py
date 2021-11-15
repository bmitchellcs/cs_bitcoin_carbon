import pandas as pd
import coinmetrics as cm

class Hash(object):
    '''
    a class to represent Bitcoin network hashrate
    ...
    Attributes
    ----------
    None
    
    Methods
    ---------
    pull(field, asset=""): Calls and returns data from Coinmetrics API
    
    pull_hash(failure): Pulls and returns bitcoin network hashrate
    '''
    

    def _init__(self):
        pass
    
    '''Contructs the bitcoin network hashrate object'''

    def pull(self, field, asset= 'btc'):
        
        '''
        Calls Coinmetrics API and establishes structure of dataframe object
        Fields: time, values, field, asset
        
        Parameters
        -----------
            field : list
                each metric to request from Coinmetrics
            asset : list
                each asset to request from Coinmetrics
        Returns
        --------
        An empty dataframe
        '''
        
        key = 'xKycygBlR8RFsEXXjkbp'
        api = cm.Base(key)
        res = api._api_query('/assets/{}/metricdata'.format(asset),
                                options={'api_key':'xKycygBlR8RFsEXXjkbp','metrics':field})
        a = pd.DataFrame(res['metricData']['series'])
        a['time'] = pd.to_datetime(a['time'])
        a['values'] = a['values'].map(lambda x : float(x[0]))
        a['field'] = field
        a['asset'] = asset
        return a
    
    def pull_hash(self):
        '''
        pulls Bitcoin network hashrate from Coinmetrics API
        

        Returns
        --------
        A dataframe of bitcoin hashrate over time
        Fields: time, metric value, field called, asset called 
        '''
        
        fields = ['HashRate']
        asset_list = ['btc']
        results = []
        for asset in asset_list:

            for f in fields:
                results.append(self.pull(f, asset))

            df = pd.concat(results)

            df.set_index(['time'],inplace=True)
            df.columns=['values', 'field', 'asset']
            self.btc_hash = df.loc[(df.field == 'HashRate') & (df.asset == 'btc')]