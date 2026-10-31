from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from evaluacion.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)