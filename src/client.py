import geopy
import plotly.express as px
import pandas as pd
import time
import requests
import json
import planner

geolocator = geopy.geocoders.Nominatim(user_agent='sendhelp')
px.set_mapbox_access_token(open("../secret/mapbox_token").read())

default_addrs = [
    '4 Trinity Lane Cambridge', 'North Paddock Cambridge', 'Cambridge South Paddock',
    'Cambridge Cambridge Bridge Street 12 UK', 'Cambridge 12 Round Church Street',
    '1 Grange Road CB2 9AS'
]


def get_data():
    return requests.get('http://9272-188-39-25-218.ngrok.io/data').content


def address_plot_data(datapoints):
    datapoints = datapoints.copy()
    ok = []
    for key, value in datapoints.items():
        try:
            gc = geolocator.geocode(value['address'])
            value = value.copy()
            value['capacity'] = int(value['capacity'])
            assert value['capacity'] > 0
        except (ValueError, AssertionError):
            pass
        else:
            if gc is not None:
                value = value.copy()
                value['gc'] = gc
                value['name'] = key
                print(gc.raw, value)
                ok.append(value)
    data = pd.DataFrame({
        'lat': d['gc'].latitude, 'lon': d['gc'].longitude,
        'address': d['gc'].address, 'name': d['name'],
        'capacity': d['capacity']
    } for d in ok)
    clustering = planner.cluster(data[["lat", "lon"]], 3)
    return clustering, data


def plot_loop():
    colors = px.colors.qualitative.Dark24
    last_raw = None
    while raw := get_data():
        if last_raw != raw:
            cl, df = address_plot_data(json.loads(raw))
            fig = px.scatter_mapbox(
                df, lat='lat', lon='lon', hover_name='name', custom_data=['address'],
                color=[colors[l % len(colors)] for l in cl.labels_],
                zoom=16, size=6*df['capacity']**.5
            )
            fig.update_layout(mapbox_style="basic")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            fig.show()
        last_raw = raw
        time.sleep(5)


if __name__ == '__main__':
    plot_loop()