"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# TapTogetherBackend/config/urls.py

from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported here
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Include URLs from your 'bills_api' app under the '/api/' path
    path('api/', include('bills_api.urls')),
]

# ONLY FOR DEVELOPMENT: Serve media files (like your uploaded bill images)
# In production, you would use a dedicated web server (like Nginx) or a cloud storage service (like AWS S3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)