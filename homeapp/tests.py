from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import User, UserBudget
from .forms import BudgetSetterForm

class MainTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # creating a test team
        user = User(username="steve", email="steve@gmail.com")
        user.set_password('Password123')
        user.save()

        client = Client()

        client.login(username=user.username, password="Password123")

    def test_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Welcome to the EcoTravelBudgetter app')

    def test_contact(self):
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
        user = User.objects.filter(username='steve').first()

        # getting the count of budgets before
        budgetNum = UserBudget.objects.all().count()

        data = {
            "car": "Volkswagen Golf",
            "budget": "100",
            "mpg": "50",
            "endDate": "12/08/2023",
        }

        form = BudgetSetterForm(data)
        self.assertTrue(form.is_valid())

        # getting the count of budgets after form is submitted
        budgetNumAfter = UserBudget.objects.all().count()

        response = self.client.post(reverse('budget'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(budgetNum, budgetNumAfter)

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