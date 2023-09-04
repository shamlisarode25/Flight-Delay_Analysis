import os
import numpy as np
import flask
import joblib
import pickle
from flask import Flask, render_template, request
import pandas as pd

#creating instance of the class
app=Flask(__name__)
loaded_model = joblib.load("model.joblib")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

airlines = pd.read_csv('airlines.csv')
airlines = airlines.iloc[0].to_dict()

airports = pd.read_csv('airports.csv')
airports = airports.iloc[0].to_dict()

#to tell flask what url should trigger the function index()
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', airlines_mapping=airlines)

#prediction function
def DelayPredict(to_predict_list):
           # Convert the list into a NumPy array with the right shape
           input_features = np.array(to_predict_list).reshape(1, 8)
            
           # Call the prediction function with the input features
           prediction = loaded_model.predict(input_features)[0]
           
           if prediction==0:
                 status="Flight will be Ontime"
           else:
                 status="Flight will be Delayed"
             # Display the prediction result
           return status
 
    
# Define a custom Jinja filter for reverse dictionary lookup
def reverse_lookup(value, dictionary):
    for key, val in dictionary.items():
        if val == value:
            return key
    return value

# Register the custom filter
app.jinja_env.filters['reverse_lookup'] = reverse_lookup

@app.route('/result',methods = ['POST'])
def result():
    if request.method == 'POST':
       try:
           feature_order = ['DayofMonth', 'Reporting_Airline', 'Flight_Number_Reporting_Airline', 'Origin', 'Dest', 'CRSElapsedTime', 'AirTime', 'Distance']
           
           to_predict_list = request.form.to_dict()
           to_predict_list=list(to_predict_list.values())
           to_predict_list = list(map(int, to_predict_list))
           result = DelayPredict(to_predict_list)
           
           return render_template('result.html', prediction=result, input_values=to_predict_list, airlines=airlines, airports=airports)
       
       except Exception:
           err = "Input Error!!! Enter all the details"
           return render_template('index.html', prediction=err)
       
       
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')