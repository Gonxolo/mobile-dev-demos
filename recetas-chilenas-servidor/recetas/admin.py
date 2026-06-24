from django.contrib import admin

from .models import Ingrediente, Receta, Unidad


class IngredienteInline(admin.TabularInline):
    model = Ingrediente
    extra = 1


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "porciones_base", "tiempo_preparacion_min")
    list_filter = ("categoria",)
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [IngredienteInline]


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura", "tipo", "factor_base", "orden")
    list_filter = ("tipo",)
