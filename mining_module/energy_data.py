# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import pygsheets as p
from pandas.tseries.offsets import MonthEnd
import coinmetrics as cm


# %%


# %%
#gc = p.authorize(service_account_file='stinky-pete-292910-535cd0211640.json')
#sh = gc.open_by_key('1qS9zGvEILTMaYp8NUY7kLBKC4-SCJ3rPEEHhFKizZkU')
#hash_region = pd.DataFrame(sh.worksheet('title', 'Hash Rate by Region').get_all_records())
hash_region = pd.read_excel('./data.xlsx', 'Hash Rate by Region')
hash_region.set_index('Date',inplace=True)
hash_region = pd.DataFrame(hash_region.stack()).reset_index()
# %%
hash_region['Country'] = hash_region['level_1'].map(lambda x : x.split(" - ")[0])
hash_region['Region'] = hash_region['level_1'].map(lambda x : x.split(" - ")[1])
# %%
# %%
hash_region = hash_region[['Date',  0, 'Country', 'Region']]
hash_region.columns = ['Date', '%', 'Country', 'Region']
# %%


# %%
#energy = pd.DataFrame(sh.worksheet('title', 'Energy by Source').get_all_records())
energy = pd.read_excel('./data.xlsx', 'Energy by Source')
twenty_twenty = energy.set_index(['Country', 'Region']).stack().reset_index()
twenty_twenty.columns = ['Country', 'Region', 'Source', 'Pct']


# %%
energy_region = pd.merge(hash_region,twenty_twenty,how='left',on=['Country', 'Region'])
energy_region['%'] = energy_region['%']/100
energy_region['Pct'] = energy_region['Pct']/100
energy_region['Pct'] = energy_region['Pct'].fillna(1)
energy_region['Network Pct'] = energy_region['%'] * energy_region['Pct']

#shifts monthly data to month end to align with hardware data
energy_region['Date'] = pd.to_datetime(energy_region['Date'], utc=True) + MonthEnd(1)


# %%
#join in network MWh by month
#join in carbon per MWh by Source -> carbon per region, per source per month
#find carbon credit pricing source
#price carbon offset per bitcoin per month
#decide which charts/tables to display

#this needs to run off of a public source

key = 'xKycygBlR8RFsEXXjkbp'
#pull btc per month
api = cm.Base(key)
res = api._api_query('/assets/{}/metricdata'.format('btc'),
                     options={'api_key':'xKycygBlR8RFsEXXjkbp','metrics':'SplyCur'})
a = pd.DataFrame(res['metricData']['series'])
a['time'] = pd.to_datetime(a['time'])
a['values'] = a['values'].map(lambda x : float(x[0]))
btc_supply = a.groupby(pd.Grouper(key='time', freq='M')).mean()
