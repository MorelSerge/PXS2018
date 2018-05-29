""" Script to calculate all the scores for the cities, cantons and countries """
from django.db.models.aggregates import Count, Avg
from django.db.models.functions import Cast
from django.db.models import Subquery, OuterRef, Q
from django.contrib.gis.db.models import GeometryField
import numpy as np
from ui.models import Canton, Country, City, Tile
from ui import functions

weights = [
    160, # Tree coverage
    240, # Tree sparsity
    30, # Cars per person
    1, # Relative population
    2 # Relative area
]

def run():
    """ Runs the script """
    # First do it for the cities which have tiles
    countries = Country.objects.all()
    country_count = countries.count()
    for idx1, country in enumerate(countries):
        nr_of_country_cities = City.objects.filter(country=country).count()
        # TODO: REMOVE canton__name='Vaud'
        cities = City.objects.filter(country=country).filter(Q(canton__name='Vaud') | Q(canton__name='Genève'))
        city_count = cities.count()
        for idx2, city in enumerate(cities):
            metrics = Tile.objects.annotate(geom=Cast('mpoly', GeometryField())) \
                .filter(geom__within=city.mpoly) \
                .annotate(count=Count('*')) \
                .filter(count__gt=0) \
                .aggregate(Avg('tree_density'), Avg('tree_sparsity'))
            if metrics['tree_density__avg'] is not None: # Check if result returned, a.k.a has tiles
                tree_density = metrics['tree_density__avg']
                tree_sparsity = metrics['tree_sparsity__avg']
                cars_pp = city.cars / city.population
                rel_population = city.population / country.population * nr_of_country_cities
                rel_area = city.area / country.area * nr_of_country_cities
                city.tree_density = tree_density
                city.tree_sparsity = tree_sparsity
                city.score = np.dot(weights, [
                    tree_density,
                    functions.sparsity_to_representable(tree_sparsity),
                    (1 - cars_pp),
                    rel_population,
                    rel_area
                ])
                city.has_mapping = True
                city.save()
            print('Fetched city {}/{} ({})'.format(idx2 + 1, city_count, city.name))
        print('Fetched country {}/{} ({})'.format(idx1 + 1, country_count, country.name))
