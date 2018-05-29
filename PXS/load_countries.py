import os
import ui
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from ui.models import Country
from django.contrib.gis.db.models.functions import Area

def run(verbose=True):
    country_shape = os.path.abspath(os.path.join(os.path.dirname(ui.__file__), '..' , 'data', 'Switzerland.geojson'))
    ds = DataSource(country_shape)
    lyr = ds[0]
    feat = lyr[0]
    layer_mapping = {
        'name': 'name:en',
        'id': 'real_id',
        'population': 'population',
        'mpoly': 'POLYGON'
    }
    layer_mapping = LayerMapping(
        Country,
        country_shape,
        layer_mapping,
        transform=False,
        encoding='iso-8859-1'
    )
    layer_mapping.save(strict=True, verbose=verbose)

    country = Country.objects.annotate(area_=Area('mpoly')).get(id=51701)
    country.cars =  feat.get('cars') / country.population  
    country.area = country.area_.sq_m
    country.save()