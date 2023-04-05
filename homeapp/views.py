from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

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