import numpy as np
import geopandas as gpd
from shapely.geometry import Point

def task_func(cities=None, dic=None):
    if dic is None:
        dic = {'Lon': (-180, 180), 'Lat': (-90, 90)}
    if ('Lon' not in dic or 'Lat' not in dic
        or not isinstance(dic['Lon'], tuple)
        or not isinstance(dic['Lat'], tuple)):
        raise ValueError("Invalid dictionary format.")

    lon_min, lon_max = dic['Lon']
    lat_min, lat_max = dic['Lat']

    if cities is None:
        cities = ['New York', 'London', 'Beijing', 'Tokyo', 'Sydney']

    data = {'City': [], 'Coordinates': []}
    for city in cities:
        x = np.random.uniform(lon_min, lon_max)
        y = np.random.uniform(lat_min, lat_max)
        data['City'].append(city)
        data['Coordinates'].append(Point(x, y))

    # GeoDataFrame ohne explizit gesetzte crs
    gdf = gpd.GeoDataFrame(data, geometry='Coordinates')

    # Laufzeitfehler: .to_crs(epsg=4326) verlangt eine definierte crs,
    # die hier jedoch fehlt. Führt zu ValueError:
    # "Cannot transform naive geometries. Please set a crs on the object first."
    gdf = gdf.to_crs(epsg=4326)

    return gdf


