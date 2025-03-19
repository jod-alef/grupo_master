from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Soldador(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
      # TODO: Def SINETE - Se não estiver preenchido

    def clean(self):
        super().clean()
        if Soldador.objects.filter(cpf=self.cpf).exclude(pk=self.pk).exists():
            raise ValidationError({'cpf': "CPF já cadastrado."})

    class Meta:
        verbose_name = 'Soldador'
        verbose_name_plural = 'Soldadores'

    def __str__(self):
        return f"{self.nome}"


class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos')

    def __str__(self):
        return f"{self.nome}"


class AbstractEmpresaUser(AbstractUser):
    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='usuarios', null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.username} - ({self.empresa.nome if self.empresa else 'Sem empresa'})"


class Operador(AbstractEmpresaUser):
    setor = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Operador'
        verbose_name_plural = 'Operadores'


class SolicitacaoCadastroSoldador(models.Model):  # TODO: Perguntar sobre cabeçalho - Lógica de auto-complete
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
    sinete = models.CharField(max_length=10)  # TODO: SINETE É Ñ OBRIGATÓRIO
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
        ("FCAW", "FCAW - Soldagem com arame tubular")
    )
    processo_soldagem = models.CharField(max_length=4, choices=PROCESSO_SOLDAGEM_CHOICES)

    CONSUMIVEL_SPEC_CHOICES = [
        ("SFA_5-1", "SFA 5.1"),
        ("SFA_5-4", "SFA 5.4"),
        ("SFA_5-9", "SFA 5.9"),
        ("SFA_5-14", "SFA 5.14"),
        ("SFA_5-11", "SFA 5.11"),
        ("SFA_5-18", "SFA 5.18"),
        ("SFA_5-20", "SFA 5.20")]
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
    consumivel_classificacao = models.CharField(max_length=10, choices=CONSUMIVEL_CLASS_CHOICES)
    CONSUMIVEL_DIAMETRO_CHOICES = [
        ("1.2", "1,2 mm"),
        ("3.2", "3,25 mm")
    ]
    # GMAW | FCAW 1.2 - SMAW |GTAW 3.2
    consumivel_diametro = models.CharField(max_length=4, choices=CONSUMIVEL_DIAMETRO_CHOICES)

    METAL_BASE_SPECS_CHOICES = (
        ("A-36", "A-36 - Chapa AC"),
        ("A-106", "A-106 - Tubo AC"),
        ("16MO3", "16MO3 - Tubo AC"),
        ("SB536", "SB536 - Chapa Incoloy"),
        ("A-309", "A-309 - Chapa"),
        ("A-312", "A-312 - Chapa"),)
    metal_base_spec = models.CharField(max_length=25, choices=METAL_BASE_SPECS_CHOICES)
    # Chapa - 12.7 Tubo - 8": 12.7 | 2": 8.7
    METAL_BASE_ESPESSURA_CHOICES = [
        (12.7, "12,7 mm"),
        (8.7, "8,7 mm")
    ]
    metal_base_espessura = models.FloatField(choices=METAL_BASE_ESPESSURA_CHOICES, null=True, blank=True)
    METAL_BASE_DIAMETRO_CHOICES = [
        (8, '8"'),
        (2, '2"'),]
    metal_base_diametro = models.IntegerField(choices=METAL_BASE_DIAMETRO_CHOICES, null=True, blank=True)

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
        ("4F", "4F - Sobre-Cabeça"))
    posicao_soldagem = models.CharField(max_length=4, choices=POSICAO_SOLDAGEM_CHOICES)

    POSICAO_SOLDAGEM_PRG_CHOICES = (
        ("ASCENDENTE", "Ascendente"),
        ("DESCENDENTE", "Descendente"),
        ("NA", "N/A")
    )
    posicao_soldagem_progressao = models.CharField(max_length=25, choices=POSICAO_SOLDAGEM_PRG_CHOICES, null=True)
    cobre_junta = models.BooleanField()
    GAS_PROTECAO_CHOICES = (
        ("ARGONIO", "Argônio"),
        ("ARCO2", "Ar+CO²"),
        ("CO2", "CO²"),
        ("NA", "N/A"))
    # Verificar se a lógica está correta
    gas_protecao = models.CharField(max_length=10, choices=GAS_PROTECAO_CHOICES, null=True, blank=True)
    GAS_PROTECAO_PRG_CHOICES = (
        ("ASCENDENTE", "Ascendente"),
        ("DESCENDENTE", "Descendente"),
    )
    purga = models.BooleanField()
    MODO_TRANSF_CHOICES = (
        ("N/A", "N/A"),
        ("CURTO_CIRCUITO", "Curto Circuito"),
        ("GLOBULAR", "Globular"),
        ("SPRAY", "Spray"))
    modo_transferencia = models.CharField(max_length=15, choices=MODO_TRANSF_CHOICES, null=True, blank=True)
    # Se GMAW = Curto Circuito ---- Se FCAW = Todos
    ENSAIO_CHOICES = (
        ("DOBRAMENTO", "Dobramento Mecânico"),
        ("ULTRASSOM", "Ultrassom")
    )
    ensaio = models.CharField(max_length=10,
                              choices=ENSAIO_CHOICES)
    f_number = models.CharField(max_length=2)
    faixa_qualificada = models.CharField(max_length=15)
    cp_number = models.CharField(max_length=15, editable=False, blank=True)  # Apenas leitura TODO: POR EMPRESA!!!! - Inserir TESTE VISUAL!!! Inserir REVALIDAÇÃO!!!

    class Meta:
        verbose_name = 'Solicitação de Cadastro de Soldadores'
        verbose_name_plural = 'Solicitações de Cadastro de Soldadores'

    def save(self, *args, **kwargs):
        # Define o CP_Number com o formato `PK-AnoAtual`
        if not self.pk:
            super().save(*args, **kwargs)  # Save initially to generate the pk
            current_year = datetime.now().year
            self.cp_number = f"M00{self.pk}-{current_year}"
            # Save again to persist the generated cp_number
            super().save(update_fields=['cp_number'])  # Update only the cp_number field
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.soldador.nome} - CP: {self.cp_number}"


