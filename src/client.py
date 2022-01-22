import geopy
import plotly.express as px
import pandas as pd
import planner

geolocator = geopy.geocoders.Nominatim(user_agent='sendhelp')

addrs = ['4 Trinity Lane Cambridge', 'North Paddock Cambridge', 'Cambridge South Paddock', 'Cambridge Bridge Street 12', 'Cambridge 12 Round Church']
gcs = [geolocator.geocode(addr) for addr in addrs]

df = pd.DataFrame({'lat': gc.latitude, 'lon': gc.longitude, 'address': gc.address} for gc in gcs)

cl = planner.cluster(df[["lat", "lon"]], 3)
k = len(cl.cluster_centers_)


px.set_mapbox_access_token(open("../.mapbox_token").read())

colors = px.colors.qualitative.Dark24
fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="address",
                        color=[colors[l % len(colors)] for l in cl.labels_], zoom=10, size=[15]*len(df))
fig.update_layout(mapbox_style="basic")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
