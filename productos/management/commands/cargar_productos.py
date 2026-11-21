from django.core.management.base import BaseCommand
from productos.models import Categoria, Producto

PRODUCTOS = [
    ('Torta de Chocolate', 25000, 10, 'Tortas', 'https://www.solopostres.com/wp-content/uploads/2025/06/Torta-humeda-de-chocolate-casera-800x800.jpg', "Deliciosa torta de chocolate negro 70% cacao, con relleno de ganache y cubierta de crema batida. Perfecta para celebraciones."),
    ('Cheesecake de Frutos Rojos', 22000, 5, 'Tartas', 'https://acdn-us.mitiendanube.com/stores/002/284/314/products/53db5631-8acc-4816-85ca-02f251c3d33b-926ede26531a80b24417087259126029-480-0.webp', "Cremoso cheesecake sobre base de galleta, cubierto con abundantes frutos rojos frescos."),
    ('Caja de alfajores de Maicena', 8500, 20, 'Alfajores', 'https://acdn-us.mitiendanube.com/stores/003/312/466/products/maicena-11-9411075d3dc62d64b216876162881640-1024-1024.webp', "Los clásicos alfajorcitos de maicena, bien rellenos de dulce de leche y con coco rallado por los bordes."),
    ('Tarta de Manzana', 16000, 6, 'Tartas', 'https://content-cocina.lecturas.com/medio/2018/07/19/tarta-de-manzana-rellena_8bdd481e_800x800.jpg', "Tarta tradicional de manzana con masa quebrada, relleno de manzanas caramelizadas y toque de canela."),
    ('Pastafrola de Membrillo', 10000, 12, 'Tartas', 'https://www.revistagente.com/wp-content/uploads/2026/03/pastafrola-620x464.jpg.webp', "Pastafrola casera como la de la abuela, con masa quebradiza de vainilla y mucho membrillo. Ideal para acompañar con unos mates."),
    ('Caja de Masitas Finas', 9500, 15, 'Galletas', 'https://acdn-us.mitiendanube.com/stores/001/181/412/products/masas1kg1-7a6ddf55715e16405217580719279071-640-0.webp', "Medio kilo de masitas secas surtidas: palmeritas, pepas, vainillas, mantecadas y más. Nunca pueden faltar."),
    ('Rogel de Dulce de Leche', 15000, 3, 'Tortas', 'https://cdn.cookwithbelula.com/receta/rogel/rogel-4x3.webp', "Torre de capas crocantes de masa fina con abundande dulce de leche repostero y cubierto de merengue italiano. Un clásico de los cumpleaños."),
    ('Chocotorta', 32000, 15, 'Tortas', 'https://www.annarecetasfaciles.com/files/chocotorta-1-1-1024x575.jpg', "La chocotorta de toda la vida, con galletitas de chocolate, dulce de leche y crema. Bien fresquita, ideal para los más chicos."),
    ('Torta Balcarce', 20500, 6, 'Tortas', 'https://imgs.search.brave.com/WKKP_7PqqJPZg28zkOBljRd2qqhS6b3-q04RlhS1A9w/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/ZWxudWV2ZS5jb20u/YXIvc2l0ZXMvZGVm/YXVsdC9maWxlcy8y/MDIzLTEyL0JBTENB/UkNFJTIwUE9TVFJF/LnBuZw', "Postre nacional hecho con capas de bizcochuelo, dulce de leche, crema, merengue y castañas. ¡Un clásico de años!"),
    ('Pepas de Membrillo', 3000, 30, 'Galletas', 'https://imgs.search.brave.com/NbPUI3DlmNUKY35UDW8s3NOo_FEECofOQCGkWTKa1lY/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/Y3JvbmljYS5jb20u/YXIvZmlsZXMvaW1h/Z2UvMTY2MC8xNjYw/NzUxLzZhMGM1MmYx/OWZlY2VfOTkyXzU1/OCEuanBnP3M9NTc3/MmU4NmUxMWRjMGJl/YTY1ZWQyZDE3NTNk/ODk4ZWUmZD0xNzc5/MTU5NjAw', "Pepitas caseras de masa sableé con mucho membrillo en el centro y coco rallado."),
    ('Lemon Pie', 9500, 9, 'Tartas', 'https://www.annarecetasfaciles.com/files/lemon-pie-815x458.jpg', "Tarta de limón con masa sableé crocante, crema de limón bien ácida y merengue italiano tostado. Refrescante y livianito."),
    ('Torta Red Velvet', 14500, 5, 'Tortas', 'https://www.infobae.com/resizer/v2/52E6H6YM2NHAHHAR6S7SL47SEM.jpg?auth=297e571a58ee99c362d9f16fab0b2dafa6ffba5a019ccd898a7c4741312ce74f&smart=true&width=992&height=556&quality=85', "Torta red velvet de cuatro capas con frosting de queso crema, bien húmeda y suavecita. Decorada con frutos rojos frescos, un lujo."),
    ('Torta Selva Negra', 32000, 12, 'Tortas', 'https://www.nuria.com.ar/wp-content/uploads/2018/11/Confiteria-Nuria-2018-24.jpg', "Bizcochuelo de chocolate, crema chantilly, cerezas confitadas y virutas de chocolate. Un clásocp de las fiestas de fin de año."),
    ('Tarta de Frutillas con Crema', 19500, 3, 'Tartas', 'https://resizer.glanacion.com/resizer/v2/tarta-de-frutillas-con-crema-PYKAP3ZRK5BPFOHDRV4S7IPXEM.jpg?auth=e79c6ab37f8944ed7dd7512481aa99edb2437d1f2d32c519f3812ce90423b0e2&width=880&height=586&quality=70&smart=true', "Base de masa sableé rellena con crema chantilly y frutillas frescas de estación, con un toque de brillo de mermelada. Fresquita y tentadora."),
    ('Torta Tres Leches', 25000, 7, 'Tortas', 'https://cdn0.recetasgratis.net/es/posts/0/1/9/torta_tres_leches_8910_1200.jpg', "Bizcochuelo súper húmedo bañado en mezcla de tres leches, cubierto con crema batida y canela. Bien rendidora, para compartir en familia."),
]


class Command(BaseCommand):
    help = 'Carga los productos de ejemplo de la pastelería'

    def handle(self, *args, **options):
        for nombre, precio, stock, cat, imagen, descripcion in PRODUCTOS:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat)
            Producto.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'precio': precio,
                    'stock': stock,
                    'categoria': categoria,
                    'imagen': imagen,
                    'descripcion': descripcion,
                },
            )
        self.stdout.write(self.style.SUCCESS(f'{len(PRODUCTOS)} productos cargados'))