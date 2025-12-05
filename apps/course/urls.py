from django.urls import path
from .views import list_courses, get_course, create_course, update_course, delete_course

urlpatterns = [
    path('', list_courses, name='list-courses'),
    path('<int:course_id>/', get_course, name='get-course'),
    path('create/', create_course, name='create-course'),
    path('<int:course_id>/update/', update_course, name='update-course'),
    path('<int:course_id>/delete/', delete_course, name='delete-course'),
]

