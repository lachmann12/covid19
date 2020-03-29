#############################
#
#   Author: Alexander Lachmann
#   Contact: alexander.lachmann [] gmail com 
#   Title: Correcting under-reported COVID-19 case numbers: estimating the true scale of the pandemic
#
#############################


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import io
import requests
import math

import plotly as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
from plotly import tools
import plotly.figure_factory as ff

from datetime import timedelta, date, datetime

import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
from sklearn.svm import SVR

plt.style.use('seaborn-whitegrid')

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.

confirmed_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
deaths_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
#recovered_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

url = confirmed_url
s = requests.get(url).content
cases = pd.read_csv(io.StringIO(s.decode('utf-8')))

url = deaths_url
s = requests.get(url).content
deaths = pd.read_csv(io.StringIO(s.decode('utf-8')))

#url = recovered_url
#s = requests.get(url).content
#recovered = pd.read_csv(io.StringIO(s.decode('utf-8'))).iloc[:,0:65]

cases['Country/Region'] = cases['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran')
cases['Country/Region'] = cases['Country/Region'].replace('Taiwan*', 'Taiwan')
cases['Country/Region'] = cases['Country/Region'].replace('Criuse Ship', 'Diamond Princess')
cases['Country/Region'] = cases['Country/Region'].replace('Korea, South', 'South Korea')

deaths['Country/Region'] = deaths['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran')
deaths['Country/Region'] = deaths['Country/Region'].replace('Taiwan*', 'Taiwan')
deaths['Country/Region'] = deaths['Country/Region'].replace('Criuse Ship', 'Diamond Princess')
deaths['Country/Region'] = deaths['Country/Region'].replace('Korea, South', 'South Korea')

#recovered['Country/Region'] = recovered['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran')
#recovered['Country/Region'] = recovered['Country/Region'].replace('Taiwan*', 'Taiwan')
#recovered['Country/Region'] = recovered['Country/Region'].replace('Criuse Ship', 'Diamond Princess')
#recovered['Country/Region'] = recovered['Country/Region'].replace('Korea, South', 'South Korea')

countries = cases.iloc[:,1].unique()
countries.sort()

demo = pd.read_csv("/kaggle/input/world-population-demographics-by-age-2019/world_demographics.csv")

demo["Country or Area"] = demo["Country or Area"].replace("Viet Nam", "Vietnam")
demo["Country or Area"] = demo["Country or Area"].replace("United States of America", "US")
demo["Country or Area"] = demo["Country or Area"].replace("United Kingdom of Great Britain and Northern Ireland", "United Kingdom")
demo["Country or Area"] = demo["Country or Area"].replace("Republic of Korea", "South Korea")
demo["Country or Area"] = demo["Country or Area"].replace("Venezuela (Bolivarian Republic of)", "Venezuela")
demo["Country or Area"] = demo["Country or Area"].replace('Iran (Islamic Republic of)', 'Iran')

duc = demo["Country or Area"].unique()
duc.sort()

deathrate_age = list(range(0,120))
deathrate_age[0:30] = [0]*30
deathrate_age[30:40] = [0.0012]*10
deathrate_age[40:50] = [0.0009]*10
deathrate_age[50:60] = [0.0039]*10
deathrate_age[60:70] = [0.0142]*10
deathrate_age[70:80] = [0.0474]*10
deathrate_age[80:120] = [0.083]*40


def calcVF(country1, country2):
    ma = np.where(demo["Country or Area"] == country1)[0]
    demo_c1 = demo.iloc[ma,:]
    ma = np.where(demo["Country or Area"] == country2)[0]
    demo_c2 = demo.iloc[ma,:]
    ll = list(range(0,120))
    ll = [str(i) for i in ll]
    ma = np.where(np.isin(demo_c1["Age"], np.array(ll)))[0]
    demo_c1 = demo_c1.iloc[ma,:]
    ma = np.where(np.isin(demo_c2["Age"], np.array(ll)))[0]
    demo_c2 = demo_c2.iloc[ma,:]
    vulnerable_c1 = [a * b for a, b in zip(demo_c1["Value"], deathrate_age)]
    vulnerable_c2 = [a * b for a, b in zip(demo_c2["Value"], deathrate_age)]
    v_c1 = sum(vulnerable_c1)/sum(demo_c1["Value"])
    v_c2 = sum(vulnerable_c2)/sum(demo_c2["Value"])
    exp_diff = v_c1/v_c2
    return(exp_diff)

def calculateGR(country1, d_shift):
    ma = np.where(cases["Country/Region"] == country1)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c1 = d_count_1 / c_count_1
    d_cases = np.where(d_count_1 > 10)[0]

    sds2 = d_count_1[d_cases]
    s1 = list(sds2)+[0]
    s2 = [0]+list(sds2)
    gr = np.array(s1)/np.array(s2)
    gr = pd.Series(np.array(gr[1:(len(gr)-1)]))

    new_deaths = np.array(s1)-np.array(s2)
    
    mean_gr = sum(list(gr))/len(list(gr))
    mean_double = math.log(2)/math.log(mean_gr)
    gr.index = d_count_1[d_cases][1:len(d_cases)].index
    doublings = np.log(2)/np.log(gr)

    tran = [(datetime.strptime(i, "%m/%d/%y") - timedelta(days=d_shift)).strftime("%-m/%-d/%y") for i in gr.index]
    gr.index = tran
    return(gr)

