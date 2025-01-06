from django.urls import path
from . import views

urlpatterns = [
    path('get_matches', views.find_profiles, name='getMatches'),
]
    