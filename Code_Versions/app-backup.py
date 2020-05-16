import numpy as np 
import datetime as dt
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session from sqlalchemy import create_engine, func, and_
from flask import Flask, jsonify

########## Database Setup ########### 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model 
Base = automap_base()

# Reflect the tables 
Base.prepare(engine, reflect=True)

# Save reference to the table 
Measurement = Base.classes.measurement 
Station = Base.classes.station

########## Flask Setup ########## 
app = Flask(__name__)

########## Flask Routes ########## 
@app.route("/") 
def welcome():    
    """List all available api routes."""
    return (        
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
@app.route("/api/v1.0/precipitation") 
def precipitation():    
# Create our session (link) from Python to the DB    
    session = Session(engine)
    # Query for the dates and precipitation values
    results =   session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    # Convert to list of dictionaries to jsonify    
    prcp_date_list = []
    
    for date, prcp in results:        
        new_dict = {}        
        new_dict[date] = prcp        
        prcp_date_list.append(new_dict)
    
    session.close()

    return jsonify(prcp_date_list)

@app.route("/api/v1.0/stations") 
def stations():    
# Create our session (link) from Python to the DB    
    session = Session(engine)
    stations = {}
    
    # Query all stations    
    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name
    
    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs") 
def tobs():    
    # Create our session (link) from Python to the DB    
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
    
    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>") 
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:        
        start (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    # Create our session (link) from Python to the DB    
    session = Session(engine)
    
    return_list = []
    
    results =   session.query(  Measurement.date,\
            func.min(Measurement.tobs), \
            func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    
    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)
    
    session.close()    
    
    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>") 
def temp_range_start_end(start,end):    
    """TMIN, TAVG, and TMAX per date for a date range.
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    # Create our session (link) from Python to the DB    session = Session(engine)
    return_list = []
    results =   session.query(  Measurement.date,\
            func.min(Measurement.tobs), \
            func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).\
        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
        group_by(Measurement.date).all()
    
    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)
    session.close()    
    
    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)

    