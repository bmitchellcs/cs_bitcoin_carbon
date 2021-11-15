# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pygsheets as p
import pandas as pd
import streamlit as st
import altair as alt
import base64

import mining_module.hardware as hard_ware
import mining_module.hash_rate as hash_rate
from mining_module.units_in_use import *
import mining_module.energy_data as energy_data

st.header('CoinShares Bitcoin Carbon Calculator (Prototype)')

hardware = pd.read_excel('data.xlsx', 'Hardware Database',header=0)

failure = pd.read_excel('data.xlsx', 'Unit Failure Rate Change Log', header=0)
failure['Annual Failure Rate'] = failure['Annual Failure Rate'].map(lambda x : float(x))

production = pd.read_excel('data.xlsx', 'Unit Production Rate Change Log', header=0 )
hash = hash_rate.Hash()
hash.pull_hash()

hard = hard_ware.Hardware(hardware, '1/1/2020', '12/1/2021')

hard.prep_hardware()
hard.prod_calculation(failure, production)

monthly_hash = hash.btc_hash.groupby(pd.Grouper(freq='M')).mean()
efficiency = hardware[['Hardware ID', 'Hash Rate per Unit (TH/s)', 'GH/J']].iloc[1:,:].copy()
efficiency['GH/J'] = efficiency['GH/J'].map(lambda x : float(str(x).replace(',','')))
efficiency.sort_values('GH/J',ascending=False,inplace=True)

#add unit efficiency to the number of functional units
merged = pd.merge(hard.functional_units, efficiency, on='Hardware ID')
merged['Hash Rate per Unit (TH/s)'] = merged['Hash Rate per Unit (TH/s)'].map(lambda x : float(str(x).replace(',','')))
merged['Total Possible Hash Rate'] = merged['Total Functional Units']*merged['Hash Rate per Unit (TH/s)']
monthly_hash.reset_index(inplace=True)

na = NonceAdjuster()
monthly_hash_adj = na.adjust_hash(monthly_hash)


# %%
#calculate units in use per month based on monthly average hash rate
uiu = units_in_use(merged, monthly_hash_adj)
assert capacity_check(uiu, monthly_hash_adj)

uiu = na.append_uiu(uiu)

#what is iour estimate of the energy used by the network in a given month?
network_energy = uiu.groupby(pd.Grouper(key='Date', freq='M')).sum()['MWh'].copy()
#if we don't have hash rate % by region it'll be a null as we're right joining on network_energy
energy_merged = pd.merge(energy_data.energy_region, network_energy, how='right', left_on='Date', right_index=True)
energy_merged['Source'] = energy_merged['Source'].map(lambda x : str.strip(str(x)))
energy_merged['Regional Energy Consumption'] = energy_merged['Network Pct']*energy_merged['MWh']

emissions = pd.read_excel('data.xlsx', 'Emissions per Energy Source',usecols="A:B", header=0)
emissions['Pounds CO2 per MWh'] = emissions['Pounds CO2 per MWh'].map(lambda x : float(x))

#emissions joined into energy by source
emissions_merged = pd.merge(energy_merged, emissions, how='left', left_on='Source', right_on='Fossil Fuel')

emissions_merged = emissions_merged.fillna(0)
emissions_merged['Tons of CO2'] = (emissions_merged['Regional Energy Consumption']*emissions_merged['Pounds CO2 per MWh'])/2204.63



hardware_columns = ['Hardware ID', 'Unit Name', 'Manufacturer', 'Marginal',
        'Hash Rate Per Chip (TH/s)', 'Chip Name',
    'Chips per Unit', 'Total Chips', 'Hash Rate per Unit (TH/s)',
    'CAPEX $/(TH/s)', 'GH/J', 'Total GH/J',
        'Annual Unit Production Rate',
    'Annual Failure Rate', 
        'Estimated Total Hash Rate (TH/s)',
    'Total Hashing Power (MW)', 'Total Power Cooling (MW)',
    'Total Power (MW)', 'Monthly Electricity Usage (MWh)',
    'Annual Electricity Usage (MWh)']
emissions_merged.to_csv('output/emissions.csv')
hardware.drop([0],inplace=True)
hardware[hardware_columns].to_csv('output/hardware.csv')
uiu.to_csv('output/units_in_use.csv')




carbon_cost = st.number_input('Carbon credit cost per tonne CO2 (EUR):',min_value=0., max_value=300., value=20.00)
btc_price = st.number_input('Bitcoin Price (USD)', min_value = 0,value=34000)

