""" Script to import cities """
import os
import json
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.geos import GEOSGeometry
import ui
from ui.models import City, Canton, Country

def run():
    """ Runs the script """
    geojson = os.path.abspath(os.path.join(
        os.path.dirname(ui.__file__),
        '..',
        'data',
        'Swiss-cities.geojson'
        ))
    with open(geojson, encoding='utf-8') as f:
        cities = json.load(f)
    for city in cities['features']:
        properties = city['properties']
        city_model = City()
        city_model.id = properties['real_id']
        city_model.name = properties['name']
        city_model.population = properties['population']
        city_model.cars = properties['cars']
        city_model.mpoly = GEOSGeometry(json.dumps(city['geometry']))
        city_model.country = Country.objects.get(id=properties['country_id'])
        city_model.canton = Canton.objects.get(id=properties['canton_id'])

        city_model.save()
        city_model = City.objects.annotate(area_=Area('mpoly')).get(id=city_model.id)
        city_model.area = city_model.area_.sq_m
        city_model.save()
