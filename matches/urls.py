from django.urls import path
from . import views

urlpatterns = [
    path('get', views.find_profiles, name='find_profiles'),
    path('swipe',views.updateList, name= 'Update List')
]
