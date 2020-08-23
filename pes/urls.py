from django.urls import path 
from . import views

app_name ='pes'

urlpatterns = [
    path('', views.home , name ='home'),
    path('add/', views.add_match , name ='add_match'),
    path('edit/', views.edit_match , name ='edit_match'),
    path('matches/', views.matches , name ='matches'),
   

    ]
    
