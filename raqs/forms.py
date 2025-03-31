from django import forms
from django.contrib.auth.admin import UserAdmin

from .models import (
    Empresa,
    Soldador,
    SolicitacaoCadastroSoldador,
    EnsaioMecanicoDobramento,
    EnsaioUltrassom,
    Raqs,
    Operador,
)


class BulmaMixin:
    def _apply_bulma_styles(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "textarea"})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "checkbox"})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "select"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bulma_styles()


class EmpresaForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "logo"]


class SoldadorForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = Soldador
        fields = ["nome", "cpf"]


class SolicitacaoCadastroSoldadorForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = SolicitacaoCadastroSoldador
        fields = [
            "eps",
            "norma_projeto",
            "sinete",
            "processo_soldagem",
            "consumivel_spec",
            "consumivel_classificacao",
            "consumivel_diametro",
            "metal_base_spec",
            "metal_base_espessura",
            "metal_base_diametro",
            "posicao_soldagem",
            "posicao_soldagem_progressao",
            "cobre_junta",
            "gas_protecao",
            "purga",
            "ensaio",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get("norma_projeto") == "AWS_D1-1":
            self.fields["ensaio"].choices = [("DOBRAMENTO", "Dobramento Mecânico")]

        metal_base_spec = self.initial.get(
            "metal_base_spec", self.data.get("metal_base_spec")
        )

        if metal_base_spec in ["A-36", "SB536", "A-309", "A-312"]:  # Para chapas
            # Permitir apenas METAL_BASE_ESPESSURA e limitar POSICAO_SOLDAGEM
            self.fields["metal_base_espessura"].widget.attrs.update({"required": True})
            self.fields["metal_base_espessura"].disabled = False
            self.fields["metal_base_diametro"].widget.attrs.update({"required": False})
            self.fields["metal_base_diametro"].disabled = True
            self.fields["posicao_soldagem"].choices = [
                choice
                for choice in self.fields["posicao_soldagem"].choices
                if choice[0] not in ["5G", "6G"]
            ]

        elif metal_base_spec in ["A-106", "16MO3"]:  # Para tubos
            # Permitir apenas METAL_BASE_DIAMETRO e limitar POSICAO_SOLDAGEM
            self.fields["metal_base_diametro"].widget.attrs.update({"required": True})
            self.fields["metal_base_diametro"].disabled = False
            self.fields["metal_base_espessura"].widget.attrs.update({"required": False})
            self.fields["metal_base_espessura"].disabled = True
            self.fields["posicao_soldagem"].choices = [
                choice
                for choice in self.fields["posicao_soldagem"].choices
                if choice[0] not in ["3G", "4G"]
            ]

        posicao_soldagem = self.data.get("posicao_soldagem")

        if posicao_soldagem in ["6G"]:
            self.fields["posicao_soldagem_progressao"].readonly = True
            self.fields["posicao_soldagem_progressao"].choices = [
                ("ASCENDENTE", "Ascendente")
            ]
        elif posicao_soldagem in ["3G", "3F", "5G"]:
            self.fields["posicao_soldagem_progressao"].choices = [
                ("ASCENDENTE", "Ascendente"),
                ("DESCENDENTE", "Descendente"),
            ]
        else:
            self.fields["posicao_soldagem_progressao"].readonly = True
            self.fields["posicao_soldagem_progressao"].choices = [("NA", "N/A")]

        processo_soldagem = self.data.get("processo_soldagem")

        if processo_soldagem in ["GTAW"]:
            self.fields["gas_protecao"].choices = [("ARGONIO", "Argônio")]
        elif processo_soldagem in ["GMAW"]:
            self.fields["gas_protecao"].choices = [("ARCO2", "Ar+CO²")]
        elif processo_soldagem in ["FCAW"]:
            self.fields["gas_protecao"].choices = [
                ("CO2", "CO²"),
            ]
        else:
            self.fields["gas_protecao"].choices = [("NA", "N/A")]

    def clean(self):
        cleaned_data = super().clean()
        metal_base_spec = cleaned_data.get("metal_base_spec")
        metal_base_espessura = cleaned_data.get("metal_base_espessura")
        metal_base_diametro = cleaned_data.get("metal_base_diametro")

        # Validate based on metal_base_spec
        if (
            metal_base_spec in ["A-36", "SB536", "A-309", "A-312"]
            and not metal_base_espessura
        ):
            self.add_error("metal_base_espessura", "Este campo é obrigatório.")
        if metal_base_spec in ["A-106", "16MO3"] and not metal_base_diametro:
            self.add_error("metal_base_diametro", "Este campo é obrigatório.")

        return cleaned_data


class EnsaioMecanicoDobramentoForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = EnsaioMecanicoDobramento
        fields = [
            "solicitacao",
            "fotos_amostra_1",
            "fotos_amostra_2",
            "fotos_amostra_3",
            "aprovado",
        ]


class EnsaioUltrassomForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = EnsaioUltrassom
        fields = ["solicitacao", "aprovado"]


class RaqsForm(BulmaMixin, forms.ModelForm):
    class Meta:
        model = Raqs
        fields = ["solicitacoes", "lista_de_verificacoes"]


class AdminEmpresaAdmin(UserAdmin):
    # Campos exibidos na lista do admin
    list_display = ("username", "email", "empresa", "is_staff", "is_active")
    list_filter = ("empresa", "is_staff", "is_active")

    # Campos do formulário de edição de usuários
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "email", "empresa")},
        ),
        (
            "Permissões",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Campos para o formulário de criação de usuários
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "empresa",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ("username", "email", "empresa__nome")
    ordering = ("username",)
