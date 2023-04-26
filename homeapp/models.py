from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    pass

class UserBudget(models.Model):
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.CharField(max_length=128)
    fuelType = models.CharField(max_length=32, default=None)
    budget = models.DecimalField(max_digits=16,decimal_places=2)
    mpg = models.DecimalField(max_digits=16,decimal_places=2)
    startDate = models.DateField()
    endDate = models.DateField()

class fuelPrice(models.Model):
    price = models.DecimalField(max_digits=16,decimal_places=2)
    date = models.DateTimeField()

class Routes(models.Model):
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=16,decimal_places=2)
    origin = models.CharField(max_length=256, default=None)
    destination = models.CharField(max_length=256, default=None)
    emissions = models.DecimalField(max_digits=16,decimal_places=2)
    transportType = models.IntegerField()
    date = models.DateTimeField()

class transportType(models.Model):
    type = models.CharField(max_length=128)

class Friend(models.Model):
    userOne = models.IntegerField()
    userTwo = models.IntegerField()

class carShare(models.Model):
    userID = models.IntegerField()
    routeID = models.ForeignKey(Routes, on_delete=models.CASCADE)