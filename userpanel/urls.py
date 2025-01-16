from django.urls import path
from .views import *

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('checklogin', check_login, name='checklogin'),
    path('getsignals', get_signals, name='getsignals'),
]
