"""
URL configuration for urbantrends_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('urbantrends_authentication.urls')),
    path('services/', include('urbantrends_services.urls')),
    path('dev_projects/', include('urbantrends_projects.urls')),
    path('clients/', include('client_projects.urls')),
    path('dash/projects/', include('dashboard_services.urls')),
    path('orders/', include('urbantrends_orders.urls')),
    path('blogs/', include('urbantrends_blogs.urls')),
    path('brands/', include('urbantrends_brands.urls')),
]
