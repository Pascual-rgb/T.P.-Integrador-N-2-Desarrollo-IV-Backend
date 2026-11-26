from django.contrib import admin
from .models import Mensaje

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'mensaje', 'creado', 'leido')
    search_fields = ('nombre', 'correo', 'mensaje')
    list_filter = ('creado', 'leido')