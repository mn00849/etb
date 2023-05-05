from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('routeplanner/', views.routeplanner, name="routeplanner"),
    path('routes', views.routes, name="routes"),
    #broken
    path('budget', views.budget, name='budget'),
    path('friends', views.friends, name='friends'),
    path('user', views.user, name='user'),
    path('chat', views.chat, name='chat'),
    path('setbudget', views.set_budget, name='setbudget'),
    path('budget/delete', views.delete_budget, name='deletebudget')
]