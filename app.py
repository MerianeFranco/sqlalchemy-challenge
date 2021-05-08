import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Welcome to Hawaii Temperature Measurement Station API"""
    return (
        f"Welcome to Hawaii Temperature Measurement Station API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all date and precipitation
    results = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date).all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    precipitation_info = []
    for date, pcrp in results:
        precipitation_dict = {date:pcrp}
        precipitation_info.append(precipitation_dict)

    return jsonify(precipitation_info)


@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    stations = session.query(station.station, station.name).all()
    

    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Find the most active station in the last year of measurements 
    
    mostactive = session.query(measurement.station).\
        filter(measurement.date >= query_date).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()

    mostactive_dt = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.date >= query_date).\
        filter(measurement.station == mostactive[0]).\
        order_by(measurement.date).all()
    session.close()

    return jsonify(mostactive_dt)

@app.route("/api/v1.0/<start>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start).all()
 
    return jsonify(temp)

@app.route("/api/v1.0/<start>/<end>")
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start).\
    filter(measurement.date <= end).all()
 
    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)
