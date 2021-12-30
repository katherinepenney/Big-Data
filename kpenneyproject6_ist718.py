# -*- coding: utf-8 -*-
"""KPenneyProject6_ist718.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Fg5jZElaM3LmPPeF1NMNajvFRVLEnBf4

**Instructions**
## • The research question is can we predict which three zip codes provide the best investment opportunity for the Syracuse Real Estate Investment Trust (SREIT)?
#### • Using the base data available from Zillow (files.zillowstatic.com/research/public/Zip/Zip_Zhvi_SingleFamilyResidence.csv)
#### o Review the data – clean as appropriate
#### o Provide an initial data analysis to include (but not limited to):
#### o Review the data – clean as appropriate
### ▪ Develop time series plots for the following Arkansas metro areas:
#### o Review the data – clean as appropriate
#### • Hot Springs, Little Rock, Fayetteville, Searcy
#### o Review the data – clean as appropriate
### • Present all values from 1997 to present
#### o Review the data – clean as appropriate
### • Average at the metro area level
#### o Review the data – clean as appropriate
### • Using data from Zillow:
#### o Review the data – clean as appropriate
#### o Develop model(s) for forecasting average median housing value by zip code for 2018
#### o Review the data – clean as appropriate
#### o Use the historical data from 1997 through 2017 as your training data
#### o Review the data – clean as appropriate
#### o Integrate data from other sources (think Bureau of Labor Statistics and Census data) to improve upon your base model(s)
#### o Review the data – clean as appropriate
### • Answer the following questions:
#### o Review the data – clean as appropriate
#### o What technique/algorithm/decision process did you use to down sample? (BONUS FOR NOT DOWN SAMPLING)
#### o Review the data – clean as appropriate
#### o What three zip codes provide the best investment opportunity for the SREIT?
#### o Review the data – clean as appropriate
#### o Why?
"""

import pandas as pd
import numpy as np 
from scipy.stats import uniform 
from scipy.stats import gaussian_kde as kde
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt 
import seaborn as sns
import io 
from sklearn.linear_model import LinearRegression
from google.colab import files 
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.offline as po
from datetime import datetime
from fbprophet import Prophet

# Single family residences by zipcode and county in Arkansas  
uploaded = files.upload()
data1 = pd.read_csv(io.BytesIO(uploaded['SingleFamilyResidence.csv']),na_values="--")

uploaded = files.upload()
data2 = pd.read_csv(io.BytesIO(uploaded['usprice_cust1.csv']),na_values="--")

uploaded = files.upload()
data3 = pd.read_csv(io.BytesIO(uploaded['growingcounty.csv']),na_values="--")

uploaded = files.upload()
data4 = pd.read_csv(io.BytesIO(uploaded['annual.csv']),na_values="--")

uploaded = files.upload()
data5 = pd.read_csv(io.BytesIO(uploaded['HPI1.csv']),na_values="--")

# Transforming columns  
idvars = ['RegionID','SizeRank','RegionName','RegionType','StateName',
          'State','City','Metro','CountyName']
thedata = data1.drop(columns=idvars)
columns = list(thedata.columns)
columns = columns
newdata = data1.melt(id_vars=idvars, value_vars = columns, var_name='ds',value_name='y')

#Defining function to find missing data 
def get_na(df):
  out = []
  list_zip = df.RegionName.unique()

  for i in list_zip:
      zip_df = df.loc[df['RegionName']== i]
      zip_df = zip_df[['RegionName','y']]
      count_na = zip_df.isna().sum()
      if count_na['y'] > 0:
          out.append(i)
  return out

# Remove zip codes with missing data 
na = get_na(newdata)
newdata = newdata[~newdata['RegionName'].isin(na)]

# Making column a date 
newdata['ds'] = pd.to_datetime(newdata['ds'])
newdata['year'] = newdata['ds'].dt.year
# Drop 1996 and 2020
newdata.drop(newdata[newdata['year']== 1996].index, inplace =True)  
newdata.drop(newdata[newdata['year']== 2020].index, inplace =True)

