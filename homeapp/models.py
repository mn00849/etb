from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
from datetime import datetime

class User(AbstractUser):
    pass

class UserBudget(models.Model):
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.CharField(max_length=128, null=False)
    fuelType = models.CharField(max_length=32, default="")
    budget = models.DecimalField(max_digits=16,decimal_places=2, validators=[MinValueValidator(0)])
    mpg = models.DecimalField(max_digits=16,decimal_places=2, default=50, null=False, validators=[MinValueValidator(0)])
    startDate = models.DateField(null=False)
    endDate = models.DateField(null=False)

class fuelPrice(models.Model):
    price = models.DecimalField(max_digits=16,decimal_places=2)
    date = models.DateTimeField(default=None)

class Routes(models.Model):
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=16,decimal_places=2, validators=[MinValueValidator(0)])
    origin = models.CharField(max_length=256, default=None, null=False)
    destination = models.CharField(max_length=256, default=None, null=False)
    emissions = models.DecimalField(max_digits=16,decimal_places=2, validators=[MinValueValidator(0)])
    transportType = models.IntegerField()
    distance = models.DecimalField(max_digits=16,decimal_places=2, default=0, validators=[MinValueValidator(0)])
    date = models.DateField(default=None)

class transportType(models.Model):
    type = models.CharField(max_length=128)

class Friend(models.Model):
    userOne = models.IntegerField()
    userTwo = models.IntegerField()

class carShare(models.Model):
    userID = models.IntegerField()
    routeID = models.ForeignKey(Routes, on_delete=models.CASCADE)

class Room(models.Model):
    name = models.CharField(max_length=1000)

class Message(models.Model):
    value = models.CharField(max_length=1000000)
    date = models.DateTimeField(default=datetime.now(), blank=True)
    user = models.CharField(max_length=1000000)
    room = models.CharField(max_length=1000000)