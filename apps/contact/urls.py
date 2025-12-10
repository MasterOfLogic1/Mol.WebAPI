from django.urls import path
from .views import general_contact

urlpatterns = [
    path('general-contact/', general_contact, name='general-contact'),
]

