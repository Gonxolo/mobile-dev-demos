"""
Comando `python manage.py seed_demo`.

Crea el catálogo de unidades de medida y un puñado de recetas chilenas
de ejemplo, con ingredientes en distintas unidades, para que la demo no
se vea vacía y se pueda probar la conversión y el escalado de porciones.
Es idempotente: se puede correr varias veces sin duplicar datos.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from recetas.models import Ingrediente, Receta, Unidad

UNIDADES = [
    # codigo, nombre, abreviatura, tipo, factor_base (respecto a ml o g), orden
    ("ml", "mililitro", "ml", Unidad.VOLUMEN, "1", 1),
    ("cdta", "cucharadita", "cdta", Unidad.VOLUMEN, "5", 2),
    ("cda", "cucharada", "cda", Unidad.VOLUMEN, "15", 3),
    ("taza", "taza", "tz", Unidad.VOLUMEN, "250", 4),
    ("l", "litro", "L", Unidad.VOLUMEN, "1000", 5),
    ("g", "gramo", "g", Unidad.MASA, "1", 1),
    ("kg", "kilogramo", "kg", Unidad.MASA, "1000", 2),
    ("un", "unidad", "un", Unidad.UNIDAD, "1", 1),
    ("diente", "diente", "diente", Unidad.UNIDAD, "1", 2),
    ("pizca", "pizca", "pizca", Unidad.UNIDAD, "1", 3),
]

RECETAS = [
    {
        "nombre": "Empanadas de pino",
        "emoji": "🥟",
        "categoria": Receta.ENTRADA,
        "porciones_base": 12,
        "tiempo_preparacion_min": 90,
        "descripcion": "El clásico de las fiestas patrias: masa horneada rellena de pino de carne, cebolla, huevo y aceituna.",
        "pasos": [
            "Pica la cebolla en cuadritos pequeños y sofríela en aceite junto con el comino y el ají de color hasta que esté transparente.",
            "Agrega la carne molida, sazona con sal y pimienta, y cocina hasta que esté lista. Deja enfriar el pino.",
            "Forma discos de masa, rellena con pino, media aceituna, un trozo de huevo duro y una pasa.",
            "Cierra las empanadas en repulgue, pinta con huevo batido y hornea a 200°C por 25-30 minutos.",
        ],
        "ingredientes": [
            ("harina", "1", "kg", ""),
            ("manteca", "150", "g", "derretida"),
            ("agua tibia", "350", "ml", ""),
            ("carne de vacuno molida", "700", "g", ""),
            ("cebolla", "3", "un", "picada"),
            ("comino", "1", "cdta", ""),
            ("ají de color", "1", "cda", ""),
            ("huevo", "3", "un", "duros, para el relleno"),
            ("aceitunas", "12", "un", "sin carozo"),
            ("pasas", "1", "cdta", "opcional"),
            ("huevo", "1", "un", "batido, para pintar"),
        ],
    },
    {
        "nombre": "Pastel de choclo",
        "emoji": "🌽",
        "categoria": Receta.FONDO,
        "porciones_base": 6,
        "tiempo_preparacion_min": 75,
        "descripcion": "Pino de carne y pollo cubierto con un pastel dulzón de choclo molido, gratinado al horno.",
        "pasos": [
            "Prepara un pino igual que para empanadas, con carne, pollo desmenuzado, cebolla y especias.",
            "Licúa los choclos con leche y albahaca; cocina la mezcla a fuego lento con mantequilla hasta que espese.",
            "Distribuye el pino en una fuente, agrega medio huevo duro y una aceituna por porción.",
            "Cubre con la mezcla de choclo, espolvorea azúcar y hornea a 200°C hasta gratinar, unos 25 minutos.",
        ],
        "ingredientes": [
            ("choclo desgranado", "1.5", "kg", "puede ser congelado"),
            ("leche", "250", "ml", ""),
            ("albahaca fresca", "4", "un", "hojas"),
            ("mantequilla", "100", "g", ""),
            ("carne de vacuno molida", "500", "g", ""),
            ("pollo cocido desmenuzado", "300", "g", ""),
            ("cebolla", "2", "un", "picada"),
            ("huevo", "3", "un", "duros"),
            ("aceitunas", "6", "un", ""),
            ("azúcar", "2", "cda", "para espolvorear"),
        ],
    },
    {
        "nombre": "Sopaipillas",
        "emoji": "🍂",
        "categoria": Receta.PAN_MASA,
        "porciones_base": 20,
        "tiempo_preparacion_min": 40,
        "descripcion": "Masa frita de zapallo, perfecta para los días de lluvia con pebre o chancaca.",
        "pasos": [
            "Cocina el zapallo al vapor y hazlo puré sin agregar agua.",
            "Mezcla el puré tibio con harina, manteca, sal y polvos de hornear hasta lograr una masa lisa.",
            "Estira la masa y corta círculos; pincha cada uno al centro con un tenedor.",
            "Fríe en aceite caliente hasta que doren por ambos lados y escurre sobre papel absorbente.",
        ],
        "ingredientes": [
            ("zapallo", "400", "g", "cocido y hecho puré"),
            ("harina", "500", "g", ""),
            ("manteca", "50", "g", ""),
            ("polvos de hornear", "1", "cdta", ""),
            ("sal", "1", "pizca", ""),
            ("aceite", "500", "ml", "para freír"),
        ],
    },
    {
        "nombre": "Mote con huesillo",
        "emoji": "🍑",
        "categoria": Receta.BEBESTIBLE,
        "porciones_base": 4,
        "tiempo_preparacion_min": 30,
        "descripcion": "Bebida fría y dulce de verano hecha con huesillos remojados y mote de trigo cocido.",
        "pasos": [
            "Remoja los huesillos la noche anterior en agua con azúcar y canela.",
            "Cocina los huesillos remojados a fuego bajo en su misma agua hasta que estén blandos; deja enfriar el jugo.",
            "Cuece el mote de trigo en agua hasta que esté tierno y escúrrelo.",
            "Sirve el jugo frío con un par de huesillos y una cucharada de mote en cada vaso.",
        ],
        "ingredientes": [
            ("huesillos", "300", "g", "secos"),
            ("agua", "1.5", "l", ""),
            ("azúcar", "150", "g", ""),
            ("canela en rama", "1", "un", ""),
            ("mote de trigo", "200", "g", "cocido"),
        ],
    },
    {
        "nombre": "Leche asada",
        "emoji": "🍮",
        "categoria": Receta.POSTRE,
        "porciones_base": 8,
        "tiempo_preparacion_min": 60,
        "descripcion": "Postre horneado de leche, huevo y vainilla, similar al flan pero más firme y dorado por arriba.",
        "pasos": [
            "Bate los huevos con el azúcar hasta que blanqueen un poco.",
            "Agrega la leche, la vainilla y una pizca de sal, mezclando sin batir demasiado para no incorporar aire.",
            "Vierte en un molde enmantequillado y hornea a baño maría a 180°C por 45 minutos, hasta que cuaje.",
            "Deja enfriar y refrigera antes de servir, espolvoreada con canela.",
        ],
        "ingredientes": [
            ("leche", "1", "l", ""),
            ("huevo", "6", "un", ""),
            ("azúcar", "200", "g", ""),
            ("esencia de vainilla", "1", "cdta", ""),
            ("sal", "1", "pizca", ""),
            ("canela en polvo", "1", "cdta", "para espolvorear"),
        ],
    },
]


class Command(BaseCommand):
    help = "Crea unidades de medida y recetas chilenas de ejemplo (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        unidades_por_codigo = {}
        for codigo, nombre, abreviatura, tipo, factor, orden in UNIDADES:
            unidad, _ = Unidad.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "abreviatura": abreviatura,
                    "tipo": tipo,
                    "factor_base": Decimal(factor),
                    "orden": orden,
                },
            )
            unidades_por_codigo[codigo] = unidad
        self.stdout.write(self.style.SUCCESS(f"Unidades listas: {len(unidades_por_codigo)}"))

        total_recetas = 0
        for datos in RECETAS:
            receta, _ = Receta.objects.update_or_create(
                slug=slugify(datos["nombre"]),
                defaults={
                    "nombre": datos["nombre"],
                    "emoji": datos["emoji"],
                    "categoria": datos["categoria"],
                    "porciones_base": datos["porciones_base"],
                    "tiempo_preparacion_min": datos["tiempo_preparacion_min"],
                    "descripcion": datos["descripcion"],
                    "pasos": "\n".join(datos["pasos"]),
                },
            )
            receta.ingredientes.all().delete()
            for orden, (nombre, cantidad, codigo_unidad, nota) in enumerate(datos["ingredientes"]):
                Ingrediente.objects.create(
                    receta=receta,
                    nombre=nombre,
                    cantidad=Decimal(cantidad),
                    unidad=unidades_por_codigo[codigo_unidad],
                    nota=nota,
                    orden=orden,
                )
            total_recetas += 1

        self.stdout.write(self.style.SUCCESS(f"Recetas listas: {total_recetas}"))
