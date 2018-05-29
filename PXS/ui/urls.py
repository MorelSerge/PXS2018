""" URLs """
from django.urls import path

from . import views

app_name = 'ui'
urlpatterns = [
    path('', views.index, name='index'),
    path('ranking', views.ranking, name='ranking'),
    path('country/<int:id>', views.country, name='country'),
    path('country/<int:id>/cantons', views.countryCantons, name='countryCantons'),
    path('canton/<int:id>', views.canton, name='canton'),
    path('canton/<int:id>/cities', views.cantonCities, name='cantonCities'),
    path('canton/<int:id>/polygon', views.cantonPolygon, name='cantonPolygon'),
    path('city/<int:id>', views.city, name='city'),
    path('city/<int:id>/polygon', views.cityPolygon, name='cityPolygon'),
    path('polygon', views.polygon, name='polygon'),
    path('polygon/stats', views.polygonStats, name='polygonStats'),
]
