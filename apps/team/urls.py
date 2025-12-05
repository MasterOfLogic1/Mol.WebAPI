from django.urls import path
from .views import list_team_members, get_team_member, create_team_member, update_team_member, delete_team_member

urlpatterns = [
    path('', list_team_members, name='list-team-members'),
    path('<int:member_id>/', get_team_member, name='get-team-member'),
    path('create/', create_team_member, name='create-team-member'),
    path('<int:member_id>/update/', update_team_member, name='update-team-member'),
    path('<int:member_id>/delete/', delete_team_member, name='delete-team-member'),
]

