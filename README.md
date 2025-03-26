# Hawaii Climate Analysis Project

## Project Overview

This project demonstrates data analysis and visualization skills through a comprehensive climate analysis of Honolulu, Hawaii. The analysis involves working with historical climate data using SQLAlchemy, Pandas, and Matplotlib, followed by implementing a Flask API to make the data accessible.

## Technical Skills Showcased

* **Data Analysis** : SQL queries, statistical analysis, and data exploration
* **Data Visualization** : Creating informative plots using Matplotlib
* **Database Management** : Using SQLAlchemy ORM to interact with SQL databases
* **API Development** : Building a Flask API with multiple endpoints
* **Python Programming** : Pandas for data manipulation, Flask for web development

## Project Structure

The project is divided into two main parts:

### Part 1: Data Analysis and Exploration

In this section, I analyze climate data using Python and SQLAlchemy:

* Connect to an SQLite database using SQLAlchemy
* Reflect database tables into Python classes
* Perform precipitation analysis:

  * Identify the most recent date in the dataset
  * Collect 12 months of precipitation data
  * Load data into Pandas DataFrames for analysis
  * Visualize precipitation trends over time
  * Calculate summary statistics

  ![1741318557296](image/README/Histogram_README.md_image.png)
* Perform station analysis:

  * Calculate the total number of stations
  * Identify the most active stations
  * Analyze temperature data for the most active station
  * Create a histogram of temperature observations

  ![1741318534085](image/README/Second_diagram.png)

### Part 2: Flask API Development

In this section, I design and implement a Flask API with the following routes:

* Home route (`/`): Lists all available routes
* Precipitation route (`/api/v1.0/precipitation`): Returns JSON precipitation data
* Stations route (`/api/v1.0/stations`): Returns JSON list of stations
* Temperature Observations route (`/api/v1.0/tobs`): Returns temperature data for the most active station
* Start/End Date routes (`/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`): Returns temperature statistics for specified date ranges
* [Station Analysis ](http://127.0.0.1:5000/api/v1.0/station-analysis): **/api/v1.0/station-analysis**

## Tools and Technologies Used

* **Python** (with Pandas, NumPy)
* **SQLAlchemy ORM**
* **SQLite**
* **Flask**
* **Matplotlib**
* **Jupyter Notebook**

## Methodology

1. **Data Collection** : Access the provided SQLite database containing Hawaii climate data
2. **Data Cleaning and Preparation** : Query, filter, and organize data for analysis
3. **Exploratory Analysis** : Generate statistics and visualizations to understand climate patterns
4. **API Development** : Create routes to make the analyzed data accessible via web endpoints

## Key Findings

* Identified seasonal precipitation patterns across Hawaii
* Determined the most reliable weather stations for data collection
* Analyzed temperature trends to help with vacation planning
* Created a user-friendly API to access climate data programmatically

---

This project demonstrates my proficiency in data analysis, visualization, and API development, showing how I can transform raw data into meaningful insights and accessible applications.
