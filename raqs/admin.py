from django.contrib import admin
from .forms import AdminEmpresaAdmin
from .models import *

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Soldador)
admin.site.register(SolicitacaoCadastroSoldador)
admin.site.register(EnsaioMecanicoDobramento)
admin.site.register(EnsaioUltrassom)
admin.site.register(Raqs)
admin.site.register(Operador, AdminEmpresaAdmin)
