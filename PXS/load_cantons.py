import os
import json
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
import ui
from ui.models import Canton, Country

def run():
    geojson = os.path.abspath(os.path.join(os.path.dirname(ui.__file__), '..' , 'data', 'Swiss-cantons.geojson'))
    with open(geojson, encoding='utf-8') as f:
        cantons = json.load(f)
    for canton in cantons['features']:
        properties = canton['properties']
        canton_model = Canton()
        canton_model.id = properties['real_id']
        canton_model.name = properties['name']
        canton_model.population = properties['population']
        canton_model.cars= properties['cars']
        canton_model.mpoly = GEOSGeometry(json.dumps(canton['geometry']))
        canton_model.country = Country.objects.get(id=properties['country_id'])
        
        canton_model.save()
        canton_model = Canton.objects.annotate(area_=Area('mpoly')).get(id=canton_model.id)
        canton_model.area = canton_model.area_.sq_m
        canton_model.save()