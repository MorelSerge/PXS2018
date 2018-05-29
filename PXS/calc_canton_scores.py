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
    # First do it for the cantons which have fetched cities
    countries = Country.objects.all()
    country_count = countries.count()
    for idx1, country in enumerate(countries):
        nr_of_country_cantons = Canton.objects.filter(country=country).count()
        cantons = Canton.objects.filter(Q(name='Vaud') | Q(name='Genève'))
        canton_count = cantons.count()
        for idx2, canton in enumerate(cantons):
            metrics = City.objects.filter(canton=canton).aggregate(Avg('tree_density'), Avg('tree_sparsity'))
            if metrics['tree_density__avg'] is not None:
                tree_density = metrics['tree_density__avg']
                tree_sparsity = metrics['tree_sparsity__avg']
                cars_pp = canton.cars / canton.population
                rel_population = canton.population / country.population * nr_of_country_cantons
                rel_area = canton.area / country.area * nr_of_country_cantons
                canton.tree_density = tree_density
                canton.tree_sparsity = tree_sparsity
                canton.score = np.dot(weights, [
                    tree_density,
                    functions.sparsity_to_representable(tree_sparsity),
                    (1 - cars_pp),
                    rel_population,
                    rel_area
                ])
                canton.has_mapping = True
                canton.save()
            print('Fetched canton {}/{} ({})'.format(idx2 + 1, canton_count, canton.name))
        print('Fetched country {}/{} ({})'.format(idx1 + 1, country_count, country.name))
