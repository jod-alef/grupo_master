from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path
from raqs import views

urlpatterns = [
    path("", views.dashboard_redirect, name="index"),
    path("admin/", admin.site.urls),
    path(
        "update-ensaio-choices/",
        views.update_ensaio_choices,
        name="update-ensaio-choices",
    ),
    path("cadastro-soldador/", views.cadastro_soldador, name="cadastro-soldador"),
    path(
        "solicitacao-qualificacao-soldador/<int:soldador_id>/",
        views.solicitacao_qualificacao_soldador,
        name="solicitacao-qualificacao-soldador",
    ),
    path("list-soldadores/", views.list_soldadores, name="list-soldadores"),
    path("update-metal-fields/", views.update_metal_fields, name="update-metal-fields"),
    path(
        "update-progressao/", views.update_progressao_choices, name="update-progressao"
    ),
    # path('update-gas-protec/', views.update_gas_protecao, name='update-gas-protecao'),
    path("dashboard/", views.empresa_dashboard, name="empresa-dashboard"),
    path("verificar-cpf/", views.verificar_cpf_htmx, name="verificar-cpf"),
    path("login/", views.custom_login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "solicitacoes-soldador/<int:soldador_id>/",
        views.solicitacoes_soldador,
        name="solicitacoes-soldador",
    ),
    path(
        "apagar-solicitacao/<int:solicitacao_id>/",
        views.apagar_solicitacao,
        name="apagar-solicitacao",
    ),
    path(
        "update-consumivel-classificacao/",
        views.update_consumivel_classificacao,
        name="update-consumivel-classificacao",
    ),
    path("master-dashboard/", views.master_dashboard, name="master_dashboard"),
    path("raqs/criar/<int:empresa_id>/", views.criar_raqs, name="criar_raqs"),
    path(
        "raqs/<int:raqs_id>/adicionar/",
        views.adicionar_solicitacao_raqs,
        name="adicionar_solicitacao_raqs",
    ),
    path("raqs/<int:raqs_id>/fechar/", views.fechar_raqs, name="fechar_raqs"),
    path("raqs/<int:raqs_id>/", views.raqs_detail, name="raqs_detail"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
