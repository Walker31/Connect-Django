from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('user.urls')),
    path('post/',include('post.urls')),
    path('azure/',include('azureservice.urls')),
    path('match/',include('matches.urls')),
    path('chat/',include('messaging.urls'))
]
