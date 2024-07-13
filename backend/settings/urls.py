from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # path('', include('custom_admin.urls')),
    path('admin/', admin.site.urls),
    path('admin_tools/', include('admin_tools.urls')),
    path('api/', include('db_api.urls')),
]
