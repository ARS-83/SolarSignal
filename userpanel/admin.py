from django.contrib import admin
from userpanel.models import Subscription,CustomUser
# Register your models here.

admin.site.register(Subscription)
admin.site.register(CustomUser)