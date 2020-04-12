import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os.path
import time
from shutil import copyfile
from flask_cors import CORS, cross_origin
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import io
import requests
import math
from datetime import timedelta, date, datetime
from waitress import serve
from utils import *
import json

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/": {"origins": "*"}})
app.config['SECRET_KEY'] = 'XOXO'    


cases, deaths, demo, deathrate_age = initData()
fit_rate = getSpline(deaths)
#dshift, prerate = estimateParameter("Italy", deaths, fit_rate)
countries, country_d, country_g = precomputeParameters(deaths, fit_rate)
print(country_d)


@app.route('/listcountries', methods=['GET', 'POST'])
def print_countries():
	return(json.dumps(countries))

@app.route('/country', methods=['GET', 'POST'])
def print_country_stats():
	country = request.args.get('name')
	info = {}
	info["country"] = country
	info["supression_days"] = country_d[country]
	info["exponential_growthrate"] = country_g[country]
	info["deaths_projection"] = getPredictionSeries(country, deaths, fit_rate, shift=country_d[country], exprate=country_g[country])
	info["stats"] = getStats(country, deaths, cases, info["deaths_projection"][0]["predicted_deaths"], calcVF(country, "South Korea", demo, deathrate_age))
	return(json.dumps(info))

@app.route('/help')
def print_help():
	return("Cases: "+str(len(cases))
	+"<br>VF: "+str(calcVF("Italy", "South Korea", demo, deathrate_age))
	+"<br>GR: "+str(calculateGR("US", deaths))
	)

@app.route('/')
@cross_origin(origin='*', headers=['Content- Type'])
def upload_form():
	return render_template('index.html')

@app.route('/', methods=['GET'])
@cross_origin(origin='*',headers=['Content- Type'])
def upload_file():
	if request.method == 'GET':
		return()

if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0')
	serve(app, host='0.0.0.0', port=5000)