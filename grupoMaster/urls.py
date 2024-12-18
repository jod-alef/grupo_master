from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from raqs import views

urlpatterns = [
    path('', views.empresa_dashboard, name='index'),
    path('admin/', admin.site.urls),
    path('update-ensaio-choices/', views.update_ensaio_choices, name='update-ensaio-choices'),
    path('cadastro-soldador/', views.cadastro_soldador, name='cadastro-soldador'),
    path('solicitacao-qualificacao-soldador/<int:soldador_id>/', views.solicitacao_qualificacao_soldador, name='solicitacao-qualificacao-soldador'),
    path('list-soldadores/', views.list_soldadores, name='list-soldadores'),
    path('update-metal-fields/', views.update_metal_fields, name='update-metal-fields'),
    path('update-progressao/', views.update_progressao_choices, name='update-progressao'),
    path('update-gas-protec/', views.update_gas_protecao, name='update-gas-protecao'),
    path('dashboard/', views.empresa_dashboard, name='empresa-dashboard'),
    path('verificar-cpf/', views.verificar_cpf_htmx, name='verificar-cpf'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)