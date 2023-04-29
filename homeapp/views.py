from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import ContactForm, RoutePlannerForm
from .models import transportType, UserBudget, Routes, User, carShare
import googlemaps 

url = "https://www.globalpetrolprices.com/United-Kingdom/gasoline_prices/"

def getFuel():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    prices = soup.find_all("td")
    count = 0
    gas = 0
    for price in prices:
        try:
            thisPrice = float(price.get_text())
            gas = thisPrice
            count += 1
            if (count == 2):
                break
        except ValueError:
            continue  

    return gas

# Create your views here.
def home(request):
    context = {}
    return render(request, 'homeapp/home.html', context)

def about(request):
    context = {}
    return render(request, 'homeapp/about.html', context)

def contact(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            email = form.cleaned_data['email']
            message = name + ':\n' + form.cleaned_data['message']
            try:
                send_mail(subject, message, email, ['so00647@surrey.ac.uk'])
            except BadHeaderError():
                return HttpResponse("Invalid header found.")
            return redirect(reverse('home'))
    return render(request, 'homeapp/contact.html', {"form": form})

@login_required(login_url='/login/auth0')
def budget(request):
    context = {}
    return render(request, 'homeapp/budget.html', context)

@login_required(login_url='/login/auth0')
def logout(request):
    django_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = 'http://127.0.0.1:8000' # this can be current domain
    return redirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

@login_required(login_url='/login/auth0')
def routeplanner(request):
    if request.method == "GET":
        form = RoutePlannerForm()
    else:
        form = RoutePlannerForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            endpoint = form.cleaned_data['endpoint']
            date = form.cleaned_data['date']
            friends = form.cleaned_data['friends']
            transport = transportType.objects.get(id=1).id # getting the DRIVING row

            # parsing the friends field
            if (len(friends) > 0):
                friends = str(friends).split(",")
            else:
                friends = None

            # calculating the cost of the journey
            my_API_KEY = "AIzaSyBrgHg_dQJ4qJW_BR5VmQ-x_nhVy9A8tfg"

            gmaps = googlemaps.Client(key=my_API_KEY)
            
            distance = gmaps.distance_matrix(origin,endpoint)['rows'][0]['elements'][0]["distance"]["value"]
            #print(gmaps.distance_matrix(origin,endpoint)['rows'])
            # converting km to miles
            distance = float((distance / 1000) / 1.6)

            mpg = UserBudget.objects.get(userID=request.user).mpg
            fuelUsed = round(float(distance)/float(mpg),2)

            fuelPrice = getFuel()
            cost = round(float(fuelUsed)*fuelPrice,2)

            # source: https://connectedfleet.michelin.com/blog/calculate-co2-emissions
            emissions = round(2.68*float(fuelUsed), 2)

            route = Routes(userID=request.user, cost=cost, origin=origin, destination=endpoint, emissions=emissions, transportType=transport, date=date)
            route.save()

            # adding the friends to the carshare table
            routeID = Routes.objects.latest('id') # finding the route

            if (len(friends) > 0):
                for currentUser in friends:
                    # finding the user
                    user = User.objects.get(email=currentUser).id
                    carshare = carShare(userID=user, routeID = routeID)

            return redirect(reverse('home'))
    return render(request, 'homeapp/routeplanner.html', {"form": form})