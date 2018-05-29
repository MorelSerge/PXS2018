import os
import csv
import json

canton_population = 'city-population.csv'
population = {}
with open(canton_population) as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        population[row[0][11:]] = int(row[1])
        
with open('../Swiss-cantons.geojson', encoding='utf-8') as f:
    cantons = json.load(f)
def findCanton(cantonnum):
    for canton in cantons['features']:
        if canton['properties']['swisstopo:KANTONSNUM'] == cantonnum:
            return canton['properties']
    return None

skip = ['Riviera','La Grande-Béroche']
geojson = '../Swiss-cities.geojson'
with open(geojson, encoding='utf-8') as f:
    cities = json.load(f)
for city in cities['features']:
    properties = city['properties']
    properties['real_id'] = int(properties['@id'][len("relation/"):])
    try:
        if properties['name'] in population:
            properties['population'] = population[properties['name']]
        else:
            try:
                properties['population'] = population[properties['official_name']]
                properties['name'] = properties['official_name']
            except KeyError as e:
                if properties['name'] not in skip:
                    print(properties['name'])
                    raise e
                else:
                    properties['population'] = None
    except KeyError as e:
        print(properties)
        raise e
    canton = findCanton(properties['swisstopo:KANTONSNUM'])
    if canton is None:
        print('No canton found for {}'.format(city))
        break
    if properties['name'] not in skip:
        properties['cars'] = int(canton['cars'] * properties['population'] / canton['population'])
    else:
        properties['cars'] = None
    properties['country_id'] = 51701
    properties['canton_id'] = canton['real_id']

with open(geojson, 'w', encoding='utf-8') as f:
    json.dump(cities, f, ensure_ascii=False)