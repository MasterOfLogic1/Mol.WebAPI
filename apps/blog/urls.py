from django.urls import path
from .views import list_blog_posts, get_blog_post, create_blog_post, update_blog_post, delete_blog_post

urlpatterns = [
    path('', list_blog_posts, name='list-blog-posts'),
    path('<int:post_id>/', get_blog_post, name='get-blog-post'),
    path('create/', create_blog_post, name='create-blog-post'),
    path('<int:post_id>/update/', update_blog_post, name='update-blog-post'),
    path('<int:post_id>/delete/', delete_blog_post, name='delete-blog-post'),
]

