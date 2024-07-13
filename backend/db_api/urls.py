from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.UserView.as_view()),
    path('driver/', views.DriverView.as_view()),
    path('language/', views.LanguageListView.as_view()),
    path('trip/', views.TripView.as_view()),
    path('review/', views.ReviewView.as_view()),
]
