from django.urls import path
from .views import user_profile, get_user_by_username

urlpatterns = [
    path('user/profile/', user_profile, name="user-profile"),
    path('user/<str:username>/', get_user_by_username, name="get-user-by-username"),
]
