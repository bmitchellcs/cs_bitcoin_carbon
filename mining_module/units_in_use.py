import pandas as pd
from mining_module.hash_rate import Hash


class NonceAdjuster(Hash):

    def __init__(self):
        h = Hash()
        self.s9 = pd.read_csv('S9 Units in Use.csv', parse_dates=['time'])
        self.s7 = pd.read_csv('S7 Units in Use.csv', parse_dates=['time'])
        self.s7['Units in Use'] = self.s7['Units in Use']/4.73
        self.s9['Units in Use'] = self.s9['Units in Use']/13.5
        self.s9_pct = pd.read_csv('S9 Hash Rate %.csv', parse_dates=['time'])
        self.s7_pct = pd.read_csv('S7 Hash Rate %.csv', parse_dates=['time'])
        



    def adjust_hash(self, monthly_hash):
        self.pct = pd.concat([self.s9_pct, self.s7_pct])
        self.pct = self.pct.groupby('time').sum()
        self.pct = self.pct.groupby(pd.Grouper(freq='M')).mean()
        self.pct = self.pct['values'].map(lambda x : (100-x)/100.)
        self.monthly_hash = monthly_hash
        comb = pd.merge(self.monthly_hash, pd.DataFrame(self.pct), how='inner', left_on='time', right_index=True)
        #print(comb)
        comb['values'] = comb['values_x']*comb['values_y']
        return comb[['time', 'values']]
        #down adjust hash to pass to UIU

    def append_uiu(self, uiu):
        deets = {'s7':['2286935e-fb39-47d8-bc96-e98a4d885873', 4.73, 4.00],
        's9':['d6069bc1-ef76-4e63-8a6e-9afb0a63633e', 13.5, 10.20]}
        self.s7['Hardware ID'] = deets['s7'][0]
        self.s7['Hash Rate per Unit (TH/s)'] = deets['s7'][1]
        self.s7['GH/J'] = deets['s7'][2]
        self.s9['Hardware ID'] = deets['s9'][0]
        self.s9['Hash Rate per Unit (TH/s)'] = deets['s9'][1]
        self.s9['GH/J'] = deets['s9'][2]
        self.hardware = pd.concat([self.s7, self.s9])
        self.hardware['Watts'] = (self.hardware['Hash Rate per Unit (TH/s)'] * self.hardware['Units in Use'])/(self.hardware['GH/J']/1000.0)
        self.hardware['MW'] = self.hardware['Watts']/10**6
        self.hardware['MWh'] = self.hardware['MW']*(24*30)
        #self.hardware.reset_index(inplace=True, drop=False)
        print(self.hardware.columns)
        self.hardware.columns = ['Date','Units in Use', 'Hardware ID', 'Hash Rate per Unit (TH/s)', 'GH/J',
       'Watts', 'MW', 'MWh']

        uiu = uiu[(uiu['Hardware ID']!= deets['s7'][0]) & (uiu['Hardware ID'] != deets['s9'][0])].copy()
        return pd.concat([uiu, self.hardware[self.hardware['Date']>'2020-1-1']])
        #pull in uiu
        #calculate Watts, MW and monthly MWh
        pass  




def units_in_use(merged, monthly_hash):
    dates = pd.unique(merged['Date'])
    all_dates = []
    for d in dates:
        test_df = merged[merged['Date'] == d]
        #reset so it'll merge with hash data
        test_df['Date'] = pd.to_datetime(test_df['Date'],utc=True)
        hash_merge = pd.merge(test_df, monthly_hash, left_on='Date', right_on='time', how='inner')
        hash_merge.sort_values('GH/J',ascending=False,inplace=True)
        hash_merge['Cumulative Possible Hash'] = hash_merge['Total Possible Hash Rate'].cumsum()
        #if residual hash is negative then those machines are not needed
        hash_merge['Residual Hash'] = hash_merge['values'] - hash_merge['Cumulative Possible Hash']
        hash_merge['Excess Units'] = hash_merge['Residual Hash']/hash_merge['Hash Rate per Unit (TH/s)']
        hash_merge['Excess Units'] = hash_merge['Excess Units'].map(lambda x : x if x<0 else 0)
        hash_merge['Units in Use'] = hash_merge['Total Functional Units'] + hash_merge['Excess Units']
        hash_merge['Units in Use'] = hash_merge['Units in Use'].map(lambda x : x if x>0 else 0)
        #GH/J / 1000 = TH/J
        hash_merge['Watts'] = (hash_merge['Hash Rate per Unit (TH/s)'] * hash_merge['Units in Use'])/(hash_merge['GH/J']/1000)
        hash_merge['MW'] = hash_merge['Watts']/10**6
        hash_merge['MWh'] = hash_merge['MW']*(24*30)
        all_dates.append(hash_merge)
    return pd.concat(all_dates)



def capacity_check(uiu, monthly_hash):
    check_capacity = uiu.groupby(pd.Grouper(key='Date', freq='1M')).max()['Cumulative Possible Hash'].copy()
    check = pd.merge(monthly_hash, check_capacity, left_on='time',right_index=True,how='right')
    check['Check'] = check['Cumulative Possible Hash']>check['values']
    if len(check[check['Check']!=True])==0:
        return True
    else:
        return False