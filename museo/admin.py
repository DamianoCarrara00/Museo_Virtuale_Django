from django.contrib import admin
from .models import Autore, Tema, Sala, Opera

# Registriamo tutti i modelli per renderli visibili nell'admin
admin.site.register(Autore)
admin.site.register(Tema)
admin.site.register(Sala)
admin.site.register(Opera)