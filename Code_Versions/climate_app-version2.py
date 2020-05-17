########## File Information and Author ########### 
# SQLAlchemy Homework - Surfs Up
# DATE DUE: May 16, 2020
# AUTHOR Rob Gauer
# FILE NAME 'climate_app.py
# Code files saved to folder: 'sqlalchemy-challenge' GitHub Repository
# 
# Route(s) output screen copy images saved to folder: Output_Images
#
########## Import Setup and Dependancies ########### 
import numpy as np 
import datetime as dt
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#
########## Database Setup ########### 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database and tables
Base = automap_base()

# Reflect the tables 
Base.prepare(engine, reflect=True)

# Save reference to the tables 
Measurement = Base.classes.measurement 
Station = Base.classes.station

########## Flask Setup ###########
# Create an app
app = Flask(__name__)

########## Flask Routes ###########
## Route - HOME PAGE
@app.route("/") 
def welcome():    
    """List all available api routes."""
    return (        
        f"Welcome to Hawaii Climate Home Page<br/> "
        f"Available Routes:<br/>"
        f"<br/>"
        f"List precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List precipitation stations names and location information:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"List of temperature observations a year from the last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"<br/>"
        f"DIRECTIONS (for last two Routes)<br/>"
        f"At browser address line, overtype <start> or <start>/<end> with date.<br/>"
        f"Use the following date format:  'yyyy-mm-dd' or 'yyyy-mm-dd'/'yyyy-mm-dd'.<br/>"
        f"<br/>"
        f"Diplay Minimum, Maximum, and Average temperatures from a given start date:<br/>"
        f"/api/v1.0/min_max_avg/&lt;start&gt;<br/>"
        f"<br/>"
        f"Diplay Minimum, Maximum, and Average temperatures from a given start and end date:<br/>"
        f"/api/v1.0/min_max_avg/&lt;start&gt;/&lt;end&gt;<br/>"
        f"<br/>"
        f"<br/>"
    )

## Route - PRECIPITATION
@app.route("/api/v1.0/precipitation") 
def precipitation():    
# Create our session (link) from Python to the Database    
    session = Session(engine)
    # Query for the dates and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    # Convert to list of dictionaries to jsonify    
    prcp_date_list = []
    
    for date, prcp in results:        
        new_dict = {}        
        new_dict[date] = prcp        
        prcp_date_list.append(new_dict)
    session.close()
    
    # jsonify the result
    return jsonify(prcp_date_list)

## Route - STATIONS LIST
@app.route("/api/v1.0/stations") 
def stations():    
# Create our session (link) from Python to the Database    
    session = Session(engine)
    stations = {}
    
    # Query all stations    
    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name
    session.close()
    
    # jsonify the result
    return jsonify(stations)

## Route - TEMPERATURE OBSERVATION DATA (TOBS) MOST ACTIVE STATION for LAST YEAR
@app.route("/api/v1.0/tobs") 
def tobs():    
    # Create our session (link) from Python to the Database    
    session = Session(engine)
    # Get the last date contained in the dataset and date from one year ago    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
        - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the dates and temperature values    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year_date).\
            order_by(Measurement.date).all()
    
    # Convert to list of dictionaries to jsonify
    tobs_date_list = []
    
    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)
    session.close()
    
    # jsonify the result
    return jsonify(tobs_date_list)

## Route - TEMPERATURE by START DATE
## List of the minimum temperature, the average temperature, 
## and the max temperature for a given start date. or start-end range.
@app.route("/api/v1.0/min_max_avg/<start>") 
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    Args:        
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Create our session (link) from Python to the Database    
    session = Session(engine)
    
    results = session.query(Measurement.date,\
        func.min(Measurement.tobs), \
            func.avg(Measurement.tobs), \
                func.max(Measurement.tobs)).\
            filter(Measurement.date>=start).\
            group_by(Measurement.date).all()
    
    # Create a list to hold results
    start_list = []
    for start_date, min, avg, max in results:
        dict_a = {}
        dict_a["Date"] = start_date
        dict_a["TMIN"] = min
        dict_a["TAVG"] = avg
        dict_a["TMAX"] = max
        start_list.append(dict_a)
    
    session.close()    
    
    # jsonify the result
    return jsonify(start_list)

## Route - TEMPERATURE by START and END DATE
## List of the minimum temperature, the average temperature, 
## and the max temperature for a given start and end date range. 
@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    # take start and end dates and convert to yyyy-mm-dd format for the query
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date)

    session.close()

    # Create a list to hold results
    tempature_list = []
    for result in results:
        range = {}
        range["StartDate"] = start_date
        range["EndDate"] = end_date
        range["TMIN"] = result[0]
        range["TAVG"] = result[1]
        range["TMAX"] = result[2]
        tempature_list.append(range)

    # jsonify the result
    return jsonify(tempature_list)

#run the app
if __name__ == "__main__":
    app.run(debug=True)

## EOF ##