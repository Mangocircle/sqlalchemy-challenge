# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base=automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
Measurement = base.classes.Measurement
Station = base.classes.Measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
session = Session(engine)
 
date_list = session.query(Measurement.date)
recent_date = [x[0] for x in date_list]
recent_date = max(recent_date)
    
recent_date_clean = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()
date_one_year = recent_date_clean - dt.timedelta(days=365)

station_list = session.query(Measurement.station)

station_names = []
    
for name in station_list:
    station_names.append(name)

station_names = set(station_names)
station_names = [x[0] for x in station_names]

station_counts = []

for station in station_names:
    number_rows = session.query(Measurement.station).filter(Measurement.station == station).count()
    station_counts.append(number_rows)
    
active_stations_df = pd.DataFrame({"station": station_names,
                                   "number of rows": station_counts})
    
active_stations_df = active_stations_df.sort_values("number of rows",ascending=False)
active_stations_df = active_stations_df.reset_index(drop=True)

session.close()

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        "Welcome, to HaweatherApp <br/>"
        "/Resources/hawaii.sqlite <br/>"
        "/api/v1.0/stations <br/>"
        "/api/v1.0/tobs <br/>"
        "/api/v1.0/start-date (yyyy-mm-dd) <br/>"
        "/api/v1.0/start-date (yyyy-mm-dd)/end-date (yyyy-mm-dd)")

@app.route("/Resources/hawaii.sqlite")
def hawaii():
    session = Session(engine)
    yearprecip = session.query(Measurement).filter(Measurement.date >= date_one_year).filter(Measurement.date <= recent_date_clean)
    precipdict = [{"date": x.date,
                  "prcp": x.prcp} for x in yearprecip]
    return jsonify(precipdict)
    session.close()


@app.route("/api/v1.0/stations")
def stations():
    return jsonify(station_names)
    

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_12_months_tobs = session.query(Measurement).filter(Measurement.station == active_stations_df["station"][0]).filter(Measurement.date >= date_one_year).filter(Measurement.date <= recent_date_clean)
    last_12_months = [{"date": x.date,
                  "tobs": x.tobs} for x in last_12_months_tobs]
    return jsonify(last_12_months)
    session.close()

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    temp = session.query(Measurement.tobs).filter(Measurement.date >= str(start))
    temp_list = [x[0] for x in temp]
    max_temp = max(temp_list)
    min_temp = min(temp_list)
    mean_temp = statistics.mean(temp_list)
    temp_dict = {"lowest value": min_temp,
                      "highest value": max_temp,
                      "average": mean_temp}
    return jsonify(temp_dict)
    session.close()


@app.route("/api/v1.0/<start>/<end>")
def end_date(start,end):
    session = Session(engine)
    temp = session.query(Measurement.tobs).filter(Measurement.date >= str(start)).filter(Measurement.date <= str(end))
    temp_list = [x[0] for x in temp]
    max_temp = max(temp_list)
    min_temp = min(temp_list)
    mean_temp = statistics.mean(temp_list)
    temp_dict = {"lowest value": min_temp,
                      "highest value": max_temp,
                      "average": mean_temp}
    return jsonify(temp_dict)
    session.close()


if __name__ == "__main__":
    app.run(debug=True)