class EnsaioMecanicoDobramento(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoCadastroSoldador, on_delete=models.PROTECT)
    data_teste = models.DateField(auto_now=True)
    fotos_amostra_1 = models.FileField(upload_to='media/')
    fotos_amostra_2 = models.FileField(upload_to='media/')
    fotos_amostra_3 = models.FileField(upload_to='media/')
    fotos_amostra_4 = models.FileField(upload_to='media/')
    aprovado = models.BooleanField()

    class Meta:
        verbose_name = 'Ensaio Mecânico'
        verbose_name_plural = 'Ensaios Mecânicos'

    def __str__(self):
        return f"Ensaio de {self.solicitacao.soldador.nome} em {self.data_teste}"


class EnsaioUltrassom(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoCadastroSoldador, on_delete=models.PROTECT)
    data_teste = models.DateField(auto_now=True)
    aprovado = models.BooleanField()

    class Meta:
        verbose_name = 'Ensaio Ultrassom'
        verbose_name_plural = 'Ensaios Ultrassom'

    def __str__(self):
        return f"Ensaio de {self.solicitacao.soldador.nome} em {self.data_teste}"


class Raqs(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoCadastroSoldador, on_delete=models.PROTECT)
    LISTA_VERIFICA_CHOICES = (
        ("1", "1 - Segue as regras básicas, segurança e utiliza corretamente os EPI's básicos e específicos"),
        ("2", "2 - Identifica corretamente os equipamentos e acessórios de soldagem apresentados"),
        ("3", "3 - Utiliza corretamente os equipamentos e acessórios de soldagem"),
        ("4", "4 - Segue corretamente as variáveis de soldagem determinadas na EPS"),
        ("5", "5 - Mantém um padrão uniforme e linear das camadas de solda"),
        ("6", "6 - Deposita o material em passes uniformes, mantendo um padrão linear"),
        ("7", "7 - Face (mordedura, poros, sobreposição, trinca, deposição insuficiente, reforço excessivo, "
              "abertura de arco, respingo"),
        ("8", "8 - Raiz (mordedura da raiz, falta de penetração, falta de fusão, perfuração, concavidade, penetração "
              "excessiva"),

    )
    class Meta:
        verbose_name = 'RAQS'
        verbose_name_plural = 'RAQS'

    lista_de_verificacoes = models.CharField(max_length=1, choices=LISTA_VERIFICA_CHOICES)

