# Import the dependencies.

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_, text, inspect, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine= create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
measurement=Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################

app= Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes. For the last two routes please enter the dates or date range (start to end) you want to query. The format is cited in the route as AAAA-MM-DD. """
    return (
        f"Available Routes <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/AAAA-MM-DD <br/>"
        f"/api/v1.0/AAAA-MM-DD/AAAA-MM-DD <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    
    dates = session.query(measurement.date).\
    filter(and_(measurement.date >= '2016-08-23', measurement.date <= '2017-08-23')).\
    order_by(measurement.date).all()

    prcps = session.query(measurement.prcp).\
    filter(and_(measurement.date >= '2016-08-23', measurement.date <= '2017-08-23')).\
    order_by(measurement.date).all()

    all_dates= list(np.ravel(dates))
    all_prcps= list(np.ravel(prcps))
    
    precipitation_dict = dict(zip(all_dates, all_prcps))
    return jsonify(precipitation_dict)
    
session.close()

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    stations_query=session.query(station.station).all()
    all_station= list(np.ravel(stations_query))
    return (all_station)
session.close()


@app.route("/api/v1.0/tobs")
def temps():
    temperatures = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(and_(measurement.station=="USC00519281",measurement.date >= '2016-08-23', measurement.date <= '2017-08-23')).\
        order_by(measurement.tobs).all()
    all_stations = [station[0] for station in temperatures]  
    all_dates = [date[1] for date in temperatures] 
    all_tobs = [tob[2] for tob in temperatures] 

    temp_dict = {date: (station, tob) for date, station, tob in zip(all_dates, all_stations, all_tobs)}
    return jsonify(temp_dict)

session.close()

@app.route("/api/v1.0/<start>")
def start(start):
    av_temp = session.query(
    measurement.date,
    func.min(measurement.tobs).label('min_temp'),
    func.max(measurement.tobs).label('max_temp'),
    func.avg(measurement.tobs).label('avg_temp')).filter(measurement.date >= start).group_by(measurement.date).all()

    all_dates = [date[0] for date in av_temp]  
    all_mins = [minTemp[1] for minTemp in av_temp] 
    all_max = [maxTemp[2] for maxTemp in av_temp] 
    all_avTemp = [avTemp[3] for avTemp in av_temp] 

    # Create a dictionary to hold the results
    temp_dict = {date: (minTemp, maxTemp, avTemp) for date, minTemp, maxTemp, avTemp in zip(all_dates, all_mins, all_max, all_avTemp)}
    
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def startEnd(start,end):
    av_temp2 = session.query(
    measurement.date,
    func.min(measurement.tobs).label('min_temp'),
    func.max(measurement.tobs).label('max_temp'),
    func.avg(measurement.tobs).label('avg_temp')).filter(measurement.date >= start, measurement.date<=end).group_by(measurement.date).all()

    all_dates = [date[0] for date in av_temp2]  
    all_mins = [minTemp[1] for minTemp in av_temp2] 
    all_max = [maxTemp[2] for maxTemp in av_temp2] 
    all_avTemp = [avTemp[3] for avTemp in av_temp2] 

    # Create a dictionary to hold the results
    temp_dict = {date: (minTemp, maxTemp, avTemp) for date, minTemp, maxTemp, avTemp in zip(all_dates, all_mins, all_max, all_avTemp)}
    
    return jsonify(temp_dict)
session.close()

#Define main behaviou
if __name__=="__main__":
    app.run(debug=True)
