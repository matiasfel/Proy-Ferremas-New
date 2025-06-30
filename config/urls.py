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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Roots URLs
    path("",                include(('apps.landing.urls', 'landing'),               namespace='landing')),
    path("authentication/", include(('apps.authentication.urls', 'authentication'), namespace='authentication')),
    path("store/",          include(('apps.store.urls', 'store'),                   namespace='store')),
    path("users/",          include(("apps.users.urls", "users"),                   namespace="users")),
    path("admin_panel/",    include(("apps.admin_panel.urls", "admin_panel"),       namespace="admin_panel")),
    path("core/",           include(("apps.core.urls", "core"),                     namespace="core")),
]

#Only include the browser reload URLs if DEBUG is True
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)