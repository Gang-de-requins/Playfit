from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, GoogleOAuthLoginView, DocsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include("social_django.urls", namespace="social")),
    path('google-login/', GoogleOAuthLoginView.as_view(), name='google-login'),
    path('docs/', DocsView.as_view(), name='docs'),
]