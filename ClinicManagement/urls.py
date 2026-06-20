from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path('', include('home.urls')),
    path('bahikhata/', include('bahikhata.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# path('schema/', SpectacularAPIView.as_view(), name='schema'),
# path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
# path('docs/', SpectacularRedocView.as_view(url_name='schema'), name='docs'),