# Make only Arkansas 
AR = newdata.groupby(['Metro','year'])['y'].median()
AR = pd.DataFrame(AR)
AR.reset_index(inplace= True)
# Fayettenam
fay = AR[AR['Metro'] == 'Fayetteville-Springdale-Rogers']
# Little Rock 
LR = AR[AR['Metro'] == 'Little Rock-North Little Rock-Conway']
# Searcy 
Sear = AR[AR['Metro'] == 'Searcy']
# Hot Springs 
HS = AR[AR['Metro'] == 'Hot Springs']

newdata.head(5)

# Plot Metros
plt.plot(fay['year'], fay['y'])
plt.plot(LR['year'], LR['y'])
plt.plot(Sear['year'], Sear['y'])
plt.plot(HS['year'], HS['y'])
plt.legend(["Fayetteville", "Little Rock", "Searcy", "Hot Springs"], loc ="lower right")

newdata.head(5)

# Use dataset 2 and remove unneeded columns
data2 = data2.drop(['median','theaverage','theaverage','average '], axis=1)

data2.head(5)

# Forecasting Arkansas Median House Price
# Prepair columns names 
data2_2 = data2.copy()
data2_2 = data2_2[['Year','themedian']]
data2_2.columns = ['ds','y']


#define model 
model = Prophet()
# fit model 
model.fit(data2_2)

# use model for forecast 
forecast = model.predict(data2_2)
forecast = pd.Series(forecast['yhat'].values,index = [data2['Year']])
forecast = forecast.rename("Prophet")

# Plot predictions 
fig, ax = plt.subplots(figsize = (15,5))
chart = sns.lineplot(x='Year', y = 'themedian', data = data2)
chart.set_title('Arkansas Median')
forecast.plot(ax=ax, color = 'red', marker="o", legend = True, rot=90)

# Population differences from biggest Arkansas from 2010 to 2019
labels = ['Benton', 'Craighead', 'Pulaski', 'Garland', 'Washington','White']
bar1 = [93.365, 40.610,175.735,50.550,87.944,32.537]
bar2 = [112.183, 46.934,186.437,51.015,96.310,35.035]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, bar1, width, label='2010')
rects2 = ax.bar(x + width/2, bar2, width, label='2019')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Population x100 ')
ax.set_title('Population Changes in Big Counties')
ax.set_xticks(x, labels)
ax.legend()

fig.tight_layout()

plt.show()

# Graph the HPI (House Price Index) of Arkansas from 1975 - 2020

x = data5['Year']
y = data5['HPI']

plt.plot(x,y)
plt.title("HPI of Arkansas 1975-2020")
plt.xlabel("Year")
plt.ylabel("HPI")

# Compare the HPI of Arkansas, and how it relates to the HPI based on the 1990 and 2000 statistics
thex = data5['Year']
they = data5['HPI']
they2 = data5['HPI with 1990 base']
they3 = data5['HPI with 2000 base']

plt.plot(thex,they)
plt.plot(thex,they2)
plt.plot(thex,they3)
plt.title('HPI and 1990/2000 base')
plt.xlabel('Year')
plt.ylabel('HPI')
plt.legend(["HPI", "HPI with 1990 base", "HPI with 2000 base"], loc ="lower right")
plt.show()

# Box plot comparing the HPI of Arkansas, the HPI with a 1990 base, and a HPI with a 2000 base
sns.set(style='whitegrid')
fig, ax1 = plt.subplots(figsize=(10, 6))
d1 = data5['HPI'].plot(kind='box')

sns.set(style='whitegrid')
fig, ax1 = plt.subplots(figsize=(10, 6))
d2 = data5['HPI with 1990 base'].plot(kind='box')

sns.set(style='whitegrid')
fig, ax1 = plt.subplots(figsize=(10, 6))
d3 = data5['HPI with 2000 base'].plot(kind='box')

