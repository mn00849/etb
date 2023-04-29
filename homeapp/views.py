from django.shortcuts import get_object_or_404, render, redirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from django.contrib import messages
from .models import UserBudget
from .forms import BudgetForm #Name of budget setting form, to be changed
=======
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import ContactForm, RoutePlannerForm
>>>>>>> bbb9a19afe5d5dce0e523adfd0752f6c8753ba14

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

<<<<<<< HEAD
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
=======
def routeplanner(request):
    if request.method == "GET":
        form = RoutePlannerForm()
    else:
        form = RoutePlannerForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            endpoint = form.cleaned_data['endpoint']
            return redirect(reverse('home'))
    return render(request, 'homeapp/routeplanner.html', {"form": form})
>>>>>>> bbb9a19afe5d5dce0e523adfd0752f6c8753ba14
