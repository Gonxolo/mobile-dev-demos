"""
Modelos de la app `recetas`.

La idea central de este proyecto: un ingrediente se guarda con una
**cantidad** y una **unidad**, y la unidad sabe a qué "familia" de
medidas pertenece (volumen, masa o unidad simple) y cuánto vale en la
unidad base de su familia (`factor_base`). Eso permite convertir entre
unidades automáticamente, pero **solo cuando tiene sentido**: mililitros
y tazas se pueden convertir entre sí (ambas son volumen), pero gramos y
tazas no, porque convertir volumen a masa requiere conocer la densidad
de cada ingrediente (no es lo mismo una taza de harina que una taza de
miel), y eso queda fuera del alcance de esta demo.
"""

from decimal import Decimal

from django.db import models
from django.urls import reverse


class Unidad(models.Model):
    """
    Una unidad de medida (ej: gramo, taza, cucharada).

    `tipo` agrupa las unidades en familias intercambiables entre sí.
    `factor_base` indica cuánto vale 1 de esta unidad expresado en la
    unidad base de su familia (ml para volumen, g para masa, 1 para
    unidades simples como "diente" o "unidad").
    """

    VOLUMEN = "volumen"
    MASA = "masa"
    UNIDAD = "unidad"
    TIPO_CHOICES = [
        (VOLUMEN, "Volumen (base: mililitro)"),
        (MASA, "Masa (base: gramo)"),
        (UNIDAD, "Unidad simple (no convertible)"),
    ]

    codigo = models.SlugField(
        max_length=20, unique=True, help_text="Identificador corto, ej: 'taza'."
    )
    nombre = models.CharField(max_length=40, help_text="Nombre legible, ej: 'taza'.")
    abreviatura = models.CharField(max_length=10, help_text="Ej: 'tz', 'cda', 'g'.")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    factor_base = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("1"),
        help_text="Cuánto vale 1 unidad de esta medida en la unidad base de su tipo.",
    )
    orden = models.PositiveSmallIntegerField(
        default=0, help_text="Orden de aparición en los selectores (menor a mayor)."
    )

    class Meta:
        ordering = ["tipo", "orden"]

    def __str__(self):
        return self.nombre

    def es_convertible(self):
        return self.tipo != Unidad.UNIDAD


class Receta(models.Model):
    """Una receta chilena, con sus pasos y porciones de referencia."""

    ENTRADA = "entrada"
    FONDO = "fondo"
    POSTRE = "postre"
    BEBESTIBLE = "bebestible"
    PAN_MASA = "pan_masa"
    CATEGORIA_CHOICES = [
        (ENTRADA, "Entrada"),
        (FONDO, "Plato de fondo"),
        (POSTRE, "Postre"),
        (BEBESTIBLE, "Bebestible"),
        (PAN_MASA, "Pan y masas"),
    ]

    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    emoji = models.CharField(
        max_length=8, default="🍽️", help_text="Emoji decorativo para la tarjeta de la receta."
    )
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default=FONDO)
    porciones_base = models.PositiveSmallIntegerField(
        default=4, help_text="Número de porciones al que corresponden las cantidades guardadas."
    )
    tiempo_preparacion_min = models.PositiveSmallIntegerField(
        help_text="Tiempo total estimado de preparación, en minutos."
    )
    pasos = models.TextField(
        help_text="Un paso por línea. Se muestran como una lista numerada."
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("receta_detalle", args=[self.slug])

    def lista_pasos(self):
        return [p.strip() for p in self.pasos.splitlines() if p.strip()]


class Ingrediente(models.Model):
    """Un ingrediente de una receta, con su cantidad en una unidad dada."""

    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="ingredientes")
    nombre = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, related_name="ingredientes")
    nota = models.CharField(
        max_length=80, blank=True, help_text="Ej: 'a gusto', 'opcional', 'picada finamente'."
    )
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "id"]

    def __str__(self):
        return f"{self.cantidad} {self.unidad.abreviatura} de {self.nombre}"

    def cantidad_en_unidad_base(self):
        """Cantidad expresada en la unidad base del tipo (ml, g, o unidad)."""
        return self.cantidad * self.unidad.factor_base
