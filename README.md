# Huawei GT2 KML to Table Data Converter

## Overview

This Python script converts KML files exported from Huawei GT2 watches into a structured table format, making it easier for further analysis. The resulting table includes columns for Date, Time, Latitude (Lat), Longitude (Lng), and Altitude. It is required that you place all your kml files into the kmls folder.

## Installation

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/tzikos/huawei-gt2-kml-converter.git
    ```

2. Navigate to the project directory:

    ```bash
    cd huawei-gt2-kml-converter
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script by providing the path to your Huawei GT2 KML file:

```bash
python merge.py 
