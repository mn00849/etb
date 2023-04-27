from django.shortcuts import get_object_or_404, render, redirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserBudget
from .forms import BudgetForm #Name of budget setting form, to be changed

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

@login_required
def logout(request):
    django_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = 'http://127.0.0.1:8000' # this can be current domain
    return redirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

@login_required
def set_budget(request):
    context ={}
    obj = get_object_or_404(UserBudget, id = request.user.id)
    userID = reqest.user.id
    if(obj == None):
        form = BudgetForm(request.POST or None, initial={'userID':userID})
        if(request.method == 'POST'):
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Budget has been set')
                return redirect('budget_page', userID = userID)
            else:
                messages.add_message(request, messages.ERROR, 'Invalid Form Data; Budget has not been set')
                context['form']= form
    else:
        if(obj.userID != request.userID):
            raise PermisssionDenied()
        form = BudgetForm(request.POST or None, instance = obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Budget Updated')
            return redirect('budget_page', userID = userID)
            context["form"] = form
    return render(request, "budget_setter", context)