import xml.etree.ElementTree as ET
import pandas as pd
import os

def parse_coordinates(coordinates_str):
    coordinates = coordinates_str.split(',')
    if len(coordinates) == 3:
        return float(coordinates[0]), float(coordinates[1]), float(coordinates[2])
    elif len(coordinates) == 2:
        return float(coordinates[0]), float(coordinates[1]), None
    else:
        return None, None, None


def parse_kml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []

    ns = {'ns0': 'http://earth.google.com/kml/2.1'}
    for placemark in root.findall('.//ns0:Placemark', namespaces=ns):
            timespan = placemark.find('.//ns0:TimeSpan', namespaces=ns)
            if timespan is not None:
                # Extracting timestamp
                begin_time_str = timespan.find('.//ns0:begin', namespaces=ns).text
                # Parsing timestamp into date and time
                date, time = begin_time_str.split('T')
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

df_dict = {}

for kml_file in os.listdir('./kmls/'):
    df_dict[kml_file[:8]] = parse_kml('./kmls/'+kml_file)


final_df = pd.concat([df_dict[key] for key in df_dict.keys()],axis=0)

final_df.to_csv('./expo/running_data_2020to2024.csv',encoding='utf-8',header=True)