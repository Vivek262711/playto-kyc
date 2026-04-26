"""
Root URL configuration.
All API endpoints live under /api/v1/.
In production, serves the React SPA for all non-API routes.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/merchant/', include('kyc.urls_merchant')),
    path('api/v1/reviewer/', include('kyc.urls_reviewer')),
    path('api/v1/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve React SPA for all non-API routes (production)
# This must be LAST so it doesn't override API routes
if settings.FRONTEND_BUILD_DIR.exists():
    urlpatterns += [
        re_path(r'^(?!api/|admin/|static/|media/).*$',
                TemplateView.as_view(template_name='index.html'),
                name='spa-fallback'),
    ]
