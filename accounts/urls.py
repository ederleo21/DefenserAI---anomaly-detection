# accounts/urls.py
from django.urls import path
from .views import register, login_view
from django.contrib.auth import views as auth_logout

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_logout.LogoutView.as_view(), name='logout'),
]
