# miningmodel

1) Estimate total number of each model produced since inception
2) Assume a failure rate for each model
3) Estimate number of serviceable units by month
4) Estimate units in use per month on the assumption that the least marginal will always be in production and most marginal will come in and out of production
5) Derive estimated network power consumption

Parameters
- Start date and end date: the dates we do our hardware estimations for determines units in use
- Oxford 2019 energy source by country data (see energy_data.py)



Sources of error:

- Failure rate is parameterized just by hardware, not time so we could have missing units
- Production rate could be zero for a unit
- We may not have hash rate data by region (Energy Regions) for the analysis period


- input carbon credit price
- Default start & end dates


Writeup:

Purpose/Methodology
---------------------------------
-- Our goal is to create a model that estimates the amount of carbon credits necessary to offset the carbon footprint of bitcoin holdings
-- To do this we took a bottom-up approach that examines the amount of ASIC hardware available to bitcoin miners
-- We considered the amount of functional units available to all miners by estimating monthly production rates of each manufacturer for each of their products along with how many may fail each month
-- We then estimated the amount of units actively mining bitcoin to be the most efficient functional units, those which produced the highest amount of hashes per unit of energy expended. Considering their efficiency, we included each unit until the cumulative amount of hashes by active units equated to the actual observed hash rate average for a given month.
-- Next, we gathered the estimated global distribution of hashes for each month across countries and regions. With this, we estimated the electrical energy consumed to generate those hashes based on the efficiency of units actively mining bitcoin.
-- Then, we gathered the mix of sources generating electricity for each country and region on an annual basis. With this, we applied each generation mix to our estimate of electrical energy directed from each country and region toward the Bitcoin network.
- Next, we gathered the amount of carbon emitted from each type of fossil fuel. With this and our estimation of fossil fuel energy consumed per region, we estimated the carbon footprint of the total Bitcoin network and the emissions in each region. 
- Then, we gathered the average supply of bitcoin on a given day in each month. Given the energy directed to the Bitcoin network serves as a wall of security that each holder of bitcoin benefits from, we estimated the carbon footprint of each unit of bitcoin (100mm sats) by evening distributing the load of emissions across the average current supply of bitcoin in each month.
- Lastly, we gathered the price per carbon credit which offsets each ton of CO2 emitted. With this, we estimated the amount of carbon credits necessary to offset the carbon footprint of bitcoin holdings.


Inputs
-----------
- Annual unit failure rate
- Hash rate per unit of energy expended
- Average daily hash rate for each month
- Geographical distribution of global Bitcoin hashrate per country per region
- Electricity generation mix per country per region
- Carbon emissions per MWh of each fossil fuel
- Average daily supply of bitcoin for each month
- Price of carbon credit per ton of CO2 emitted


Assumptions
--------------------
- The annual failure rate of ASIC products is the same
- The production rate of ASIC products is the same
- Miners will use the most efficient ASIC products if available to them
- The distribution of functional mining rigs are available to all miners across the globe
- The electricity generation mix for miners is equivalent to the electricity generation mix per region in a each country
- The energy directed to the Bitcoin network is of equal benefit to each unit of bitcoin, the asset


Outputs
-------------
- The functional amount of ASIC products in each month
- The active ASIC products actively mining bitcoin in each month
- The amount of energy expended by the network for each month
- The global distribution of hashrate and energy in each country and region for each month
- The electrical energy generation mix in each country and region for each month
- The amount of CO2 emitted by the Bitcoin network in each country and region for each month
- The amount of carbon credits required to offset the carbon footprint per bitcoin


Results
-------------
Access from Workstation/be aware that firewall may be an issue
http://util-docker-01.coinshares.cloud:7687/


Future Development/Questions
---------------------------------------------
- Best way to update
- How to extrapolate Seasonal hashrate changes
- What energy is consumed by mining pools, full nodes, and cooling
- Fine tuning production/failure rates, regional energy mixes
- Interactive dashboard so community and customise their assumptions and apply different inputs
- Oxford data only matches each country for 2019?




units in use
---------------------------------------------

- Gh/J - Gigahash per joule per unit of the type
- MWh - Estimated monthly MWh consumed by that unit type
- Total Failed Units - Estimated cumulative failed units of the type
- Total Functional Units - Estimated cumulative units which remain functional of the type
- Excess Units - Units estimated to be functional but not turned on in that month of that type
- Total Possible Hash Rate - Estimated total possible hash rate of functional units of the type
- Units in use - Units of the type estimated to be plugged in and operational




emissions
---------------------------------------------
- % - Percentage of hash rate estimated to come from that region
- Pct - Estimated percentage of electrical power to come from that source
- Network Pct - % of network hash coming from that region and that source i.e. %*Pct
- MWh - Total estimated power consumption of the network in that month
- Network Energy Consumption - Percentage of the total network power consumption estimated to come from that region and source
- Tons of CO2 - Estimated tons of CO2 coming from that region, from that source
- Pounds CO2 per MWh - Carbon intensity measure of that region, source