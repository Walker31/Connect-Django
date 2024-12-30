from django.urls import path
from . import views

urlpatterns = [
    path('get_matches', views.find_profiles_within_radius, name='getMatches'),
]
    