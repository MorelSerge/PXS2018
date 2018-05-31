from ui.models import *
from django.db.models.functions import Cast
from django.contrib.gis.db.models import GeometryField
import json

canton = Canton.objects.get(name='Genève')
output = []
city_count = canton.city_set.count()
for idx, city in enumerate(canton.city_set.all()):
    c_dict = {}
    c_dict['tree_density'] = city.tree_density
    c_dict['tree_sparsity'] = city.tree_sparsity
    c_dict['name'] = city.name
    c_dict['geometry'] = city.mpoly.json
    
    tiles = Tile.objects.annotate(geom=Cast('mpoly', GeometryField())).filter(geom__within=city.mpoly)
    c_dict['data'] = []
    for tile in tiles:
        centroid = tile.mpoly.centroid
        c_dict['data'].append({'x': centroid.x, 'y': centroid.y, 'value': tile.tree_density})
    output.append(c_dict)
    print('Parsed city {}/{}'.format(idx+1, city_count))

with open('geneva-cities.json', 'w') as f:
    json.dump(output, f)