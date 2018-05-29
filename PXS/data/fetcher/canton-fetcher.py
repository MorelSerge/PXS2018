import os
import csv
import json

canton_population = 'canton-population.csv'
population = {}
with open(canton_population) as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        population[row[0]] = int(row[1])
canton_cars = 'canton-cars.csv'
cars = {}
with open(canton_cars) as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        cars[row[0]] = int(row[1])

geojson = '../Swiss-cantons.geojson'
with open(geojson, encoding='utf-8') as f:
    cantons = json.load(f)
for canton in cantons['features']:
    properties = canton['properties']
    properties['real_id'] = int(properties['@id'][len("relation/"):])
    properties['population'] = population[properties['name']]
    properties['cars'] = cars[properties['name']]
    properties['country_id'] = 51701

with open(geojson, 'w', encoding='utf-8') as f:
    json.dump(cantons, f, ensure_ascii=False)