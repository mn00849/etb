from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

import requests
import uuid
from datetime import datetime

from .models import User, UserBudget, Routes, carShare, Friend, Room, Message
from .forms import BudgetSetterForm, RoutePlannerForm

class MainTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # creating a test team
        user = User(email="steve@gmail.com", username="steve")
        user.set_password('Password123')
        user.save()

        client = Client()

        client.login(username=user.username, password="Password123")

    def testHomepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Welcome to the EcoTravelBudgetter app')

    def testContact(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
    
        self.assertContains(response, 'Contact Us')

    # testing if user can login
    def testLogin(self):
        login = self.client.login(username='steve', password='Password123') 
        self.assertTrue(login)

    # testing budget setter form
    def testBudgetSetForm(self):
        login = self.client.login(username='steve', password='Password123') 
        user = User.objects.filter(email='steve@gmail.com').first()

        data = {
            "car": "Volkswagen Golf",
            "budget": "100",
            "mpg": "50",
            "endDate": "12/08/2023",
        }

        form = BudgetSetterForm(data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse('budget'), data)
        self.assertEqual(response.status_code, 200)

    # testing if budget page loads with budget that has been set
    def testBudgetPage(self):
        login = self.client.login(username='steve', password='Password123')

        # getting the current user
        user = User.objects.filter(username='steve').first()

        # creating a budget
        budget = UserBudget(userID=user, car="Volkswagen Golf", fuelType="", budget=100, mpg=50, startDate="2023-05-15", endDate="2023-08-12")
        budget.save()

        response = self.client.get(reverse('budget'))
        self.assertEqual(response.status_code, 200)
    
        self.assertContains(response, '£100')

    # testing budget boundaries
    def testBudgetBoundary(self):
        login = self.client.login(username='steve', password='Password123')

        # getting the current user
        user = User.objects.filter(username='steve').first()

        # checking if budget can be smaller than 0
        budget = UserBudget(userID=user, car="Volkswagen Golf", fuelType="", budget=-100, mpg=50, startDate="2023-05-15", endDate="2023-08-12")
        budget.save()
        self.assertRaises(ValidationError, budget.full_clean)

        # checking if mpg can be smaller than 0
        budget = UserBudget(userID=user, car="Volkswagen Golf", fuelType="", budget=100, mpg=-50, startDate="2023-05-15", endDate="2023-08-12")
        budget.save()
        self.assertRaises(ValidationError, budget.full_clean)

    # test current routes page loads
    def testRoutesPage(self):

        # checking if the page doesn't load if not logged in
        response = self.client.get(reverse('routes'))
        self.assertFalse(response.status_code == 200)

        login = self.client.login(username='steve', password='Password123')
        response = self.client.get(reverse('routes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A page to see your current routes, add new routes and remove routes.")

    # test routes form
    def testRoutesForm(self):
        login = self.client.login(username='steve', password='Password123')

        # checking if redirect if no userbudget exists
        response = self.client.get(reverse('routeplanner'))
        self.assertFalse(response.status_code == 200)

        data = {
            "origin": "Guildford",
            "endpoint": "Woking",
            "date": "09/25/2023",
            "friends": "",
        }

        form = RoutePlannerForm(data)
        self.assertTrue(form.is_valid())


        response = self.client.post(reverse('routes'), data)
        self.assertEqual(response.status_code, 200)

        # testing with invalid data
        data = {
            "origin": "",
            "endpoint": "Woking",
            "date": "09/25/2023",
            "friends": "",
        }

        form = RoutePlannerForm(data)
        self.assertFalse(form.is_valid())

        data = {
            "origin": "Guildford",
            "endpoint": "",
            "date": "09/25/2023",
            "friends": "",
        }

        form = RoutePlannerForm(data)
        self.assertFalse(form.is_valid())
        
        data = {
            "origin": "Guildford",
            "endpoint": "Woking",
            "date": "2023-09-25",
            "cost": 0.05,
            "emissions": 0.4,
            "transportType": 1,
        }

        currentUser = User.objects.get(email="steve@gmail.com")
        route = Routes(userID=currentUser, origin=data["origin"], destination=data["endpoint"], date=data["date"], cost=data["cost"], emissions=data["emissions"], transportType=data["transportType"])
        route.save()

        response = self.client.get(reverse('routes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guildford")
        self.assertContains(response, "Woking")

        # test deletion of route
        routeDel = Routes.objects.get(id=route.id)
        routeDel.delete()
        response = self.client.get(reverse('routes'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Guildford")
        self.assertNotContains(response, "Woking")

    # test route map viewer page loads
    def testRouteMapPage(self):

        # creating a dummy route
        data = {
            "origin": "Guildford",
            "endpoint": "Woking",
            "date": "2023-09-25",
            "cost": 0.05,
            "emissions": 0.4,
            "transportType": 1,
        }

        currentUser = User.objects.get(email="steve@gmail.com")

        route = Routes(userID=currentUser, origin=data["origin"], destination=data["endpoint"], date=data["date"], cost=data["cost"], emissions=data["emissions"], transportType=data["transportType"])
        route.save()

        # checking if the page doesn't load if not logged in
        response = self.client.get('/route/show/'+str(route.id))
        self.assertFalse(response.status_code == 200)

        login = self.client.login(username='steve', password='Password123')
        response = self.client.get('/route/show/'+str(route.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Route")
        self.assertContains(response, "Guildford")
        self.assertContains(response, "Woking")

        # creating a new user
        user = User(email="jack@gmail.com", username="jack")
        user.set_password('Password123')
        user.save()

        # checking a user cannot access another user's route
        login = self.client.login(username='jack', password='Password123')
        response = self.client.get('/route/show/'+str(route.id))
        self.assertFalse(response.status_code == 200)

    # testing car share
    def testCarShare(self):
        login = self.client.login(username='steve', password='Password123')

        # creating a new user
        user = User(email="jack@gmail.com", username="jack")
        user.set_password('Password123')
        user.save()

        # creating a dummy route
        data = {
            "origin": "Guildford",
            "endpoint": "Woking",
            "date": "2023-09-25",
            "cost": 0.05,
            "emissions": 0.4,
            "transportType": 1,
        }

        currentUser = User.objects.get(email="steve@gmail.com")
        route = Routes(userID=currentUser, origin=data["origin"], destination=data["endpoint"], date=data["date"], cost=data["cost"], emissions=data["emissions"], transportType=data["transportType"])
        route.save()

        # adding a user to the current route
        share = carShare(userID=2, routeID=route)
        share.save()

        # loading the routes page to see if friend is included there
        response = self.client.get(reverse('routes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "jack@gmail.com")

        route.delete()

        response = self.client.get(reverse('routes'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "jack@gmail.com")

    # testing friends page
    def testFriendsPage(self):
        login = self.client.login(username='steve', password='Password123')
        currentUser = User.objects.get(email="steve@gmail.com")

        response = self.client.get(reverse('friends'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Friends")
        self.assertContains(response, "Your friends:")

        # adding a dummy friend
        user = User(email="jack@gmail.com", username="jack")
        user.set_password('Password123')
        user.save()

        friend = Friend(userOne=currentUser.id, userTwo=user.id)
        friend.save()

        response = self.client.get(reverse('friends'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Friends")
        self.assertContains(response, "Your friends:")
        self.assertContains(response, "jack@gmail.com")

        # removing friend
        friend.delete()

        response = self.client.get(reverse('friends'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Friends")
        self.assertContains(response, "Your friends:")
        self.assertNotContains(response, "jack@gmail.com")
    
    # loading friends chat list
    def testFriendChatList(self):
        login = self.client.login(username='steve', password='Password123')
        currentUser = User.objects.get(email="steve@gmail.com")

        # adding a dummy friend
        user = User(email="jack@gmail.com", username="jack")
        user.set_password('Password123')
        user.save()

        friend = Friend(userOne=currentUser.id, userTwo=user.id)
        friend.save()

        response = self.client.get(reverse('chatlist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chat with friends")
        self.assertContains(response, "Select a friend to chat to")
        self.assertContains(response, "jack@gmail.com")
    
    # loading chat room
    def testChatroom(self):
        login = self.client.login(username='steve', password='Password123')
        currentUser = User.objects.get(email="steve@gmail.com")

        # adding a dummy friend
        user = User(email="jack@gmail.com", username="jack")
        user.set_password('Password123')
        user.save()

        friend = Friend(userOne=currentUser.id, userTwo=user.id)
        friend.save()

        # getting the chatroom name
        names = sorted([currentUser.email, user.email])
        roomName = uuid.uuid5(uuid.NAMESPACE_X500, names[0]+ "|" + names[1])

        # creating the room
        room = Room(name=roomName)
        room.save()

        response = self.client.get('/friends/chat/'+str(roomName)+'/?username='+currentUser.email)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"Chatroom")

        # sending a message
        message = Message(value="Hi Jack!", user=currentUser.email, room=roomName)
        message.save()
        
    # Data Analytics Page
    def testDataAnalytics(self):
        login = self.client.login(username='steve', password='Password123')

        response = self.client.get(reverse('stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Data Analytics")
        self.assertContains(response, "Sorry, there are not enough routes to show any data for the cost per route for the current month.")