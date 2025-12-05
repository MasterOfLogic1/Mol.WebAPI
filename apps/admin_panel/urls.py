from django.urls import path
from .views import list_all_users, block_user, user_statistics, update_user_password, get_user

urlpatterns = [
    path('users/', list_all_users, name='list-all-users'),
    path('users/get/', get_user, name='get-user'),
    path('users/<int:user_id>/block/', block_user, name='block-user'),
    path('users/<int:user_id>/password/', update_user_password, name='update-user-password'),
    path('users/statistics/', user_statistics, name='user-statistics'),
]

