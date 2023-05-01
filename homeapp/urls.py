from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('logout/', views.logout, name='logout'),
    path('routeplanner/', views.routeplanner, name="routeplanner"),
    path('budget', views.budget, name='budget'),
    path('friends', views.friends, name='friends'),
    path('user', views.user, name='user'),
    path('chat', views.chat, name='chat')
]