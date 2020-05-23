# 1. import Flask

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)


# reflect an existing database into a new model

# reflect the tables
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API<br/>"
        f"Avaiable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end>\n"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""

    prev_year = dt.date(2017,8,23)-dt.timedelta(days = 365)
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year).all()
    precip = {date:prcp for date,prcp in precipitation}

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""

    result = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()
    
    stations = list(np.ravel(result))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the tobs data as json"""
    prev_year = dt.date(2017,8,23)-dt.timedelta(days = 365)
    datetemp = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= prev_year).filter(measurement.station=='USC00519281').all()

    return jsonify(datetemp)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def starts(start=None, end=None):
    """Return the start and end data as json"""
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ =="__main__":
    app.run()