from django.urls import path
from .views import RegisterView, ProfileView

urlpatterns = [
    path('registro/', RegisterView.as_view(), name='auth_register'),
    path('perfil/', ProfileView.as_view(), name='user_profile'),
]