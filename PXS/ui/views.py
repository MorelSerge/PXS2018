import os
import json
import numpy as np
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.core.serializers import serialize
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models.functions import Cast
from django.db.models.aggregates import Avg, Sum
from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.geos import GEOSGeometry
from ui import functions, models


# Create your views here.
def index(request):
    return render(request, 'pxs/index.html')

def ranking(request):
    return render(request, 'pxs/ranking.html')

@require_http_methods(["GET"])
@cache_page(60*60)
def country(request, id):
    response = {}
    country = models.Country.objects.filter(id=id).first()
    if country:
        response = json.loads(serialize('json', [country], fields=('pk', 'name', 'tree_density', 'score', 'has_mapping')))[0]
        response['fields']['rank'] = country.get_rank()
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def countryCantons(request, id):
    response = {}
    country = models.Country.objects.filter(id=id).first()
    if country:
        response = json.loads(serialize('geojson', country.canton_set.all(), fields=('pk', 'name', 'mpoly', 'has_mapping', 'score')))
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def canton(request, id):
    response = {}
    canton = models.Canton.objects.filter(id=id).first()
    if canton:
        response = json.loads(serialize('json', [canton], fields=('pk', 'name', 'tree_density', 'score', 'has_mapping')))[0]
        response['fields']['rank'] = canton.get_rank()
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def cantonCities(request, id):
    response = {}
    canton = models.Canton.objects.filter(id=id).first()
    if canton:
        response = json.loads(serialize('geojson', canton.city_set.all(), fields=('pk', 'name', 'mpoly', 'has_mapping', 'score')))
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def city(request, id):
    response = {}
    city = models.City.objects.filter(id=id).first()
    if city:
        response = json.loads(serialize('json', [city], fields=('pk', 'name', 'tree_density', 'score', 'has_mapping')))[0]
        response['fields']['rank'] = city.get_rank()
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def polygon(request):
    param = request.GET.get('geojson', None)
    if not param:
        raise Http404
    parsed_geojson = json.loads(param)
    geometry = GEOSGeometry(json.dumps(parsed_geojson['geometry']))
    tiles = models.Tile.objects \
        .annotate(geom=Cast('mpoly', GeometryField())) \
        .filter(geom__within=geometry)
    densities = []
    for tile in tiles:
        centroid = tile.mpoly.centroid
        densities.append({'x': centroid.x, 'y': centroid.y, 'value': tile.tree_density})
    polygon = functions.get_polygon(parsed_geojson['geometry'], densities=densities)
    response = HttpResponse(content_type='image/png')
    polygon.save(response, 'PNG')
    return response
    
@require_http_methods(["GET"])
@cache_page(60*60)
def polygonStats(request):
    param = request.GET.get('geojson', None)
    if not param:
        raise Http404
    response = {}
    parsed_geojson = json.loads(param)
    geometry = GEOSGeometry(json.dumps(parsed_geojson['geometry']))
    country = models.Country.objects \
        .annotate(geom=Cast('mpoly', GeometryField())) \
        .filter(geom__contains=geometry) \
        .first()
    if country:
        metrics = models.Tile.objects \
            .annotate(geom=Cast('mpoly', GeometryField())) \
            .filter(geom__within=geometry) \
            .aggregate(Avg('tree_density'), Avg('tree_sparsity'), Sum(Area('mpoly')))
        tree_density = 0
        tree_sparsity = 0
        weights = [
            160, # Tree coverage
            240, # Tree sparsity
            2 # Relative area
        ]
        if metrics['tree_density__avg']: # Check if result returned, a.k.a has tiles
            tree_density = metrics['tree_density__avg']
            tree_sparsity = metrics['tree_sparsity__avg']
            rel_area = metrics['Area__sum'].sq_m / country.area
            score = np.dot(weights, [
                tree_density,
                functions.sparsity_to_representable(tree_sparsity),
                rel_area
            ])
            response['tree_density'] = tree_density
            response['tree_sparsity'] = tree_sparsity
            response['score'] = score
    return JsonResponse(response)

@require_http_methods(["GET"])
@cache_page(60*60)
def cityPolygon(request, id):
    item = models.City.objects.filter(id=id).first()
    if item is None:
        raise Http404
    tiles = models.Tile.objects \
        .annotate(geom=Cast('mpoly', GeometryField())) \
        .filter(geom__within=item.mpoly)
    densities = []
    for tile in tiles:
        centroid = tile.mpoly.centroid
        densities.append({'x': centroid.x, 'y': centroid.y, 'value': tile.tree_density})
    polygon = functions.get_polygon(json.loads(item.mpoly.json), densities=densities)
    response = HttpResponse(content_type='image/png')
    polygon.save(response, 'PNG')
    return response

@require_http_methods(["GET"])
@cache_page(60*60)
def cantonPolygon(request, id):
    item = models.Canton.objects.filter(id=id).first()
    if item is None:
        raise Http404
    tiles = models.Tile.objects \
        .annotate(geom=Cast('mpoly', GeometryField())) \
        .filter(geom__within=item.mpoly)
    densities = []
    for tile in tiles:
        centroid = tile.mpoly.centroid
        densities.append({'x': centroid.x, 'y': centroid.y, 'value': tile.tree_density})
    polygon = functions.get_polygon(json.loads(item.mpoly.json), densities=densities)
    response = HttpResponse(content_type='image/png')
    polygon.save(response, 'PNG')
    return response
