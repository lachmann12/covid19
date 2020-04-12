import os

from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os.path
import time
from shutil import copyfile
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import io
import requests
import math
from datetime import timedelta, date, datetime
import statistics
from scipy import optimize
import logging
logging.basicConfig(level=logging.DEBUG)

def initData():
    confirmed_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    deaths_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    url = confirmed_url
    s = requests.get(url).content
    cases = pd.read_csv(io.StringIO(s.decode('utf-8')))
    url = deaths_url
    s = requests.get(url).content
    deaths = pd.read_csv(io.StringIO(s.decode('utf-8')))

    cases['Country/Region'] = cases['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran')
    cases['Country/Region'] = cases['Country/Region'].replace('Taiwan*', 'Taiwan')
    cases['Country/Region'] = cases['Country/Region'].replace('Criuse Ship', 'Diamond Princess')
    cases['Country/Region'] = cases['Country/Region'].replace('Korea, South', 'South Korea')

    deaths['Country/Region'] = deaths['Country/Region'].replace('Iran (Islamic Republic of)', 'Iran')
    deaths['Country/Region'] = deaths['Country/Region'].replace('Taiwan*', 'Taiwan')
    deaths['Country/Region'] = deaths['Country/Region'].replace('Criuse Ship', 'Diamond Princess')
    deaths['Country/Region'] = deaths['Country/Region'].replace('Korea, South', 'South Korea')

    demo = pd.read_csv("data/world_demographics.csv")
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

    return(cases, deaths, demo, deathrate_age)

def calcVF(country1, country2, demo, deathrate_age):
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

def calculateGR(country, deaths):
    ma = np.where(deaths["Country/Region"] == country)[0]
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    d_cases = np.where(d_count_1 > 10)[0]
    sds2 = d_count_1[d_cases]
    
    s1 = list(sds2)+[0]
    s2 = [0]+list(sds2)
    gr = (1.0*np.array(s1))/np.array(s2)
    
    gr = pd.Series(np.array(gr[1:(len(gr)-1)]))
    gr.index = d_count_1[d_cases][1:len(d_cases)].index
    tran = [(datetime.strptime(i, "%m/%d/%y") - timedelta(days=23)).strftime("%-m/%-d/%y") for i in gr.index]
    gr.index = tran
    return(gr)

def findDecayShift(growthrates, decay_spline):
    decay_shift = 0
    ff = statistics.median(growthrates[-5:])
    
    if ff < 1.01:
        decay_shift = 100
        return(decay_shift)

    while float(ff) < float(list(decay_spline)[decay_shift]):
        decay_shift = decay_shift + 1
        if decay_shift-1 > len(decay_spline):
            break
    return(decay_shift)

def getSpline(deaths):
    country1 = "Italy"
    country2 = "China"
    country3 = "Spain"

    gr1 = list(calculateGR(country1, deaths))
    gr2 = list(calculateGR(country2, deaths))
    gr3 = list(calculateGR(country3, deaths))

    g1 = gr1[19:len(gr1)]
    g2 = gr2[10:len(gr2)]
    g3 = gr3[14:len(gr3)]

    def func(x, a, b):
        return a * np.exp(-b * x)+1

    x = list(range(0,len(g1)))+list(range(0, len(g2)))+list(range(0, len(g3)))
    y = list(g1+g2+g3)

    popt, params_covariance = optimize.curve_fit(func, x[3:len(x)], y[3:len(y)], p0=[2, 2])

    xrange = 400
    fit_rate = func(np.array(list(range(0, xrange))), *popt)
    return(fit_rate)

def extrapolateDeaths(country, deaths, fitrate, intervention, timescale=60, shift=0, pastDays=23, exprate=1.25):
    
    ma = np.where(deaths["Country/Region"] == country)[0]
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
    d_cases = np.where(d_count_1 > 10)[0]
    sds2 = d_count_1[d_cases]
    
    gr = calculateGR(country, deaths)
    gr = gr[0:(len(gr)-shift)]
    predicted_deaths = list(range(0,timescale))
    predicted_deaths[0] = sds2[-(1+shift)]
    
    j = 0
    for i in range(1,timescale):
        if i < 23-pastDays:
            predicted_deaths[i] = predicted_deaths[i-1]*exprate
        else:
            predicted_deaths[i] = predicted_deaths[i-1]*fitrate[j-intervention]
            j = j+1
    
    dd =sds2.index
    datelist = pd.date_range(pd.to_datetime(dd[len(dd)-1], format='%m/%d/%y', errors='ignore'), periods=timescale).tolist()
    str_date = [d.strftime('%m/%d/%y') for d in datelist]
    
    return(pd.DataFrame(data=predicted_deaths, index=str_date))

