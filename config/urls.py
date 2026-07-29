from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Brand Django Admin
admin.site.site_header = "LexVision AI Administration"
admin.site.site_title = "LexVision AI Legal Tech"
admin.site.index_title = "Contract Intelligence Platform Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.documents.urls')),
    path('', include('apps.analysis.urls')),
    path('', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)