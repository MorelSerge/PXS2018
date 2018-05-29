""" Script to import predicted data """
import os
import glob
from django.contrib.gis.geos import Polygon
from django.db import transaction
from ui import functions
from ui.models import Tile

def run(path=None):
    """ Runs the script """
    zoom = 16
    tile_size = 512
    tile_splits = 16
    tile_chunk = tile_size // tile_splits
    if not path:
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            'Notebooks',
            'Code2',
            'data'
            ))
    prediction_file_pattern = 'Predictions-Y*.p'
    files = glob.glob(os.path.join(path, prediction_file_pattern))
    print('Found {} pickled data files'.format(len(files)))
    count = 0
    y_in_db = Tile.objects.values('y').distinct()
    for idx, file in enumerate(files):
        already_in_db = False
        for c_y_in_db in y_in_db:
            if file.endswith('Y' + str(c_y_in_db['y']) + '.p'):
                already_in_db = True
        if already_in_db:
            print('Processed file {}/{} ({})'.format(idx + 1, len(files), file))
            continue
        data = functions.read_pickle(file)
        with transaction.atomic():
            for idx2, c_data in enumerate(data):
                c_x = c_data['x']
                c_y = c_data['y']
                c_pred = c_data['pred']
                c_splits = functions.split_tile(c_x, c_y, zoom, splits=tile_splits)
                for i in range(tile_splits):
                    for j in range(tile_splits):
                        c_split_pred = c_pred[i*tile_chunk:(i+1)*tile_chunk, j*tile_chunk:(j+1)*tile_chunk]
                        c_poly = c_splits[i, j].tolist()
                        c_poly.append(c_poly[0])
                        c_density = functions.calculate_density(c_split_pred)
                        c_sparsity = functions.calculate_sparsity(c_split_pred)
                        tile = Tile()
                        tile.x = c_x
                        tile.y = c_y
                        tile.index = i * tile_splits + j
                        tile.tree_density = c_density
                        tile.tree_sparsity = c_sparsity
                        tile.mpoly = Polygon([[p[1], p[0]] for p in c_poly]) # Reverse order for Polygon object
                        tile.save()
                        count += 1
        print('Processed file {}/{} ({})'.format(idx + 1, len(files), file))
    print('Processed {} tiles'.format(count))
