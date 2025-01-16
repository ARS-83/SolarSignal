from django.urls import path
from .views import register, login, check_login

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('checklogin', check_login, name='checklogin'),

]
