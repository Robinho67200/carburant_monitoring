"""
URL configuration for carburant_monitoring_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path

from main_app.views import index, recherche, station, departement, ville, region
from carburant_monitoring_web import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", index, name="index"),
    path("recherche/", recherche, name="recherche"),
    path("station/<str:id>", station, name="station"),
    path("departement/<str:id>", departement, name="departement"),
    path("ville/<str:id>", ville, name="ville"),
    path("region/<str:id>", region, name="region"),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
