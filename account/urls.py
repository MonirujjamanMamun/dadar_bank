from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.UserRegistetionsViews.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileUpdateView.as_view(), name="profile"),
]
