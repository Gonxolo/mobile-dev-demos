"""
Rutas principales del proyecto.

El manifest y el service worker se sirven en la raíz del sitio (no bajo
/static/) para que el service worker pueda controlar todas las páginas
de la app (su "scope" es la carpeta donde vive el archivo .js).
"""

from django.contrib import admin
from django.urls import include, path

from recetas import views as recetas_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("manifest.json", recetas_views.manifest, name="manifest"),
    path("service-worker.js", recetas_views.service_worker, name="service_worker"),
    path("", include("recetas.urls")),
]