col1, col2 = st.beta_columns(2)


col1.header(round((uiu[uiu['time']==uiu['time'].max()]['MWh'].sum()/10**6)*12))
col1.write('Annualized Network Energy Usage (TWh)')
# %%
uiu['Current Hash'] = uiu['Units in Use']*uiu['Hash Rate per Unit (TH/s)']
network_efficiency = uiu.groupby('Date',as_index=False).sum()[['Date', 'Current Hash', 'MW']]
network_efficiency['Efficiency'] = (network_efficiency['MW']*10**6)/network_efficiency['Current Hash']


start_date = emissions_merged['Date'].max() - pd.Timedelta(365,'D')
trailing_emissions = emissions_merged[emissions_merged['Date']>start_date]['Tons of CO2'].sum()
col2.header(round((trailing_emissions/10**6),2))
col2.write('Network CO2 Emissions (Trailing 12 Months) Millions Tonnes')


col1.header('{} EUR'.format(round((trailing_emissions/20**6)*carbon_cost,2)))
col1.write('Cost of Carbon Offsetting 1 BTC (Trailing 12 Months)')


val = round(((trailing_emissions/20**6)*carbon_cost)/(btc_price/.86),6)
col1.header('{} bps'.format(val*10000))
col1.write('% Cost of Carbon Offsetting (Trailing 12 Months, .86 USD/EUR)')

max_date = emissions_merged['Date'].max()

rr_emissions = emissions_merged[emissions_merged['Date']==max_date]['Tons of CO2'].sum()

col2.header('{} EUR'.format(round(((rr_emissions*12)/20**6)*carbon_cost,2)))
col2.write('Cost of Offsetting 1 BTC (Run Rate Annualized)')


val2 = ((rr_emissions/20**6)*carbon_cost)/(btc_price/.86)
col2.header('{} bps'.format(round(val2*10000,3)))
col2.write('% Cost of Carbon Offsetting (Run Rate Annualized, .86 USD/EUR')


st.header('Hardware Estimates')
uiu_display = pd.merge(uiu, hardware, how='inner', on='Hardware ID')[['Unit Name', 'time', 'GH/J_y', 'Monthly Units Produced', 'Total Failed Units', 'Total Functional Units', 'Units in Use']]
uiu_display = uiu_display[uiu_display['time'] == uiu_display['time'].max()]

uiu_display

st.write('BTC Hash Rate TH/s')
c = alt.Chart(monthly_hash).mark_bar().encode(x='time', y= 'values')
st.altair_chart(c, use_container_width=True)

st.write('Bitcoin Network Efficiency J/Th')
h = alt.Chart(network_efficiency).mark_line().encode(x='Date', y='Efficiency')
st.altair_chart(h,use_container_width=True)

regional_energy = emissions_merged.groupby(['Date', 'Country']).sum()[['Regional Energy Consumption']].reset_index()
regional_energy = regional_energy[regional_energy['Country']!=0].copy()
d = alt.Chart(regional_energy).mark_area().encode(x='Date', y='Regional Energy Consumption', color='Country')
st.write('Regional Energy Consumption MWh')
st.altair_chart(d, use_container_width=True)

regional_co2 = emissions_merged.groupby(['Date', 'Country']).sum()[['Tons of CO2']].reset_index()
regional_co2 = regional_co2[regional_co2['Country']!=0].copy()
e = alt.Chart(regional_co2).mark_area().encode(x='Date', y='Tons of CO2', color='Country')
st.write('Tons of CO2 by Region')
st.altair_chart(e, use_container_width=True)


source_energy = emissions_merged.groupby(['Date', 'Source']).sum()[['Regional Energy Consumption']].reset_index()
f = alt.Chart(source_energy).mark_area().encode(x='Date', y='Regional Energy Consumption', color='Source')
st.write('Energy Consumption MWh by Source')
st.altair_chart(f, use_container_width=True)

source_co2 = emissions_merged.groupby(['Date', 'Source']).sum()[['Tons of CO2']].reset_index()
g = alt.Chart(source_co2).mark_area().encode(x='Date', y='Tons of CO2', color='Source')
st.write('Tons of CO2 by Source')
st.altair_chart(g, use_container_width=True)

df = emissions_merged.groupby(['Date']).sum()[['Tons of CO2']].reset_index()
df




st.balloons()
