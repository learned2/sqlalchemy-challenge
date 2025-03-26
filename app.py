# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify, render_template
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

#################################################
# Database Setup
#################################################

# Get absolute path to the database file
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "Resources", "hawaii.sqlite")

# Check if database file exists
if not os.path.exists(db_path):
    print(f"ERROR: Database file not found at: {db_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Contents of Resources directory:")
    resources_dir = os.path.join(basedir, "Resources")
    if os.path.exists(resources_dir):
        print(os.listdir(resources_dir))
    else:
        print("Resources directory not found")

# Create engine using the absolute path to the database file
engine = create_engine(f"sqlite:///{db_path}")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Function to find date one year from the last date in the database
def date_prev_year():
    # Create the session
    session = Session(engine)
    
    # Query the most recent date from the Measurement table
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Close the session                   
    session.close()
    
    # Convert the recent date string to datetime object
    recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    
    # Calculate the date one year from the last date
    prev_year_date = recent_date - dt.timedelta(days=365)
    
    # Convert the date to string format
    prev_year_date = prev_year_date.strftime('%Y-%m-%d')
    
    return prev_year_date

# Function to find the most active station
def most_active_station():
    session = Session(engine)
    
    # Query to find the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
    
    session.close()
    
    # Return the most active station id
    return active_stations[0][0]

#################################################
# Flask Setup
#################################################
# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Start at the homepage.
# List all the available routes.
@app.route("/")
def homepage():
    return """ <h1> Welcome to Honolulu, Hawaii Climate API! </h1>
    <h3> The available routes are: </h3>
    <ul>
    <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: <strong>/api/v1.0/precipitation</strong> </li>
    <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li>
    <li><a href = "/api/v1.0/tobs"> TOBS </a>: <strong>/api/v1.0/tobs</strong></li>
    <li><a href = "/api/v1.0/station-analysis"> Station Analysis </a>: <strong>/api/v1.0/station-analysis</strong></li>
    <li>To retrieve the minimum, average, and maximum temperatures for a specific start date, use <strong>/api/v1.0/&ltstart&gt</strong> (replace start date in yyyy-mm-dd format)</li>
    <li>To retrieve the minimum, average, and maximum temperatures for a specific start-end range, use <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (replace start and end date in yyyy-mm-dd format)</li>
    </ul>
    """

# Define the station analysis route
@app.route("/api/v1.0/station-analysis")
def station_analysis():
    # Create a session
    session = Session(engine)
    
    try:
        # 1. Find the number of stations in the dataset
        station_count = session.query(func.count(Station.station)).scalar()
        
        # 2. List stations and observation counts in descending order
        station_obs = session.query(Measurement.station, 
                                    func.count(Measurement.station).label('observation_count'),
                                    Station.name).\
                            join(Station, Measurement.station == Station.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).all()
        
        # Get most active station
        most_active = station_obs[0][0]
        
        # 3. Find min, max, and avg temperatures for most active station
        temp_stats = session.query(func.min(Measurement.tobs),
                                   func.avg(Measurement.tobs),
                                   func.max(Measurement.tobs)).\
                            filter(Measurement.station == most_active).all()
        
        # 4. Get previous 12 months of TOBS data for most active station
        tobs_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == most_active).\
                        filter(Measurement.date >= date_prev_year()).all()
        
        # 5. Save query results to DataFrame
        tobs_df = pd.DataFrame(tobs_data, columns=['date', 'tobs'])
        
        # 6. Create histogram
        plt.figure(figsize=(10, 6))
        plt.hist(tobs_df['tobs'], bins=12, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title(f'Temperature Observations for Station {most_active}')
        plt.xlabel('Temperature (F)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        
        # Save plot to a temporary buffer
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        
        # Format station observation data for display
        station_list = []
        for station, count, name in station_obs:
            station_list.append({
                "station_id": station,
                "name": name,
                "observation_count": count
            })
        
        # Prepare the analysis results
        analysis = {
            "station_count": station_count,
            "stations_by_activity": station_list,
            "most_active_station": {
                "id": most_active,
                "name": station_obs[0][2],
                "observation_count": station_obs[0][1],
                "temperature_stats": {
                    "min": temp_stats[0][0],
                    "avg": round(temp_stats[0][1], 2),
                    "max": temp_stats[0][2]
                }
            },
            "tobs_data_sample": tobs_df.head(5).to_dict(orient="records"),
            "plot": f"data:image/png;base64,{plot_url}"
        }
        
        # Return the analysis results as HTML
        html_response = f"""
        <h1>Station Analysis</h1>
        <h3>Number of Stations: {analysis['station_count']}</h3>
        <h3>Stations by Activity:</h3>
        <ul>
        {''.join([f"<li>{station['name']} (ID: {station['station_id']}) - {station['observation_count']} observations</li>" for station in analysis['stations_by_activity']])}
        </ul>
        <h3>Most Active Station:</h3>
        <p>ID: {analysis['most_active_station']['id']}</p>
        <p>Name: {analysis['most_active_station']['name']}</p>
        <p>Observation Count: {analysis['most_active_station']['observation_count']}</p>
        <h3>Temperature Stats:</h3>
        <p>Min: {analysis['most_active_station']['temperature_stats']['min']} F</p>
        <p>Avg: {analysis['most_active_station']['temperature_stats']['avg']} F</p>
        <p>Max: {analysis['most_active_station']['temperature_stats']['max']} F</p>
        <h3>TOBS Data Sample:</h3>
        <ul>
        {''.join([f"<li>Date: {record['date']}, TOBS: {record['tobs']}</li>" for record in analysis['tobs_data_sample']])}
        </ul>
        <h3>TOBS Histogram:</h3>
        <img src="{analysis['plot']}" alt="TOBS Histogram">
        """
        
        return html_response
    
    finally:
        # Close the session
        session.close()

# Define what to do when the user hits the precipitation URL
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session
    session = Session(engine)

    # Query precipitation data from last 12 months from the most recent date from Measurement table
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
    
    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of prcp_list
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(prcp_list)


# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def stations():
    # Create the session
    session = Session(engine)

    # Query station data from the Station dataset
    station_data = session.query(Station.station).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_data))

    # Return a list of jsonified station data
    return jsonify(station_list)


# Define what to do when the user hits the URL
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    # Query tobs data from last 12 months from the most recent date from Measurement table
    most_active = most_active_station()
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == most_active).\
                    filter(Measurement.date >= date_prev_year()).all()

    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)


# Define what to do when the user hits the URL with a specific start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create the session
    session = Session(engine)
    
    try:
        # Make a list to query (the minimum, average and maximum temperature)
        sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        
        # Check if there is an end date then do the task accordingly
        if end == None: 
            # Query the data from start date to the most recent date
            start_data = session.query(*sel).\
                                filter(Measurement.date >= start).all()
            # Convert list of tuples into normal list
            start_list = list(np.ravel(start_data))
            return jsonify(start_list)
        else:
            # Query the data from start date to the end date
            start_end_data = session.query(*sel).\
                                filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).all()
            # Convert list of tuples into normal list
            start_end_list = list(np.ravel(start_end_data))
            return jsonify(start_end_list)
    finally:
        # Close the session                   
        session.close()
    
# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)