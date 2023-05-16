from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserBudget, fuelPrice, Routes, transportType, Friend, carShare, Room, Message

admin.site.register(User, UserAdmin)
admin.site.register(UserBudget)
admin.site.register(fuelPrice)
admin.site.register(Routes)
admin.site.register(transportType)
admin.site.register(Friend)
admin.site.register(carShare)
admin.site.register(Room)
admin.site.register(Message)