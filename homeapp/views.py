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
from .forms import ContactForm, RoutePlannerForm, BudgetSetterForm, FriendForm
from datetime import date, datetime
from .models import transportType, UserBudget, Routes, User, carShare, Friend, Room, Message
import googlemaps
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
import uuid
import json

url = "https://www.globalpetrolprices.com/United-Kingdom/gasoline_prices/"

def getFuel():
    proxyDict = { 
          'http'  : "http://mn00849.pythonanywhere.com", 
          'https' : "https://mn00849.pythonanywhere.com"
        }
    response = requests.get(url, proxies={"http": "http://mn00849.pythonanywhere.com"})
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

def handler404(request, exception, template_name="404.html"):
    response = render(request, 'homeapp/exception.html', {})
    response.status_code = 404
    return response

@login_required(login_url='/login/auth0')
def dashboard(request):
    context = {}
    return render(request, 'homeapp/dashboard.html', context)

@login_required(login_url='/login/auth0')
def friends(request):
    context = {}

    # getting this users' friends
    friendsList = []

    friends1 = Friend.objects.filter(userOne=request.user.id).all()
    friends2 = Friend.objects.filter(userTwo=request.user.id).all()
    if (type(friends1) != None):
        # getting all the user objects of the friends
        for friend in friends1:
            thisUser = User.objects.get(id=friend.userTwo)
            if (type(thisUser) != None):
                friendsList.append(thisUser)
    if (type(friends2) != None):
        # getting all the user objects of the friends
        for friend in friends2:
            thisUser = User.objects.get(id=friend.userOne)
            if (type(thisUser) != None):
                friendsList.append(thisUser)

    if (len(friendsList) > 0):
        context["friends"] = friendsList

    return render(request, 'homeapp/friends.html', context)

@login_required(login_url='/login/auth0')
def user(request):
    context = {}
    context["user"] = request.user
    return render(request, 'homeapp/user.html', context)

@login_required(login_url='/login/auth0')
def stats(request):
    context = {}

    currentUser = User.objects.get(id=request.user.id)

    # getting the number of carbon emissions for each route
    # emissionsSortedDates
    emissions = []
    dates = []

    today = date.today()

    #accessing the year attribute
    year = today.year

    routesByDate = Routes.objects.filter(userID=currentUser, date__year = int(year)).all().order_by("date")
    # getting the stats per month
    monthsEmissions = [0,0,0,0,0,0,0,0,0,0,0,0]
    for route in routesByDate:
        
        # getting the current month of the route
        dateTravel = datetime.strptime(str(route.date), "%Y-%m-%d")
        month = dateTravel.month
        emissionsTravel = float(route.emissions)

        monthsEmissions[month-1] += emissionsTravel

    context["emissionsTime"] = json.dumps(monthsEmissions)

    # showing the cost per route for this month
    costRouteX = [0]
    costRouteY = [0]

    routesByDate = Routes.objects.filter(userID=currentUser, date__year = int(year), date__month = int(today.month)).all().order_by("date")

    if (len(routesByDate) > 0):
        for route in routesByDate:

            # getting the cost of the trip
            cost = float(route.cost)

            costRouteX.append(len(costRouteX))
            costRouteY.append(cost)

        context["costRouteX"] = json.dumps(costRouteX)
        context["costRouteY"] = json.dumps(costRouteY)

    # showing average distance of journeys
    # < 1 miles, >= 1 miles and < 5 miles, >= 5 miles and < 10 miles, >= 10 miles and < 25 miles, >= 25 miles
    distanceRoute = [0,0,0,0,0]

    routesByDate = Routes.objects.filter(userID=currentUser, date__year = int(year), date__month = int(today.month)).all().order_by("date")

    if (len(routesByDate) > 0):
        for route in routesByDate:
            # getting the distance of the route
            distance = float(route.distance)

            # comparing distance
            if (distance < 1):
                distanceRoute[0] += 1
            if (distance >= 1 and distance < 5):
                distanceRoute[1] += 1
            if (distance >= 5 and distance < 10):
                distanceRoute[2] += 1
            if (distance >= 10 and distance < 25):
                distanceRoute[3] += 1
            if (distance >= 25):
                distanceRoute[4] += 1

        context["distanceRoute"] = json.dumps(distanceRoute)

    return render(request, 'homeapp/stats.html', context)

@login_required(login_url='/login/auth0')
def chatlist(request):
    context = {}

    # getting this users' friends
    friendsList = []
    roomNames = []

    friends1 = Friend.objects.filter(userOne=request.user.id).all()
    friends2 = Friend.objects.filter(userTwo=request.user.id).all()
    if (type(friends1) != None):
        # getting all the user objects of the friends
        for friend in friends1:
            thisUser = User.objects.get(id=friend.userTwo)
            if (type(thisUser) != None):
                # sorting the names
                names = sorted([request.user.email, thisUser.email])
                roomName = uuid.uuid5(uuid.NAMESPACE_X500, names[0]+ "|" + names[1])
                friendsList.append({"user":thisUser,"room":roomName})
    if (type(friends2) != None):
        # getting all the user objects of the friends
        for friend in friends2:
            thisUser = User.objects.get(id=friend.userOne)
            if (type(thisUser) != None):
                names = sorted([request.user.email, thisUser.email])
                roomName = uuid.uuid5(uuid.NAMESPACE_X500, names[0]+ "|" + names[1])
                friendsList.append({"user":thisUser,"room":roomName})

    if (len(friendsList) > 0):
        context["friends"] = friendsList

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

        # getting time till reset
        endDateFormatted = datetime.strptime(str(endDate), "%Y-%m-%d")
        
        todayDate = date.today()

        # calculating the amount remaining
        try:
            routesCost = Routes.objects.filter(userID=currentUser, date__range=[todayDate, endDate]).aggregate(Sum('cost'))
            if (routesCost != 0 and (not (routesCost is None)) and (type(routesCost) != None)):
                routesCost = round(float(routesCost['cost__sum']), 2)
                remaining = round(float(budget), 2) - routesCost
                remaining = round(float(remaining), 2)
                context["budget_used"] = remaining
                context["costs"] = routesCost
        except:
            routesCost = 0
            context["budget_used"] = budget

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

            startWithTime = datetime(
                year=startDate.year, 
                month=startDate.month,
                day=startDate.day,
            )

            # boundary checks
            if (float(budget) < 0 or float(mpg) < 0 or datetime.strptime(str(endDate), "%Y-%m-%d") < startWithTime):
                messages.add_message(request, messages.ERROR, 'Invalid Form Data')
                form = BudgetSetterForm()
                context['form'] = form
            else:
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

    if (UserBudget.objects.filter(userID=currentUser).exists()):
        # finding the budget
        budget = UserBudget.objects.get(userID=currentUser)
        budget.delete()
    return redirect('budget')