def plotGR(country1, gr, doublings):
    plt.figure(figsize=(10,6))
    fig, ax = plt.subplots(constrained_layout=True)
    ax.grid(False)

    plt.ylim(0.95, 1.8)
    res1, = plt.plot(gr, 'ro-', label="Growth Rate ("+country1+")")
    plt.ylabel("growth rate")

    ax.yaxis.label.set_color('red')
    ax.tick_params(axis='y', colors='red')

    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    plt.xticks(rotation=60)
    ax2 = ax.twinx()
    ax2.yaxis.label.set_color('blue')
    ax2.tick_params(axis='y', colors='blue')

    res2, = ax2.plot(doublings, 'b^-', label="Doubling Time (days)")
    plt.ylabel("doubling time (days)")
    plt.legend(handles=[res1, res2])
    plt.show()

    def predictCases(country1, country2, d_shift, p=False):
    ma = np.where(cases["Country/Region"] == country1)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c1 = d_count_1 / c_count_1
    d_cases = np.where(d_count_1 > 10)[0]
    sds2 = d_count_1[d_cases]
    
    ma = np.where(cases["Country/Region"] == country2)[0]
    c_count_2 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_2 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c2 = d_count_2 / c_count_2

    predicted_deaths = list(range(0,d_shift+1))
    predicted_deaths[0] = sds2[-1]

    for i in range(1,d_shift+1):
        #predicted_deaths[i] = predicted_deaths[i-1]*mean_gr
        #predicted_deaths[i] = predicted_deaths[i-1]*1.2
        predicted_deaths[i] = predicted_deaths[i-1]*gr[-1]

    combined_deaths = list(sds2) + list(predicted_deaths[1:len(predicted_deaths)])
    predicted_cases = np.array(combined_deaths) / (exp_diff*dr_c2[-1])
    #predicted_cases = np.array(combined_deaths) / (exp_diff*0.012)
    shift_cases = predicted_cases[-(len(d_cases)+1):-1]
    
    if p:
        plt.figure(figsize=(10,6))
        fig, ax = plt.subplots(constrained_layout=True)
        ax.grid(False)

        res1, = plt.plot(c_count_1[d_cases], 'bo-', label="Reported Cases ("+country1+")")
        res2, = plt.plot(shift_cases, 'ro-', label="Adjusted Cases ("+country1+")")
        plt.xticks(rotation=60)
        ax.axvline(x=len(d_cases)-6)

        plt.ylabel("cases")
        plt.xticks(rotation=90)
        plt.legend(handles=[res1, res2])
        plt.show()

    return(shift_cases)

def plotDR(country1, country2):
    ma = np.where(cases["Country/Region"] == country1)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c1 = d_count_1 / c_count_1

    ma = np.where(cases["Country/Region"] == country2)[0]
    c_count_2 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_2 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c2 = d_count_2 / c_count_2

    sig_cases = np.where(c_count_1 > 100)[0]
    ax1 = plt.subplot(1,1,1)
    res1, = plt.plot(range(0,len(sig_cases)), c_count_1[sig_cases], 'ro-', linewidth=3, label="reported cases")

    ax1.grid(False)
    plt.xticks(rotation=60)
    ax2 = ax1.twinx()
    res3, = ax2.plot(d_count_1[sig_cases], 'gs-', linewidth=3, label="deaths")

    for label in ax1.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    plt.title(country1)
    ax1.set_ylabel('cases', color="black")
    color = 'green'
    ax2.set_ylabel('deaths', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.legend(handles=[res1, res3])

    plt.figure(figsize=(10,6))
    plt.rc('ytick', labelsize=23) 
    plt.rc('xtick', labelsize=13)

    res1, = plt.plot(dr_c1[sig_cases]*100, 'b.-', label="Death rate ("+country1+")")
    res2, = plt.plot(dr_c2[sig_cases]*100, 'r.-', label="Death rate ("+country2+")")
    plt.xticks(rotation=60)
    plt.ylabel("death rate")

    plt.legend(handles=[res1, res2])
    plt.show()

def getMGR(country, shift):
    gr = calculateGR(country, shift)
    mgr = mean_gr = sum(list(gr))/len(list(gr))
    return(mgr)

def extrapolateDeaths(country, fitrate, intervention, timescale=50):
    
    ma = np.where(cases["Country/Region"] == country)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    dr_c1 = d_count_1 / c_count_1
    d_cases = np.where(d_count_1 > 10)[0]
    sds2 = d_count_1[d_cases]
    
    predicted_deaths = list(range(0,timescale))
    predicted_deaths[0] = sds2[-1]
    
    for i in range(1,timescale):
        if i < intervention:
            predicted_deaths[i] = predicted_deaths[i-1]*1.1
        else:
            predicted_deaths[i] = predicted_deaths[i-1]*fitrate[i-intervention]
    dd =sds2.index
    datelist = pd.date_range(pd.to_datetime(dd[len(dd)-1], format='%m/%d/%y', errors='ignore'), periods=timescale).tolist()
    str_date = [d.strftime('%m/%d/%y') for d in datelist]
    
    return(pd.DataFrame(data=predicted_deaths, index=str_date))