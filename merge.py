import xml.etree.ElementTree as ET, xml
import pandas as pd
import os
from datetime import datetime
import numpy as np
import os
from math import radians, sin, cos, sqrt, atan2
import warnings


# Functions

def parse_coordinates(coordinates_str):
    coordinates = coordinates_str.split(',')
    if len(coordinates) == 3:
        return float(coordinates[0]), float(coordinates[1]), float(coordinates[2])
    elif len(coordinates) == 2:
        return float(coordinates[0]), float(coordinates[1]), None
    else:
        return None, None, None


def parse_kml(file_path):
    tree = ET.parse('./kmls/'+file_path)
    root = tree.getroot()

    data = []

    ns = {'ns0': 'http://earth.google.com/kml/2.1'}
    for placemark in root.findall('.//ns0:Placemark', namespaces=ns):
            timespan = placemark.find('.//ns0:TimeSpan', namespaces=ns)
            if timespan is not None:
                # Extracting timestamp
                begin_time_str = timespan.find('.//ns0:begin', namespaces=ns).text
                # Parsing timestamp into date and time
                date = datetime.strptime(file_path[:8], '%Y%m%d').date()
                time = begin_time_str.split('T')[1]
                time = time.split('.')[0]  # Remove milliseconds

                # Extracting coordinates and altitude
                coordinates_str = placemark.find('.//ns0:coordinates', namespaces=ns).text
                lng, lat, altitude = parse_coordinates(coordinates_str)

                data.append({
                    'Date': date,
                    'Time': time,
                    'Lat': lat,
                    'Lng': lng,
                    'Altitude': altitude
                }) 
    return pd.DataFrame(data)

def make_aggregations(df):

    warnings.filterwarnings("ignore")

    # Appropriate transformations
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')

    # Calculations preparing for aggregation
    df['Total Uphill'] = df['Altitude'].diff().clip(lower=0)
    df['Total Altitude Difference'] = df['Altitude'].diff()
    df['Highest Peak'] = df['Altitude']
    df['Lowest Trough'] = df['Altitude']

    # Distance Calculation 
    df.sort_values(by=['Date','Time'], inplace=True)

    # Function to calculate Haversine distance
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Radius of the Earth in kilometers

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    df['PrevLat'] = df['Lat'].shift(1)
    df['PrevLng'] = df['Lng'].shift(1)

    # Calculate distance between consecutive points
    df['Distance'] = df.apply(lambda row: haversine(row['Lat'], row['Lng'], row['PrevLat'], row['PrevLng']) if pd.notna(row['PrevLat']) else 0, axis=1)


    # Aggregation
    aggregated_df = df.groupby('Date').agg({
        'Time': lambda x: (x.max()-x.min()).seconds/60,
        'Total Uphill': 'sum',
        'Total Altitude Difference':'sum',
        'Highest Peak':'max',
        'Lowest Trough': 'min',
        'Distance':'sum',
    })
    aggregated_df.reset_index(inplace=True)

    return aggregated_df.values[0].tolist()


# Make full dataset

df_dict = {}

for kml_file in os.listdir('./kmls/'):
    df_dict[kml_file[:8]] = parse_kml(kml_file)


final_df = pd.concat([df_dict[key] for key in df_dict.keys()],axis=0)
final_df.reset_index(inplace=True,drop=True)

# Make aggregation dataset

df_date_dict = {}
for date in final_df['Date'].unique():
    df_date_dict[str(date)] = final_df[final_df['Date']==date]

list_df = []
columns = ['Date', 'Time', 'Total Uphill', 'Total Altitude Difference','Highest Peak', 'Lowest Trough', 'Distance']
for date_df in df_date_dict.keys():
    list_df.append(make_aggregations(df_date_dict[date_df]))

aggregated_data = pd.DataFrame(np.array(list_df),columns = columns)

# Export 

today_date = datetime.today().date()
final_df.to_csv(f'./expo/full datasets/{today_date}_running_data_2020to2024.csv',encoding='utf-8',header=True)
aggregated_data.to_csv(f'./expo/aggregated datasets/{today_date}_aggregated_running_data_2020to2024.csv',encoding='utf-8',header=True)