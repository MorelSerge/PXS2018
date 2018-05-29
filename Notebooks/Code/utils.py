import math
import numpy as np
from shapely.geometry import shape

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)
    
def polygon_union(features, start=None):
    polygon = start
    for feature in features:
        if polygon is None:
            polygon = shape(feature['geometry'])
        else:
            polygon = polygon.union(shape(feature['geometry']))
    return polygon
    
def split_image(img, chunk_size=16):
    split_size = img.shape[0] / chunk_size
    return [row.astype('float32') / 255.0 for column in np.split(img, split_size, axis=0) for row in np.split(column, split_size, axis=1)]
    
def rgb_to_bw(rgb):
    return rgb.convert('1')