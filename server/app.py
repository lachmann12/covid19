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

import warnings
from waitress import serve

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/": {"origins": "*"}})

app.config['SECRET_KEY'] = 'XOXO'    

print("server initialized")

@app.route('/help')
def print_help():
	return("Hello World!")

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
	serve(app, host='0.0.0.0', port=8000)