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
    path('route/delete/<int:id>', views.deleteRoute, name="deleteroute"),
    path('route/show/<int:id>', views.showRoute, name="showroute"),
    #broken
    path('budget', views.budget, name='budget'),
    path('friends', views.friends, name='friends'),
    path('friend/add', views.addFriend, name='addfriend'),
    path('friend/delete/<int:id>', views.deleteFriend, name='deletefriend'),
    path('user', views.user, name='user'),
    path('chatlist', views.chatlist, name='chatlist'),
    path('setbudget', views.set_budget, name='setbudget'),
    path('budget/delete', views.delete_budget, name='deletebudget'),
    path('friends/chat/<str:room>/', views.room, name='room'),
    path('friends/chat/checkview/<str:roomName>', views.checkview, name='checkview'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
]