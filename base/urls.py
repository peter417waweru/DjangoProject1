from django.urls import path
from . import views

urlpatterns =  [
    path('login/', views.LoginPage, name="login"),
    path('logout/', views.LogoutPage, name="logout"),
    path('signup/', views.SignupPage, name='signup'), 
    path('', views.home, name="home"),
    path('room/<int:pw>/', views.room, name="room"),

    path('profile/<str:pw>/', views.userProfile, name="user-profile"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pw>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pw>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pw>/', views.deleteMessage, name="delete-message")
]