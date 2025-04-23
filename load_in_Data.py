import cdsapi
import os

os.chdir(os.path.dirname(__file__))



dataset = "cams-global-atmospheric-composition-forecasts"
request = {
    "variable": [
        "particulate_matter_2.5um",
        "particulate_matter_10um"
    ],
    "date": ["2018-01-01/2022-12-31"],
    "time": ["00:00", "12:00"],
    "leadtime_hour": ["0"],
    "type": ["forecast"],
    "data_format": "grib",
    "area": [37, -19, 20, -1]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()