def estimateParameter(country, deaths, fitrate):
    limi = 50
    
    ggr = calculateGR(country, deaths)
    if limi > len(ggr):
        limi = len(ggr)-4
    
    mink = 0
    minsd = 100000000

    for k in range(15, 70):
        expl = list()
        for i in range(0,limi):
            decay_position = -findDecayShift(ggr[0:(len(ggr)-i)], fitrate)    
            exp_d = extrapolateDeaths(country, deaths, fitrate, decay_position, timescale=80+i, shift=i, pastDays=k-i)
            expl.append(exp_d.iloc[-1,0])
        
        if statistics.stdev(expl) < minsd:
            minsd = statistics.stdev(expl)
            mink = k

    minr = 1.2
    minsd = 1000000000
    for k in [1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.2, 1.21, 1.22, 1.23, 1.24, 1.25, 1.26, 1.27, 1.28, 1.29, 1.3, 1.31, 1.32, 1.33]:
        expl = list()
        for i in range(1,limi):
            decay_position = -findDecayShift(ggr[0:(len(ggr)-i)], fitrate)    
            exp_d = extrapolateDeaths(country, deaths, fitrate, decay_position, timescale=80+i, shift=i, pastDays=mink-i, exprate=k)
            expl.append(exp_d.iloc[-1,0])
        
        if statistics.stdev(expl) < minsd:
            minsd = statistics.stdev(expl)
            minr = k        
    return (mink, minr)

def precomputeParameters(deaths, fitrate):
    countries = list(set(deaths["Country/Region"]))
    pass_countries = list()
    country_shift = {}
    country_growthrate = {}
    for country in countries:
        ma = np.where(deaths["Country/Region"] == country)[0]
        d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)
        d_cases = np.where(d_count_1 > 10)[0]
        if len(d_cases) > 10:
            ds, gr = estimateParameter(country, deaths, fitrate)
            country_shift[country] = ds
            country_growthrate[country] = gr
            pass_countries.append(country)
    return(pass_countries, country_shift, country_growthrate)

def getPredictionSeries(country, deaths, fitrate, limi=18, shift=0, exprate=1.25):
    ggr = calculateGR(country, deaths)
    if limi > len(ggr):
        limi = len(ggr)-4
    expl = {}
    for i in range(0,limi):
        decay_position = -findDecayShift(ggr[0:(len(ggr)-i)], fitrate)    
        exp_d = extrapolateDeaths(country, deaths, fitrate, decay_position, timescale=80+i, shift=i, pastDays=shift-i, exprate=exprate)
        ll = list(exp_d.iloc[:,0])
        ll = [int(num) for num in ll]
        ind = list(exp_d.index)
        dp = {}
        dp["date"] = ind
        dp["predicted_deaths"] = ll
        expl[i] = dp
    return(expl)

def getStats(country, deaths, cases, pdeaths, vf):

    country2 = "South Korea"

    info = {}
    ma = np.where(deaths["Country/Region"] == country)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)

    info["current_cases"] = int(c_count_1[-1])
    info["current_deaths"] = int(d_count_1[-1])
    info["current_cfr"] = float(d_count_1[-1])/float(c_count_1[-1])

    ma = np.where(cases["Country/Region"] == country2)[0]
    c_count_1 = cases.iloc[ma, 4:].sum(axis=0)
    d_count_1 = deaths.iloc[ma, 4:].sum(axis=0)

    c1 = list(c_count_1)[-1]
    c2 = list(d_count_1)[-1]

    drr = float(c2)/float(c1)

    mean_days_death = 18
    asym_days = 5

    d_shift = mean_days_death + asym_days
    gr = calculateGR(country, deaths)

    info["predicted_total_deaths"] = int(pdeaths[-1])

    num = pdeaths[d_shift]/(vf*drr)
    info["predicted_current_infections"] = int(num)
    
    num = pdeaths[-1]/(vf*drr)
    info["predicted_total_infections"] = int(num)

    doublings = np.log(2)/np.log(gr)
    info["current_doubling_time"] = round(doublings[-1], 5)

    return(info)