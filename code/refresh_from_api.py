# Dependencies
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import *
import json
import requests
from pprint import pprint
from config import driver, username, password, host, port, database
from sqlalchemy import create_engine
from time import ctime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

def refresh_from_api():

    #Connection string
    connection_string = f"{driver}://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)

    # reflect an existing database into a new model
    Base = automap_base()

    # reflect the tables
    Base.prepare(engine, reflect=True)

    session = Session(engine)

    ContentChoice = Base.classes.contentChoice

    # Table "contentChoice" has the list of locations that are being used in this App.
    resultsLocations = session.query(ContentChoice).all()
    session.close()

    # locations = [("Los Angeles", 34.0522, -118.2437),("Berkeley", 37.871853, -122.258423), ("La Jolla", 32.87888, -117.23593), ("Santa Barbara", 34.413963, -119.848946), ("Irvine", 33.64099, -117.84437)]
    weekly_forecast_full = pd.DataFrame()
    hourly_forecast_full = pd.DataFrame()

    locations = []

    for row in resultsLocations:
        location = ()

        city_name = row.city
        latitude = float(row.latitude)
        longitude = float(row.longitude)
        short_name = row.shortName

        location = (city_name, latitude, longitude, short_name)

        locations.append(location)

    for location in locations:
        city = location[0]
        lat = location[1]
        lon = location[2]
        shortname = location[3]

        ## Get initial endpoint for location
        # Assign initial api url to a variable
        lat_lon_url = f"https://api.weather.gov/points/{lat},{lon}"

        # API call to retrieve enpoints for location of lat and lon
        response = requests.get(lat_lon_url).json()

        # Specify the URL
        # Major cities in California
        weekly_url = response["properties"]["forecast"]
        hourly_url = response["properties"]["forecastHourly"]
        tz =  response["properties"]["timeZone"]

        # Make request and store response
        weekly_response = requests.get(weekly_url).json()
        retrievedDateTime = ctime()

        # # Find generatedAt string; convert to datetime object
        # call_datetime_str = weekly_response["properties"]["generatedAt"]
        # call_datetime = parse(call_datetime_str)

        # Find period forecasts; assign to variable
        period_forecasts = weekly_response["properties"]["periods"]

        weekly_forecast = []
        for i, period_forecast in enumerate(period_forecasts):
            # Isolate date and time from StartTime and EndTime; convert to datetime object
            start_date = datetime.strptime(period_forecasts[i]["startTime"].split("T")[0],"%Y-%m-%d").date()
            start_time = datetime.strptime(period_forecasts[i]["startTime"].split("T")[1],"%H:%M:%S%z").time()
            end_date = datetime.strptime(period_forecasts[i]["endTime"].split("T")[0],"%Y-%m-%d").date()
            end_time = datetime.strptime(period_forecasts[i]["endTime"].split("T")[1],"%H:%M:%S%z").time()
            
            # Get min, max wind speeds; get wind speed units
            wind_speed = period_forecasts[i]["windSpeed"].split(" ")
            if len(wind_speed) == 2:
                min_wind_speed = float(wind_speed[0])
                max_wind_speed = np.nan
                wind_speed_unit = wind_speed[1]
            elif len(wind_speed) == 4:
                min_wind_speed = float(wind_speed[0])
                max_wind_speed = float(wind_speed[2])
                wind_speed_unit = wind_speed[3]

            # Append dates and times to period_forecast dictionary
            period_forecast["city"] = city
            period_forecast['shortName'] = shortname
            period_forecast["startDate"] = start_date
            period_forecast["start_time"] = start_time
            period_forecast["endDate"] = end_date
            period_forecast["end_time"] = end_time
            period_forecast["minWindSpeed"] = min_wind_speed
            period_forecast["maxWindSpeed"] = max_wind_speed
            period_forecast["windSpeedUnit"] = wind_speed_unit
            period_forecast["latitude"] = lat
            period_forecast["longitude"] = lon
            period_forecast["retrievalDateTime"] = retrievedDateTime
            
            # Append period_forcast to weekly_forecast list
            weekly_forecast.append(period_forecast)

        # Create dataframe from "weekly_forecast" list
        weekly_forecast_raw_df = pd.DataFrame(weekly_forecast)

        # Copy weekly_forecast_raw_df to working dataframe
        weekly_forecast_working_df = weekly_forecast_raw_df

        # Convert startTime from string to datetime object
        weekly_forecast_working_df["startTime"] = pd.to_datetime(weekly_forecast_working_df["startTime"])

        # Convert endtTime from string to datetime object
        weekly_forecast_working_df["endTime"] = pd.to_datetime(weekly_forecast_working_df["endTime"])

        # Convert isDayTime from string to boolean
        weekly_forecast_working_df.replace({"isDaytime": {"True": True, "False": False}}, inplace=True)

        # Reasign column names
        weekly_forecast_working_df.rename(columns={"startTime":"startDateTime", "endTime":"endDateTime", "start_time":"startTime", "end_time":"endTime", "number":"responseNumber", "name":"responseName"}, inplace=True)

        # Rearange columns of dataframe
        weekly_forecast_working_df = weekly_forecast_working_df[['responseNumber', 'responseName', 'city', 'shortName', 'latitude', 'longitude','startDateTime', 'startDate', 'startTime', 'endDateTime', 'endDate', 'endTime', 'isDaytime', 'temperature', 'temperatureUnit', 'temperatureTrend', 'windSpeed','minWindSpeed', 'maxWindSpeed', 'windSpeedUnit', 'windDirection', 'icon', 'shortForecast', 'detailedForecast', 'retrievalDateTime']]

        # Copy working dataframe to final dataframe
        weekly_forecast_df = weekly_forecast_working_df

        # Make hourly forecast request and store response
        hourly_response = requests.get(hourly_url).json()

        # # Find generatedAt string; convert to datetime object
        # request_datetime_str = hourly_response["properties"]["generatedAt"]
        # request_datetime = parse(call_datetime_str)

        # Find hour forecasts; assign to variable
        hour_forecasts = hourly_response["properties"]["periods"]

        hourly_forecast = []
        for i, hour_forecast in enumerate(hour_forecasts):
            # Isolate date and time from StartTime and EndTime; convert to datetime object
            start_date = datetime.strptime(hour_forecasts[i]["startTime"].split("T")[0],"%Y-%m-%d").date()
            start_time = datetime.strptime(hour_forecasts[i]["startTime"].split("T")[1],"%H:%M:%S%z").time()
            end_date = datetime.strptime(hour_forecasts[i]["endTime"].split("T")[0],"%Y-%m-%d").date()
            end_time = datetime.strptime(hour_forecasts[i]["endTime"].split("T")[1],"%H:%M:%S%z").time()
            
            # Get hour wind speed; get wind speed units
            wind_speed = hour_forecasts[i]["windSpeed"].split(" ")
            hour_wind_speed = float(wind_speed[0])
            wind_speed_unit = wind_speed[1]

            # Append dates and times to hour_forecast dictionary
            hour_forecast["city"] = city
            hour_forecast['shortName'] = shortname
            hour_forecast["startDate"] = start_date
            hour_forecast["start_time"] = start_time
            hour_forecast["endDate"] = end_date
            hour_forecast["end_time"] = end_time
            hour_forecast["hourWindSpeed"] = hour_wind_speed
            hour_forecast["windSpeedUnit"] = wind_speed_unit
            hour_forecast["latitude"] = lat
            hour_forecast["longitude"] = lon
            hour_forecast["retrievalDateTime"] = retrievedDateTime
            
            # Append period_forcast to hourly_forecast list
            hourly_forecast.append(hour_forecast)

        # Create dataframe from "hourly_forecast" list
        hourly_forecast_raw_df = pd.DataFrame(hourly_forecast)

        # Copy hourly_forecast_raw_df to working dataframe
        hourly_forecast_working_df = hourly_forecast_raw_df

        # Convert startTime from string to datetime object
        hourly_forecast_working_df["startTime"] = pd.to_datetime(hourly_forecast_working_df["startTime"])

        # Convert endtTime from string to datetime object
        hourly_forecast_working_df["endTime"] = pd.to_datetime(hourly_forecast_working_df["endTime"])

        # Convert isDayTime from string to boolean
        hourly_forecast_working_df.replace({"isDaytime": {"True": True, "False": False}}, inplace=True)

        # Reasign column names
        hourly_forecast_working_df.rename(columns={"startTime":"startDateTime", "endTime":"endDateTime", "start_time":"startTime", "end_time":"endTime", "number":"responseNumber"}, inplace=True)

        # Drop empty columns "name" and "detailedForecast"
        hourly_forecast_working_df.drop(columns=["name", "detailedForecast"], inplace=True)

        # Rearange columns of dataframe
        hourly_forecast_working_df = hourly_forecast_working_df[['responseNumber', 'city', 'shortName', 'latitude', 'longitude','startDateTime', 'startDate', 'startTime', 'endDateTime', 'endDate', 'endTime', 'isDaytime', 'temperature', 'temperatureUnit', 'temperatureTrend', 'windSpeed','hourWindSpeed', 'windSpeedUnit', 'windDirection', 'icon', 'shortForecast', 'retrievalDateTime']]

        # Copy working dataframe to final dataframe
        hourly_forecast_df = hourly_forecast_working_df

        
        weekly_forecast_full = weekly_forecast_full.append(weekly_forecast_df)
        hourly_forecast_full = hourly_forecast_full.append(hourly_forecast_df)

    # Connection to database
    connection_string = f"{driver}://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    connection = engine.connect()
    session = Session(engine)

    # reflect an existing database into a new model
    Base = automap_base()

    # reflect the tables
    Base.prepare(engine, reflect=True)

    # Save reference to the tables
    DailyForecastTB = Base.classes.dailyForecastTB
    HourlyForecastTB = Base.classes.hourlyForecastTB

    # Clear tables befor loading new forecast data
    session.query(DailyForecastTB).delete()
    session.query(HourlyForecastTB).delete()

    session.commit()

    # print("Data cleared")

    # Update the Daily Forecast table to store Day level forecast
    weekly_forecast_full.to_sql('dailyForecastTB',connection, if_exists='append', index=False)

    # Update the Hourly Forecast table to store Hourwise forecast
    hourly_forecast_full.to_sql('hourlyForecastTB',connection, if_exists='append', index=False)

    session.commit()

    # print("Data loaded")

    # Read History Forecast data from the database
    DailyForecastTblDF = pd.read_sql_table('dailyForecastTB', connection)
    # print(DailyForecastTblDF)

    # Read History Forecast data from the database
    HourlyForecastTblDF = pd.read_sql_table('hourlyForecastTB', connection)