@login_required(login_url='/login/auth0')
def routeplanner(request):
    context = {}

    # checking if a budget exists for the user
    currentUser = User.objects.get(id=request.user.id)

    if (not UserBudget.objects.filter(userID=currentUser).exists()):
        messages.add_message(request, messages.ERROR, "You cannot create routes before you have a budget! Please create a budget.")
        return redirect('setbudget')

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
            #print(f"Friends: {friends}.")
            if (len(friends) > 0):
                friends = friends.replace(" ", "")
                friends = str(friends).split(",")
            else:
                friends = ""

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

            route = Routes(userID=request.user, cost=cost, origin=origin, destination=endpoint, emissions=emissions, distance=distance,transportType=transport, date=date)
            route.save()

            # adding the friends to the carshare table
            routeID = Routes.objects.latest('id') # finding the route

            if (type(friends) != type(None) or friends != ""):    
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
    routes = Routes.objects.filter(userID=currentUser).all().order_by("date")
    allRoutes = []

    # getting all the friends that the user is travelling with
    friendsAll = []

    for route in routes:
        friends = carShare.objects.filter(routeID=route).all()

        if (type(friends) != None and len(friends) > 0):
            # converting friends back into a string
            friendString = []

            for thisFriend in friends:
                # finding the user
                friendUser = User.objects.get(id=thisFriend.userID).email
                friendString.append(friendUser)

            friendString = ", ".join(friendString)
            friendsAll.append(friendString)
    
            #print(f"route {route.id} has {friendString} joining on the trip.")
            allRoutes.append({"route":route,"friends":friendString})
        else:
            allRoutes.append({"route":route,"friends":0})

    '''if (len(friendsAll) == 0):
        context.pop["friends"]'''

    context["routes"] = allRoutes

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

@login_required(login_url='/login/auth0')
def addFriend(request):
    context = {}

    if request.method == "GET":
        form = FriendForm()
        context["form"] = form

    if request.method == "POST":
        form = FriendForm(request.POST)
        if (form.is_valid()):
            # checking if the user exists

            userEmail = form.cleaned_data['friend']

            # finding the user
            userFriend = User.objects.filter(email=userEmail)
            if (type(userFriend) != None) and (userFriend.exists()):
                # check if user hasn't typed themself
                if (userFriend.first().id == request.user.id):
                    messages.add_message(request, messages.ERROR, 'You cannot friend yourself!')
                    form = FriendForm()
                    context['form'] = form
                else:
                    # checking if the users aren't already friends
                    check1 = Friend.objects.filter(userOne=request.user.id, userTwo=userFriend.first().id)
                    check2 = Friend.objects.filter(userOne=userFriend.first().id, userTwo=request.user.id)
                    #print(check1)
                    #print(check2)
                    if (type(check1) != None or type(check2) != None) and (check1.exists() or check2.exists()):
                        # users are already friends
                        messages.add_message(request, messages.ERROR, 'You are already friends with this user!')
                        form = FriendForm()
                        context['form'] = form
                        return redirect('addfriend')
                    else:
                        # users can be added as friends
                        newFriend = Friend(userOne=request.user.id, userTwo=userFriend.first().id)
                        newFriend.save()
                        return redirect('friends')
                
            else:
                # send error back to the user
                messages.add_message(request, messages.ERROR, 'User does not exist')
                form = FriendForm()
                context['form'] = form

    return render(request, 'homeapp/addfriend.html', context)

@login_required(login_url='/login/auth0')
def deleteFriend(request, id):
    currentFriend = Friend.objects.filter(userOne=id, userTwo=request.user.id)
    if (currentFriend.exists()):
        currentFriend.delete()

    currentFriend = Friend.objects.filter(userOne=request.user.id, userTwo=id)
    if (currentFriend.exists()):
        currentFriend.delete()

    return redirect('friends')

@login_required(login_url='/login/auth0')
def room(request, room):
    username = request.user.email
    room_details = Room.objects.get(name=room)
    return render(request, 'homeapp/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })

@login_required(login_url='/login/auth0')
def checkview(request, roomName):
    room = roomName
    username = request.user.email

    if Room.objects.filter(name=room).exists():
        return redirect('/friends/chat/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/friends/chat/'+room+'/?username='+username)
    
@login_required(login_url='/login/auth0')
def send(request):
    message = request.POST['message']
    username = request.user.email
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id, date=datetime.now())
    new_message.save()
    return HttpResponse('Message sent successfully')

@login_required(login_url='/login/auth0')
def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})
