import urllib3
import json
import os
from base64 import b64encode
import math
from datetime import datetime, timezone
from dateutil import tz

def lambda_handler(event, context):
    # Token generation from WattTime API
    http = urllib3.PoolManager()
    credentials = b64encode(b'sudhagreen:Green@123').decode('utf-8')
    response = http.request(
        'GET',
        'https://api.watttime.org/login',
        headers={
            'Authorization': f'Basic {credentials}'
        }
    )
    output = response.data.decode('utf-8')
    TOKEN = json.loads(output)['token']
    
    #fetch region details. By default we work with CAISO_NORTH as watt time supports only that for free
    my_region = os.environ['AWS_REGION']
    
    # forecast the co2 levels for next 24 hours
    params = {
    "signal_type": "co2_moer",
    "region": "CAISO_NORTH"
    }
    response = http.request(
        'GET',
        'https://api.watttime.org/v3/forecast',
        headers={
            'Authorization': f"Bearer {TOKEN}"
        },
        fields = params
    )
    data_output = response.data.decode('utf-8')
    
    json_data = json.loads(data_output)
    only_data = json_data.get('data')
    
    pgm_duration = 5*60 
    allowed_exec_window = 5*60*60
    
    if len(data_output) == 0:
        print("No forecast returned and job would be executed straightaway without any delay")
    else:
        ex_time_frame = 8
        est_ex_duration = 9
        # find the best time to run the code within ex_time_frame given est_ex_duration of the task
        best_time = find_best_trigger_time(only_data, ex_time_frame, est_ex_duration)
        
    #print(best_time)
    return best_time

def find_best_trigger_time(data, ex_time_frame, est_ex_duration):
    """
    Find the best time to trigger a workload within a time window based on CO2 levels.

    Parameters:
    data (list): List of objects containing timestamp and CO2 levels.
    ex_time_frame (int): Duration of the workload in hours.
    est_ex_duration (int): Time for the execution of workload in minutes.

    Returns:
    str: Best time to trigger the workload.
    """
    ex_time_frame = math.ceil((ex_time_frame * 60) / 5) # Convert workload duration to minutes

    best_time = None
    lowest_avg_co2 = float('inf')
    
    # Iterate through each time slot within the time window
    for i in range(ex_time_frame):
        new_val = est_ex_duration//5
        # Calculate average CO2 level for the workload duration starting from this time slot
        avg_co2 = sum(data[i]['value'] for data[i] in data[i:i+new_val]) / new_val
        if avg_co2 < lowest_avg_co2:
            lowest_avg_co2 = avg_co2
            best_time = data[i]['point_time']
            best_point = i

    # Parse the given timestamp into a datetime object
    given_timestamp = datetime.fromisoformat(best_time)
    
    # Convert the given timestamp to the CAISO_NORTH timezone
    caiso_north_timezone = tz.gettz('America/Los_Angeles')
    given_timestamp_caiso_north = given_timestamp.astimezone(caiso_north_timezone)
    
    # Get the current time in the CAISO_NORTH timezone
    current_time_caiso_north = datetime.now(caiso_north_timezone)
    
    time_difference =  given_timestamp_caiso_north - current_time_caiso_north
    
    time_difference_seconds = int(time_difference.total_seconds())
    
    print(time_difference_seconds)
    
    response = {
        "bestTime": time_difference_seconds
    }
    
    #print(best_point)
    return response