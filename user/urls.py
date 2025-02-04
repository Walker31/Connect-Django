from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('update-account/<int:user_id>/', views.update_account, name='update_account'),
    path('bulk/',views.bulk_signup,name='bulk')
]
    