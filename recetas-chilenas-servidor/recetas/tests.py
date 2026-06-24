from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Ingrediente, Receta, Unidad


class ConversionUnidadesTests(TestCase):
    """La idea central de la app: convertir solo dentro de la misma familia."""

    def setUp(self):
        self.g = Unidad.objects.create(
            codigo="g", nombre="gramo", abreviatura="g", tipo=Unidad.MASA, factor_base=Decimal("1")
        )
        self.kg = Unidad.objects.create(
            codigo="kg", nombre="kilogramo", abreviatura="kg", tipo=Unidad.MASA, factor_base=Decimal("1000")
        )
        self.taza = Unidad.objects.create(
            codigo="taza", nombre="taza", abreviatura="tz", tipo=Unidad.VOLUMEN, factor_base=Decimal("250")
        )

    def test_unidades_de_la_misma_familia_son_convertibles(self):
        self.assertTrue(self.g.es_convertible())
        self.assertEqual(self.g.tipo, self.kg.tipo)

    def test_unidad_simple_no_es_convertible(self):
        unidad_simple = Unidad.objects.create(
            codigo="un", nombre="unidad", abreviatura="un", tipo=Unidad.UNIDAD, factor_base=Decimal("1")
        )
        self.assertFalse(unidad_simple.es_convertible())

    def test_cantidad_en_unidad_base(self):
        receta = Receta.objects.create(
            nombre="Receta de prueba", slug="receta-de-prueba", tiempo_preparacion_min=10, pasos="Paso 1"
        )
        ingrediente = Ingrediente.objects.create(
            receta=receta, nombre="harina", cantidad=Decimal("2"), unidad=self.kg
        )
        self.assertEqual(ingrediente.cantidad_en_unidad_base(), Decimal("2000"))


class VistasTests(TestCase):
    def setUp(self):
        self.unidad = Unidad.objects.create(
            codigo="g", nombre="gramo", abreviatura="g", tipo=Unidad.MASA, factor_base=Decimal("1")
        )
        self.receta = Receta.objects.create(
            nombre="Sopaipillas",
            slug="sopaipillas",
            tiempo_preparacion_min=30,
            pasos="Amasa\nFrita",
            porciones_base=10,
        )
        Ingrediente.objects.create(
            receta=self.receta, nombre="harina", cantidad=Decimal("500"), unidad=self.unidad
        )

    def test_lista_recetas_responde_200(self):
        response = self.client.get(reverse("lista_recetas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sopaipillas")

    def test_filtro_por_categoria(self):
        response = self.client.get(reverse("lista_recetas"), {"categoria": Receta.POSTRE})
        self.assertNotContains(response, "Sopaipillas")

    def test_detalle_receta_incluye_datos_json(self):
        response = self.client.get(self.receta.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "datos-receta")
        self.assertContains(response, "harina")

    def test_manifest_y_service_worker_responden(self):
        self.assertEqual(self.client.get("/manifest.json").status_code, 200)
        self.assertEqual(self.client.get("/service-worker.js").status_code, 200)

    def test_lista_pasos_separa_por_linea(self):
        self.assertEqual(self.receta.lista_pasos(), ["Amasa", "Frita"])
