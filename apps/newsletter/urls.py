from django.urls import path
from .views import register_newsletter, verify_newsletter

urlpatterns = [
    path('register/', register_newsletter, name='register-newsletter'),
    path('verify/<str:verification_token>/', verify_newsletter, name='verify-newsletter'),
]

