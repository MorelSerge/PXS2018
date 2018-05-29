from django.contrib.gis import admin

from .models import *

# Register your models here.
admin.site.register(Country, admin.OSMGeoAdmin)
admin.site.register(Canton, admin.OSMGeoAdmin)
admin.site.register(City, admin.OSMGeoAdmin)
admin.site.register(Tile, admin.OSMGeoAdmin)