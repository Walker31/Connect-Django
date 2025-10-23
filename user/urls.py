from django.urls import path
from .views import (
    SignupView, 
    LoginView, 
    AccountView,
    BulkSignupView,
    updateList,
    find_profiles,
    GoogleLoginView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('bulk-signup/', BulkSignupView.as_view(), name='bulk-signup'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('account/', AccountView.as_view(), name='account'),

    path('update-list/', updateList, name='update-list'),
    path('find-profiles/', find_profiles, name='find-profiles'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login')
]