from django.urls import path
from .views import list_all_users, block_user, user_statistics

urlpatterns = [
    path('users/', list_all_users, name='list-all-users'),
    path('users/<int:user_id>/block/', block_user, name='block-user'),
    path('users/statistics/', user_statistics, name='user-statistics'),
]

