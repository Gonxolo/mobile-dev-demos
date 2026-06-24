"""
Rutas de la app `recetas`.

/                    -> lista de recetas, con filtro opcional por categoría
/receta/<slug>/      -> detalle: ingredientes (con conversión y escalado en
                        vivo vía JavaScript) y pasos de preparación
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_recetas, name="lista_recetas"),
    path("receta/<slug:slug>/", views.receta_detalle, name="receta_detalle"),
    path("offline/", views.offline, name="offline"),
]
