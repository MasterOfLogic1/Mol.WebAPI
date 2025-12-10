from django.urls import path, include
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.account.urls')),
    path('api/user-profile/', include('apps.user_profile.urls')),
    path('api/course/', include('apps.course.urls')),
    path('api/blog/', include('apps.blog.urls')),
    path('api/team/', include('apps.team.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/newsletter/', include('apps.newsletter.urls')),
    path('api/contact/', include('apps.contact.urls')),
    # OpenAPI schema:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc:
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
