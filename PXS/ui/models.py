""" Models """
from django.contrib.gis.db import models
from django.db.models import Window, F
from django.db.models.functions import RowNumber

class Tile(models.Model):
    """ Tile model """
    x = models.IntegerField()
    y = models.IntegerField()
    index = models.IntegerField()
    tree_density = models.FloatField()
    tree_sparsity = models.FloatField()

    mpoly = models.GeometryField(null=True, srid=4326, geography=True)

    def __str__(self):
        return 'tile/{}-{}-{}-{}'.format(self.pk, self.x, self.y, self.index)

class Country(models.Model):
    """ Country model """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    population = models.IntegerField(null=True)
    area = models.FloatField(null=True)
    cars = models.IntegerField(null=True)

    mpoly = models.GeometryField(null=True, srid=4326, geography=True)

    score = models.FloatField(null=True)
    tree_density = models.FloatField(null=True)
    tree_sparsity = models.FloatField(null=True)
    has_mapping = models.BooleanField(default=False)

    def get_rank(self):
        ranked_countries = Country.objects.exclude(score__isnull=True).annotate(rank=Window(expression=RowNumber(), order_by=[F('score').desc()]))
        for country in ranked_countries:
            if country.pk == self.pk:
                return country.rank
        return None

    def __str__(self):
        return 'country/{}'.format(self.name)

class Canton(models.Model):
    """ Canton model """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    population = models.IntegerField(null=True)
    area = models.FloatField(null=True)
    cars = models.IntegerField(null=True)

    mpoly = models.GeometryField(null=True, srid=4326, geography=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)

    score = models.FloatField(null=True)
    tree_density = models.FloatField(null=True)
    tree_sparsity = models.FloatField(null=True)
    has_mapping = models.BooleanField(default=False)

    def get_rank(self):
        ranked_cantons = Canton.objects.exclude(score__isnull=True).annotate(rank=Window(expression=RowNumber(), order_by=[F('score').desc()]))
        for canton in ranked_cantons:
            if canton.pk == self.pk:
                return canton.rank
        return None

    def get_relative_population(self):
        nr_of_country_cities = self.country.city_set.count()
        rel_population = self.population / self.country.population
        return rel_population

    def get_relative_area(self):
        nr_of_country_cities = self.country.city_set.count()
        rel_area = self.area / self.country.area
        return rel_area

    def get_cars_pp(self):
        cars_pp = self.cars / self.population
        return cars_pp

    def __str__(self):
        return 'canton/{}'.format(self.name)

class City(models.Model):
    """ City model """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    population = models.IntegerField(null=True)
    area = models.FloatField(null=True)
    cars = models.IntegerField(null=True)

    mpoly = models.GeometryField(null=True, srid=4326, geography=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE, null=True)

    score = models.FloatField(null=True)
    tree_density = models.FloatField(null=True)
    tree_sparsity = models.FloatField(null=True)
    has_mapping = models.BooleanField(default=False)

    def get_rank(self):
        ranked_cities = City.objects.exclude(score__isnull=True).annotate(rank=Window(expression=RowNumber(), order_by=[F('score').desc()]))
        for city in ranked_cities:
            if city.pk == self.pk:
                return city.rank
        return None

    def get_relative_population(self):
        nr_of_country_cities = self.country.city_set.count()
        rel_population = self.population / self.country.population
        return rel_population

    def get_relative_area(self):
        nr_of_country_cities = self.country.city_set.count()
        rel_area = self.area / self.country.area
        return rel_area

    def get_cars_pp(self):
        cars_pp = self.cars / self.population
        return cars_pp

    def __str__(self):
        return 'city/{}'.format(self.name)
