from django.shortcuts import get_object_or_404, render, redirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import logout as django_logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserBudget
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import ContactForm, RoutePlannerForm, BudgetSetterForm
from datetime import date, datetime
from .models import transportType, UserBudget, Routes, User, carShare
import googlemaps
from django.db.models import Sum 

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

@login_required(login_url='/login/auth0')
def dashboard(request):
    context = {}
    return render(request, 'homeapp/dashboard.html', context)

def friends(request):
    context = {}
    return render(request, 'homeapp/friends.html', context)

def user(request):
    context = {}
    return render(request, 'homeapp/user.html', context)

def chat(request):
    context = {}
    return render(request, 'homeapp/chat.html', context)

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
    userID = request.user

    # finding the user
    currentUser = User.objects.get(id=request.user.id)

    #obj = get_object_or_404(UserBudget, userID = userID)
    if (UserBudget.objects.filter(userID = currentUser).exists()):
        budget = UserBudget.objects.get(userID = currentUser).budget
        endDate = UserBudget.objects.get(userID = currentUser).endDate
        context["budget"] = budget

        # calculating the amount remaining
        try:
            routesCost = Routes.objects.filter(userID=currentUser).aggregate(Sum('cost'))
            if (routesCost != 0 and (not (routesCost is None)) and (type(routesCost) != None)):
                routesCost = round(float(routesCost['cost__sum']), 2)
                remaining = round(float(budget), 2) - routesCost
                remaining = round(float(remaining), 2)
                context["budget_used"] = remaining
                context["costs"] = routesCost
        except:
            routesCost = 0
            context["budget_used"] = budget

        # getting time till reset
        endDateFormatted = datetime.strptime(str(endDate), "%Y-%m-%d")
        
        todayDate = date.today()

        if (endDate <= todayDate):
            UserBudget.objects.get(id = userID.id, endDate=endDate).delete()
            UserBudget.save()
        else:
            # finding time till next reset
            resetDate = endDate - todayDate
            resetDate = resetDate.days
            context["resetDate"] = resetDate
            

        
    return render(request, 'homeapp/budget.html', context)

@login_required(login_url='/login/auth0')
def logout(request):
    django_logout(request)
    domain = settings.SOCIAL_AUTH_AUTH0_DOMAIN
    client_id = settings.SOCIAL_AUTH_AUTH0_KEY
    return_to = 'http://127.0.0.1:8000' # this can be current domain
    return redirect(f'https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}')

@login_required(login_url='/login/auth0')
def set_budget(request):
    context = {}

    userID = User.objects.get(id=request.user.id)
    #obj = get_object_or_404(UserBudget, userID=userID)

    if (request.method == "GET"):
        form = BudgetSetterForm()
        context["form"] = form

    if (request.method == "POST"):
        # getting the data
        form = BudgetSetterForm(request.POST)

        # checking if there is already a budget
        if (form.is_valid()):
            car = form.cleaned_data['car']
            budget = form.cleaned_data['budget']
            mpg = form.cleaned_data['mpg']
            startDate = date.today()
            endDate = form.cleaned_data['endDate']

            # checking if there isn't already a budget set
            if (UserBudget.objects.filter(userID=userID).first() == None):
                newBudget = UserBudget(userID=userID,car=car,budget=budget,mpg=mpg,fuelType="",startDate=startDate,endDate=endDate)
                newBudget.save()
                return redirect('budget')
            else:
                # updating the user budget
                newBudget = UserBudget.objects.filter(userID=userID).update(car=car,budget=budget,mpg=mpg,fuelType="",endDate=endDate)

                return redirect('budget')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Form Data')
            form = BudgetSetterForm()
            context['form'] = form  
    else:
        if(userID.id != request.user.id):
            #raise PermisssionDenied()
            form = BudgetSetterForm()
    
    return render(request, "homeapp/budgetSet.html", context)

@login_required(login_url='/login/auth0')
def delete_budget(request):
    currentUser = User.objects.get(id=request.user.id)

    # finding the budget
    budget = UserBudget.objects.get(userID=currentUser)
    budget.delete()
    return redirect('budget')

@login_required(login_url='/login/auth0')
def routeplanner(request):
    context = {}

    if request.method == "GET":
        form = RoutePlannerForm()
        context["form"] = form
    else:
        form = RoutePlannerForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            endpoint = form.cleaned_data['endpoint']
            date = form.cleaned_data['date']
            friends = form.cleaned_data['friends']
            transport = transportType.objects.get(id=1).id # getting the DRIVING row

            # parsing the friends field
            if (friends != '') and (friends != None) and not (friends is None) and (friends) and (friends != "") and not form.data['friends']:
                print(f"Friends: {friends}.")
                if (len(friends) > 0):
                    friends = friends.replaceAll(" ", "")
                    friends = str(friends).split(",")
                else:
                    friends = None

            # checking if date is later than today
            todayDate = date.today()

            if (date < todayDate):
                messages.add_message(request, messages.ERROR, 'Date cannot be earlier than today')
                form = RoutePlannerForm()
                context['form'] = form

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
                
            if (friends != '') and (friends != None) and not (friends is None) and (friends) and (friends != "") and not form.data['friends']:
                if (len(friends) > 0):
                    for currentUser in friends:
                        # finding the user
                        if (User.objects.filter(email=currentUser).exists()):
                            user = User.objects.get(email=currentUser)
                            carshare = carShare(userID=user.id, routeID = routeID)
                            carshare.save()
                        else:
                            messages.add_message(request, messages.ERROR, 'Friend not found')
                            form = RoutePlannerForm()
                            context['form'] = form
        else:
            messages.add_message(request, messages.ERROR, 'Invalid Form Data')
            form = RoutePlannerForm()
            context['form'] = form 

        return redirect(reverse('routes'))
    return render(request, 'homeapp/routeplanner.html', context)

@login_required(login_url='/login/auth0')
def routes(request):
    context = {}

    # getting the current user object
    currentUser = User.objects.get(id=request.user.id)

    # getting all the user routes
    routes = Routes.objects.filter(userID=currentUser).all().order_by("-date")

    # getting all the friends that the user is travelling with
    friendsAll = []

    for route in routes:
        friends = carShare.objects.filter(routeID=route).all()

        if (type(friends) != None):
            # converting friends back into a string
            friendString = []

            for thisFriend in friends:
                # finding the user
                friendUser = User.objects.get(id=thisFriend.userID).email
                friendString.append(friendUser)

            friendString = ", ".join(friendString)
            friendsAll.append(friendString)
        
        context["friends"] = friendsAll

    if (len(friendsAll) == 0):
        del context["friends"]

    context["routes"] = routes

    return render(request, 'homeapp/routes.html', context)

@login_required(login_url='/login/auth0')
def deleteRoute(request, id):
    currentUser = User.objects.get(id=request.user.id)

    # finding the route
    route = Routes.objects.get(userID=currentUser, id=id)
    route.delete()
    return redirect('routes')

@login_required(login_url='/login/auth0')
def showRoute(request, id):
    context = {}

    # checking if it is one of this user's routes
    currentRoute = Routes.objects.get(id=id)
    currentUser = User.objects.get(id=request.user.id)
    if (type(currentRoute) != None):
        if (currentRoute.userID != currentUser):
            return redirect('routes')
        else:
            # it is this user's route
            context["route"] = currentRoute
        
    return render(request, 'homeapp/route.html', context)