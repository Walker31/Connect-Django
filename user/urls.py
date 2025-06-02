from django.urls import path
from .views import SignupView, LoginView, UpdateAccountView, BulkSignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UpdateAccountView.as_view(), name='update_account'),
    path('bulk-signup/', BulkSignupView.as_view(), name='bulk_signup'),
]
