"""
Vistas de la app `recetas`.

`receta_detalle` no hace la conversión de unidades ni el escalado de
porciones en el servidor: le entrega al navegador, como JSON embebido,
los datos crudos de cada ingrediente (cantidad, unidad, tipo de unidad
y factor respecto de la unidad base) más el catálogo de unidades por
tipo. Es JavaScript (`recetas.js`) quien recalcula todo al vuelo cuando
el usuario cambia el número de porciones o el sistema de unidades, sin
ir de nuevo al servidor.
"""

from django.shortcuts import get_object_or_404, render

from .models import Receta, Unidad


def lista_recetas(request):
    categoria = request.GET.get("categoria", "")
    busqueda = request.GET.get("q", "").strip()

    recetas = Receta.objects.all()
    if categoria:
        recetas = recetas.filter(categoria=categoria)
    if busqueda:
        recetas = recetas.filter(nombre__icontains=busqueda)

    return render(
        request,
        "recetas/lista.html",
        {
            "recetas": recetas,
            "categorias": Receta.CATEGORIA_CHOICES,
            "categoria_actual": categoria,
            "busqueda": busqueda,
        },
    )


def receta_detalle(request, slug):
    receta = get_object_or_404(Receta, slug=slug)
    ingredientes = receta.ingredientes.select_related("unidad")

    ingredientes_json = [
        {
            "nombre": ing.nombre,
            "nota": ing.nota,
            "cantidad": float(ing.cantidad),
            "unidad_codigo": ing.unidad.codigo,
            "tipo": ing.unidad.tipo,
        }
        for ing in ingredientes
    ]

    unidades_por_tipo = {}
    for unidad in Unidad.objects.filter(tipo__in=[Unidad.VOLUMEN, Unidad.MASA]):
        unidades_por_tipo.setdefault(unidad.tipo, []).append(
            {
                "codigo": unidad.codigo,
                "nombre": unidad.nombre,
                "abreviatura": unidad.abreviatura,
                "factor_base": float(unidad.factor_base),
            }
        )
    unidades_simples = {
        u.codigo: {"abreviatura": u.abreviatura, "nombre": u.nombre}
        for u in Unidad.objects.filter(tipo=Unidad.UNIDAD)
    }

    datos_js = {
        "ingredientes": ingredientes_json,
        "unidadesPorTipo": unidades_por_tipo,
        "unidadesSimples": unidades_simples,
        "porcionesBase": receta.porciones_base,
    }

    return render(
        request,
        "recetas/detalle.html",
        {
            "receta": receta,
            "datos_js": datos_js,
        },
    )


def offline(request):
    """Página mostrada por el service worker cuando no hay conexión ni caché."""
    return render(request, "recetas/offline.html")


def manifest(request):
    """Sirve el manifest.json en la raíz del sitio (requerido para instalar la PWA)."""
    return render(request, "recetas/manifest.json", content_type="application/manifest+json")


def service_worker(request):
    """
    Sirve el service worker en la raíz del sitio. Al vivir en '/' (y no en
    /static/), su scope cubre toda la app, no solo los archivos estáticos.
    """
    response = render(request, "recetas/service-worker.js", content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response
