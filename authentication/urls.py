from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('home', views.home, name="home"),
    path('about', views.about, name="about"),
    path('services', views.services, name="services"),
    # path('contact', views.contact, name="contact"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
]