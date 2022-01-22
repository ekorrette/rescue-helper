import geopy
import plotly.express as px
import pandas as pd
import planner

geolocator = geopy.geocoders.Nominatim(user_agent='sendhelp')

addrs = [
    '4 Trinity Lane Cambridge', 'North Paddock Cambridge', 'Cambridge South Paddock',
    'Cambridge Cambridge Bridge Street 12 UK', 'Cambridge 12 Round Church Street',
    '1 Grange Road CB2 9AS'
]

gcs = [geolocator.geocode(addr) for addr in addrs]

df = pd.DataFrame({'lat': gc.latitude, 'lon': gc.longitude, 'address': gc.address} for gc in gcs)

cl = planner.cluster(df[["lat", "lon"]], 3)
k = len(cl.cluster_centers_)


px.set_mapbox_access_token(open("../secret/mapbox_token").read())

colors = px.colors.qualitative.Dark24
fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="address",
                        color=[colors[l % len(colors)] for l in cl.labels_], zoom=16, size=[15]*len(df))
fig.update_layout(mapbox_style="basic")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
