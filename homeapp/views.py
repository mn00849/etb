from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

url = "https://www.globalpetrolprices.com/United-Kingdom/gasoline_prices/"

def getFuel():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    prices = soup.find_all("td")
    count = 1
    gas = 0
    for price in prices:
        try:
            thisPrice = float(price.get_text())
            gas = thisPrice
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
    context = {}
    return render(request, 'homeapp/contact.html', context)

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