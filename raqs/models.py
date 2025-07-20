from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Soldador(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)

    def clean(self):
        super().clean()
        if Soldador.objects.filter(cpf=self.cpf).exclude(pk=self.pk).exists():
            raise ValidationError({"cpf": "CPF já cadastrado."})

    class Meta:
        verbose_name = "Soldador"
        verbose_name_plural = "Soldadores"

    def __str__(self):
        return f"{self.nome}"


class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos")
    n_raqs = models.IntegerField()

    def __str__(self):
        return f"{self.nome}"


class AbstractEmpresaUser(AbstractUser):
    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.username} - ({self.empresa.nome if self.empresa else 'Sem empresa'})"


class Operador(AbstractEmpresaUser):
    setor = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"


class SolicitacaoCadastroSoldador(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
    sinete = models.CharField(max_length=10)
    data = models.DateField(auto_now=True)
    eps = models.CharField(max_length=10)
    NORMA_PROJETO_CHOICES = (
        ("ASME_I", "ASME I - 2023"),
        ("ASME_VII", "ASME VII Div.1/Div.2 - 2023"),
        ("ASME_B31-1", "ASME B31.1 - 2022"),
        ("ASME_B31-3", "ASME B31.3 - 2022"),
        ("ASME_B31-4", "ASME B31.4 - 2022"),
        ("ASME_B31-8", "ASME B31.8 - 2022"),
        ("API_620", "API 620 - 2021"),
        ("API_650", "API 650 - 2021"),
        ("AWS_D1-1", "AWS D1.1 - 2022"),
    )
    norma_projeto = models.CharField(max_length=10, choices=NORMA_PROJETO_CHOICES)
    PROCESSO_SOLDAGEM_CHOICES = (
        ("SMAW", "SMAW - Soldagem com eletrodo revestido"),
        ("GTAW", "GTAW - Soldagem TIG"),
        ("GMAW", "GMAW - Soldagem MIG"),
        ("FCAW", "FCAW - Soldagem com arame tubular"),
    )
    processo_soldagem = models.CharField(
        max_length=4, choices=PROCESSO_SOLDAGEM_CHOICES
    )

    CONSUMIVEL_SPEC_CHOICES = [
        ("SFA_5-1", "SFA 5.1"),
        ("SFA_5-4", "SFA 5.4"),
        ("SFA_5-9", "SFA 5.9"),
        ("SFA_5-14", "SFA 5.14"),
        ("SFA_5-11", "SFA 5.11"),
        ("SFA_5-18", "SFA 5.18"),
        ("SFA_5-20", "SFA 5.20"),
    ]
    consumivel_spec = models.CharField(max_length=15, choices=CONSUMIVEL_SPEC_CHOICES)

    CONSUMIVEL_CLASS_CHOICES = [
        ("E7018", "E7018"),
        ("E6010", "E6010"),
        ("E-71T-1", "E-71T-1"),
        ("E-309L", "E-309L"),
        ("ER-70S-3", "ER-70S-3"),
        ("ER-70S-6", "ER-70S-6"),
        ("ER-309L", "ER-309L"),
        ("ER-308L", "ER-308L"),
        ("ER-NiCrFe3", "ER-NiCrFe3"),
        ("E-NiCrFe3", "E-NiCrFe3"),
        ("ER-NiCrMo3", "E-NiCrMo3"),
    ]
    consumivel_classificacao = models.CharField(
        max_length=10, choices=CONSUMIVEL_CLASS_CHOICES
    )
    CONSUMIVEL_DIAMETRO_CHOICES = [("1.2", "1,2 mm"), ("3.2", "3,25 mm")]
    # GMAW | FCAW 1.2 - SMAW |GTAW 3.2
    consumivel_diametro = models.CharField(
        max_length=4, choices=CONSUMIVEL_DIAMETRO_CHOICES
    )

    METAL_BASE_SPECS_CHOICES = (
        ("A-36", "A-36 - Chapa AC"),
        ("A-106", "A-106 - Tubo AC"),
        ("16MO3", "16MO3 - Tubo AC"),
        ("B536", "B536 - Chapa Incoloy"),
        ("A-309", "A-309 - Chapa"),
        ("A-312", "A-312 - Chapa"),
    )
    metal_base_spec = models.CharField(max_length=25, choices=METAL_BASE_SPECS_CHOICES)
    # Chapa - 12.7 Tubo - 8": 12.7 | 2": 8.7
    METAL_BASE_ESPESSURA_CHOICES = [(12.7, "12,7 mm"), (8.7, "8,7 mm")]
    metal_base_espessura = models.FloatField(
        choices=METAL_BASE_ESPESSURA_CHOICES, null=True, blank=True
    )
    METAL_BASE_DIAMETRO_CHOICES = [
        (8, '8"'),
        (2, '2"'),
    ]
    metal_base_diametro = models.IntegerField(
        choices=METAL_BASE_DIAMETRO_CHOICES, null=True, blank=True
    )

    POSICAO_SOLDAGEM_CHOICES = (
        ("1G", "1G - Plana"),
        ("2G", "2G - Horizontal"),
        ("3G", "3G - Vertical"),
        ("4G", "4G - Sobre-Cabeça"),
        ("5G", "5G - Vertical"),
        ("6G", "6G - Inclinado 45º"),
        ("1F", "1F - Plana"),
        ("2F", "2F - Horizontal"),
        ("3F", "3F - Vertical"),
        ("4F", "4F - Sobre-Cabeça"),
    )
    posicao_soldagem = models.CharField(max_length=4, choices=POSICAO_SOLDAGEM_CHOICES)

    POSICAO_SOLDAGEM_PRG_CHOICES = (
        ("ASCENDENTE", "Ascendente"),
        ("DESCENDENTE", "Descendente"),
        ("NA", "N/A"),
    )
    posicao_soldagem_progressao = models.CharField(
        max_length=25, choices=POSICAO_SOLDAGEM_PRG_CHOICES, null=True
    )
    cobre_junta = models.BooleanField()
    GAS_PROTECAO_CHOICES = (
        ("ARGONIO", "Argônio"),
        ("ARCO2", "Ar+CO²"),
        ("CO2", "CO²"),
        ("NA", "N/A"),
    )
    # Verificar se a lógica está correta
    gas_protecao = models.CharField(
        max_length=10, choices=GAS_PROTECAO_CHOICES, null=True, blank=True
    )
    GAS_PROTECAO_PRG_CHOICES = (
        ("ASCENDENTE", "Ascendente"),
        ("DESCENDENTE", "Descendente"),
    )
    purga = models.BooleanField()

    ENSAIO_CHOICES = (("DOBRAMENTO", "Dobramento Mecânico"), ("ULTRASSOM", "Ultrassom"))
    ensaio = models.CharField(max_length=10, choices=ENSAIO_CHOICES)
    f_number = models.CharField(max_length=3, blank=True)

    class Meta:
        verbose_name = "Solicitação de Cadastro de Soldadores"
        verbose_name_plural = "Solicitações de Cadastro de Soldadores"

    def __str__(self):
        return f"{self.soldador.nome} - CP: {self.empresa.nome}"


class EnsaioMecanicoDobramento(models.Model):
    solicitacao = models.ForeignKey(
        SolicitacaoCadastroSoldador, on_delete=models.PROTECT
    )
    data_teste = models.DateField(auto_now=True)
    aprovado = models.BooleanField(default=False)
    realizado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ensaio Mecânico"
        verbose_name_plural = "Ensaios Mecânicos"

    def __str__(self):
        return f"Ensaio de {self.solicitacao.soldador.nome} em {self.data_teste}"


class EnsaioUltrassom(models.Model):
    solicitacao = models.ForeignKey(
        SolicitacaoCadastroSoldador, on_delete=models.PROTECT
    )
    data_teste = models.DateField(auto_now=True)
    aprovado = models.BooleanField(default=False)
    realizado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ensaio Ultrassom"
        verbose_name_plural = "Ensaios Ultrassom"

    def __str__(self):
        return f"Ensaio de {self.solicitacao.soldador.nome} em {self.data_teste}"


class TesteVisual(models.Model):
    solicitacao = models.OneToOneField(
        SolicitacaoCadastroSoldador, on_delete=models.PROTECT
    )
    TESTE_VISUAL_CHOICES = (
        ("Aprovado", "Aprovado"),
        ("Reprovado", "Reprovado"),
        ("N/A", "N/A"),
    )
    resultado = models.CharField(max_length=10, choices=TESTE_VISUAL_CHOICES, blank=True)
    LISTA_VERIFICA_CHOICES = (
        (
            "1",
            "1 - Segue as regras básicas, segurança e utiliza corretamente os EPI's básicos e específicos",
        ),
        (
            "2",
            "2 - Identifica corretamente os equipamentos e acessórios de soldagem apresentados",
        ),
        ("3", "3 - Utiliza corretamente os equipamentos e acessórios de soldagem"),
        ("4", "4 - Segue corretamente as variáveis de soldagem determinadas na EPS"),
        ("5", "5 - Mantém um padrão uniforme e linear das camadas de solda"),
        ("6", "6 - Deposita o material em passes uniformes, mantendo um padrão linear"),
        (
            "7",
            "7 - Face (mordedura, poros, sobreposição, trinca, deposição insuficiente, reforço excessivo, "
            "abertura de arco, respingo",
        ),
        (
            "8",
            "8 - Raiz (mordedura da raiz, falta de penetração, falta de fusão, perfuração, concavidade, penetração "
            "excessiva",
        ),
    )
    motivos_reprovacao = models.CharField(
        max_length=200, blank=True, help_text="Motivos da reprovação separados por vírgula"
    )
    data_teste = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Teste Visual"
        verbose_name_plural = "Testes Visuais"

    def __str__(self):
        return f"Teste Visual - {self.solicitacao.soldador.nome}"


class Raqs(models.Model):
    n_master = models.CharField(max_length=10, editable=False)
    n_sequencia = models.CharField(max_length=10, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    solicitacoes = models.ManyToManyField(
        SolicitacaoCadastroSoldador, related_name="raqs"
    )
    data = models.DateField(auto_now=True)
    aberto = models.BooleanField(default=True)
    cp_number = models.CharField(max_length=15, editable=False, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            from django.db.models import F

            self.empresa.n_raqs = F("n_raqs") + 1
            self.empresa.save()
            self.empresa.refresh_from_db()
            self.n_sequencia = str(self.empresa.n_raqs)
            super().save(*args, **kwargs)
            self.n_master = f"MAST-FORM-{self.pk}"
            super().save(update_fields=["n_master", "n_sequencia"])
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "RAQS"
        verbose_name_plural = "RAQS"

    def __str__(self):
        return f"RAQS - {self.empresa.nome}"


class CQS(models.Model):
    FQ_CONSUMIVEL_CHOICES = (
        ("1-3", "1 a 3"),
        ("1-4", "1 a 4"),
        ("6", "6"),
        ("34-41-46", "34, 41 a 46"),
        ("1-5", "1 e 5"),
    )
    fq_consumivel = models.CharField(max_length=10, choices=FQ_CONSUMIVEL_CHOICES)
    FQ_METAL_DE_BASE_CHOICES = (
        ("1-15f-34-41-49", "1 a 15 f, 34, 41 a 49"),
        ("todos", "TODOS"),
    )
    fq_metal_de_base = models.CharField(max_length=15, choices=FQ_METAL_DE_BASE_CHOICES)
    PN_METAL_DE_BASE_CHOICES = (("1", "1"), ("3", "3"), ("46", "46"), ("8", "8"))
    pn_metal_de_base = models.CharField(max_length=2, choices=PN_METAL_DE_BASE_CHOICES)
    MODO_TRANSF_CHOICES = (
        ("N/A", "N/A"),
        ("CURTO_CIRCUITO", "Curto Circuito"),
        ("GLOBULAR", "Globular"),
        ("SPRAY", "Spray"),
    )
    modo_transferencia = models.CharField(
        max_length=15, choices=MODO_TRANSF_CHOICES, null=True, blank=True
    )


@receiver(pre_save, sender=SolicitacaoCadastroSoldador)
def set_f_number(sender, instance, **kwargs):
    # Mapeamento de consumível para f_number
    f_number_mapping = {
        "E6010": "3",
        "E-6010": "3",
        "E7018": "4",
        "E-7018": "4",
        "ER-70S3": "6",
        "ER-70S-3": "6",
        "ER-70S6": "6",
        "ER-70S-6": "6",
        "E-71T1": "6",
        "E-71T-1": "6",
        "ER-309L": "6",
        "ER-308L": "6",
        "ER-NiCrFe3": "43",
        "E-NiCrFe3": "43",
        "E-309L": "5",
        "ER-NiCrMo3": "43",
        "E-NiCrMo3": "43",
    }

    # Define o f_number com base no consumível escolhido
    classificacao = instance.consumivel_classificacao
    if classificacao in f_number_mapping:
        instance.f_number = f_number_mapping[classificacao]


@receiver(pre_save, sender=CQS)
def set_fq_consumivel(sender, instance, **kwargs):
    # Mapeamento de f_number para fq_consumivel
    f_number_to_fq = {
        "3": "1-3",
        "4": "1-4",
        "6": "6",
        "43": "34-41-46",
        "5": "1-5",
    }

    # Auto-preencher fq_consumivel com base no f_number da solicitação
    if hasattr(instance, "solicitacao") and instance.solicitacao:
        f_number = instance.solicitacao.f_number
        if f_number in f_number_to_fq:
            instance.fq_consumivel = f_number_to_fq[f_number]
