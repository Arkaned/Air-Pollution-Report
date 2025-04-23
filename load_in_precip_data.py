import cdsapi

dataset = "satellite-precipitation"
request = {
    "variable": "all",
    "time_aggregation": "daily_mean",
    "year": [
        "2018", "2019", "2020",
        "2021", "2022"
    ],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "day": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
    "area": [32.1, -8.5, 31, -7.5]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()