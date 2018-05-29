""" Functions """
import json
import math
import pickle
import cv2
import numpy as np
from shapely.geometry import shape, Polygon
from skimage.filters.rank import entropy
from skimage.morphology import disk
from PIL import Image, ImageDraw

def num2deg(xtile, ytile, zoom):
    """ Transforms x,y to lat,long """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def deg2num(lat_deg, lon_deg, zoom):
    """ Transforms lat,long to x,y """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def read_pickle(file):
    """ Reads a pickle file """
    with open(file, 'rb') as f:
        return pickle.load(f)

def write_pickle(data, file):
    """ Writes a pickle file """
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def read_json(file):
    """ Reads JSON file """
    with open(file) as f:
        return json.load(f)

def color_from_density(density):
    """ Converts density to color """
    colors = [
        '#f7fcf5',
        '#e5f5e0',
        '#c7e9c0',
        '#a1d99b',
        '#74c476',
        '#41ab5d',
        '#238b45',
        '#006d2c',
        '#00441b'
    ]
    idx = 0
    if density > 0.9:
        idx = 8
    elif density > 0.8:
        idx = 7
    elif density > 0.7:
        idx = 6
    elif density > 0.6:
        idx = 5
    elif density > 0.5:
        idx = 4
    elif density > 0.4:
        idx = 3
    elif density > 0.3:
        idx = 2
    elif density > 0.2:
        idx = 1
    else:
        idx = 0
    return colors[idx]

def get_polygon(data, densities=None, img_height=512):
    """ Gets polygon image from GeoJSON """
    data = shape(data)
    if isinstance(data, Polygon):
        polygons = [data]
    else:
        polygons = list(data)
    minx = np.inf
    miny = np.inf
    maxx = 0
    maxy = 0
    all_ys = []
    data_points = {}
    for i, p in enumerate(polygons):
        x, y = p.exterior.xy
        all_ys.extend(y)
        data_points[i] = {}
        data_points[i]['x'] = np.array(x)
        data_points[i]['y'] = np.array(y)
        cminx = data_points[i]['x'].min()
        cminy = data_points[i]['y'].min()
        cmaxx = data_points[i]['x'].max()
        cmaxy = data_points[i]['y'].max()
        if cminx < minx:
            minx = cminx
        if cminy < miny:
            miny = cminy
        if cmaxx > maxx:
            maxx = cmaxx
        if cmaxy > maxy:
            maxy = cmaxy
    averagey = np.mean(all_ys)
    xrange = maxx - minx # longitude
    yrange = maxy - miny # latitude

    xrange *= 111.320 / 110.574 * math.cos(math.radians(averagey))
    for i in list(data_points.keys()):
        data_points[i]['x'] *= 111.320 / 110.574 * math.cos(math.radians(averagey))
        cminx = data_points[i]['x'].min()
        if cminx < minx:
            minx = cminx

    aspect_ratio = xrange / yrange
    padding = 10
    img_height = 512
    drawable_height = img_height - 2 * padding
    drawable_width = int(round(aspect_ratio * drawable_height))
    img_width = drawable_width + 2 * padding

    poly = Image.new('RGBA', (img_width, img_height))
    back = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    polygon_drawer = ImageDraw.Draw(poly)
    for i in list(data_points.keys()):
        x = data_points[i]['x']
        y = data_points[i]['y']
        x = x - minx
        y = y - miny
        x /= xrange
        y /= yrange
        x = np.rint(x * drawable_width) + padding
        y = np.rint(y * drawable_height) + padding
        polygon_drawer.polygon(list(zip(x, y)), fill=(255, 255, 255, 0), outline=(71, 82, 94, (0 if densities else 255)))

    if densities:
        print('hi')
        density_drawer = ImageDraw.Draw(back)
        circle_size = 0.00034332275
        circle_size *= 111.320 / 110.574 * math.cos(math.radians(averagey))
        circle_size /= xrange
        circle_size = np.rint(circle_size * drawable_width)
        circle_radius = circle_size // 2 + 1
        for density in densities:
            x = density['x']
            y = density['y']
            d = density['value']
            if d > 0:
                x *= 111.320 / 110.574 * math.cos(math.radians(averagey))
                x -= minx
                y -= miny
                x /= xrange
                y /= yrange
                x = np.rint(x * drawable_width) + padding
                y = np.rint(y * drawable_height) + padding
                density_drawer.ellipse([
                    (x - circle_radius, y - circle_radius),
                    (x + circle_radius, y + circle_radius)
                ], fill=color_from_density(d))  

    back.paste(poly, mask=poly)
    back = back.transpose(Image.FLIP_TOP_BOTTOM)
    return back

def square_coordinates_to_geometry(coordinates):
    """ Gets GeoJSON geometry field from square coordinates """
    return {
        'type': 'Polygon',
        'coordinates': [[
            coordinates[0][::-1],
            coordinates[1][::-1],
            coordinates[2][::-1],
            coordinates[3][::-1],
            coordinates[0][::-1]
        ]]
    }

def square_coordinates_to_geojson(coordinates):
    """ Tranforms 4 square coordinates to GeoJSON """
    if isinstance(coordinates, np.ndarray):
        coordinates = coordinates.tolist()
    feature = {
        'type': 'Feature',
        'properties': {},
        'geometry': square_coordinates_to_geometry(coordinates)
    }
    return json.dumps(feature)
def get_tile_corners(x, y, zoom):
    """ Gets a tile's corners in lat/long """
    ul = num2deg(x, y, zoom)
    ur = num2deg(x+1, y, zoom)
    lr = num2deg(x+1, y+1, zoom)
    ll = num2deg(x, y+1, zoom)
    return [ul, ur, lr, ll]
def get_tile_geojson(x, y, zoom):
    """ Gets a tile's GeoJSON representation """
    ul, ur, lr, ll = get_tile_corners(x, y, zoom)
    return square_coordinates_to_geojson([ul, ur, lr, ll])
def split_tile(x, y, zoom, splits=16):
    """ Splits a tile in chunks and returns lat/long coordinates """
    ul, ur, _, ll = get_tile_corners(x, y, zoom)
    lat_diff = (ul[0] - ll[0]) / splits
    long_diff = (ur[1] - ul[1]) / splits
    out = np.ndarray((splits, splits, 4, 2))
    for i in range(splits):
        for j in range(splits):
            out[i, j, :, :] = [
                [ul[0] - i*lat_diff, ul[1] + j*long_diff],
                [ul[0] - i*lat_diff, ul[1] + (j+1)*long_diff],
                [ul[0] - (i+1)*lat_diff, ul[1] + (j+1)*long_diff],
                [ul[0] - (i+1)*lat_diff, ul[1] + j*long_diff],
            ]
    return out

def calculate_density(pred):
    """ Calculates binary density """
    return np.count_nonzero(pred) / pred.size

def calculate_sparsity(pred):
    """ Calculates binary sparsity """
    _, thresh_entropy = cv2.threshold(entropy(pred, disk(3)), 0.5, 1, cv2.THRESH_BINARY)
    entropy_zero_count = np.count_nonzero(thresh_entropy)
    normal_zero_count = np.count_nonzero(pred)
    if normal_zero_count == 0:
        sparsity = 1
    elif entropy_zero_count == 0:
        sparsity = 1 / pred.size
    elif entropy_zero_count > normal_zero_count:
        sparsity = 1
    else:
        sparsity = entropy_zero_count / normal_zero_count
    return sparsity

def sparsity_to_representable(sparsity):
    """ Transforms a sparsity [0,1] to a usable coefficient """
    return math.exp(-sparsity) - math.exp(-1)
