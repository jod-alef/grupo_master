from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import *

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Soldador)
admin.site.register(SolicitacaoCadastroSoldador)
admin.site.register(EnsaioMecanicoDobramento)

