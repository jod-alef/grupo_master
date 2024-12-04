from django.core.exceptions import ValidationError
from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos')


class Soldador(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    sinete = models.CharField(max_length=10)


class SolicitacaoCadastroSoldador(models.Model):
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
    # TODO: Perguntar sobre cabeçalho - Lógica de auto-complete
    data = models.DateField(auto_now=True)
    eps = models.CharField(max_length=10)
    NORMA_PROJETO_CHOICES = (
        ("None", "Norma do Projeto"),
        ("ASME_I", "ASME I - 2023"),
        ("ASME_VII", "ASME VII Div.1/Div.2 - 2023"),
        ("ASME_B31-1", "ASME B31.1 - 2022"),
        ("ASME_B31-3", "ASME B31.3 - 2022"),
        ("ASME_B31-4", "ASME B31.4 - 2022"),
        ("ASME_B31-8", "ASME B31.8 - 2022"),
        ("API_620", "API 620 - 2021"),
        ("API_650", "API 650 - 2021"),
        ("AWS_D1-1", "AWS D1.1 - 2020"),
    )
    norma_projeto = models.CharField(max_length=10, choices=NORMA_PROJETO_CHOICES)
    PROCESSO_SOLDAGEM_CHOICES = (
        ("None", "Processo de Soldagem"),
        ("SMAW", "Soldagem com eletrodo revestido"),
        ("GTAW", "Soldagem TIG"),
        ("GMAW", "Soldagem MIG"),
        ("FCAW", "Soldagem com arame tubular")
    )
    processo_soldagem = models.CharField(max_length=4, choices=PROCESSO_SOLDAGEM_CHOICES)

    CONSUMIVEL_SPEC_CHOICES = [
        ("None", "Especificação"),
        ("SFA_5-1", "SFA 5.1"),
        ("SFA_5-4", "SFA 5.4"),
        ("SFA_5-5", "SFA 5.5"),
        ("SFA_5-11", "SFA 5.11"),
        ("SFA_5-18", "SFA 5.18"),
        ("SFA_5-20", "SFA 5.20")]
    consumivel_spec = models.CharField(max_length=15, choices=CONSUMIVEL_SPEC_CHOICES)

    CONSUMIVEL_CLASS_CHOICES = [
        ("None", "Classificação"),
        ("E7018", "E7018"),
        ("E6010", "E6010"),
        ("E-71T-1", "E-71T-1"),
        ("E-309", "E-309"),
        ("E-312", "E-312"),
        ("ER-70S-3", "ER-70S-3"),
        ("ER-70S-6", "ER-70S-6"),
        ("ER-309", "ER-309")]
    consumivel_classificacao = models.CharField(max_length=8, choices=CONSUMIVEL_CLASS_CHOICES)
    CONSUMIVEL_DIAMETRO_CHOICES = [
        ("None", "Diametro"),
        ("1.2", "1,2 mm"),
        ("3.2", "3,25 mm")
    ]
    # GMAW | FCAW 1.2 - SMAW |GTAW 3.2
    consumivel_diametro = models.CharField(max_length=4, choices=CONSUMIVEL_DIAMETRO_CHOICES)

    METAL_BASE_SPECS_CHOICES = (
        ("None", "Especificação"),
        ("A-36", "A-36 - Chapa AC"),
        ("A-106", "A-106 - Tubo AC"),
        ("16MO3", "16MO3 - Tubo AC"),
        ("SB536", "SB536 - Chapa Incoloy"),
        ("A-309", "A-309 - Chapa"),
        ("A-312", "A-312 - Chapa"),)
    metal_base_spec = models.CharField(max_length=25, choices=METAL_BASE_SPECS_CHOICES)
    # Chapa - 12.7 Tubo - 8": 12.7 | 2": 8.7
    METAL_BASE_ESPESSURA_CHOICES = [
        ("None", "Espessura"),
        ("12.7", "12,7"),
        ("8.7", "8,7")
    ]
    meta_base_espessura = models.FloatField(max_length=4, choices=METAL_BASE_ESPESSURA_CHOICES)
    METAL_BASE_DIAMETRO_CHOICES = (
        ("None", "Diâmetro"),
        ('8', '8"'),
        ('2', '2"'),)
    metal_base_diametro = models.CharField(max_length=4, choices=METAL_BASE_DIAMETRO_CHOICES)

    POSICAO_SOLDAGEM_CHOICES = (
        ("None", "Posição de Soldagem"),
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
        ("None", "Posição de Soldagem"),
        ("NA", "Não Aplicável"),
        ("ASCENDENTE", "Ascendente"),
        ("DESCENDENTE", "Descendente"),
        ("ASCENDENTE_OU_DESCENDENTE", "Ascendente ou Descendente"),)
    posicao_soldagem_progressao = models.CharField(max_length=25, choices=POSICAO_SOLDAGEM_PRG_CHOICES)
    cobre_junta = models.BooleanField()
    gas_protecao = models.BooleanField()
    purga = models.BooleanField()
    MODO_TRANSF_CHOICES = (
        ("None", "Modo de Transferencia"),
        ("NA", "N/A"),
        ("CURTO_CIRCUITO", "Curto Circuito"),
        ("GLOBULAR", "Globular"),
        ("SPRAY", "Spray"))
    modo_transferencia = models.CharField(max_length=15, choices=MODO_TRANSF_CHOICES)
    cp_number = models.CharField(max_length=15)  # CPº = pk + current.year


class EnsaioMecanicoDobramento(models.Model):
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
    data_teste = models.DateField(auto_now=True)
    fotos_amostra_inicial = models.FileField(upload_to='media/')
    fotos_amostra_final = models.FileField(upload_to='media/')
    aprovado = models.BooleanField()

    class Meta:
        verbose_name = 'Ensaio Mecânico'
        verbose_name_plural = 'Ensaios Mecânicos'

    def __str__(self):
        return f"Ensaio de {self.soldador} em {self.data_teste}"

    # TODO:
    '''
    Dúvidas:
    Ensaio mecânico e Ultrassom - Lógica de CP_N
    Solicitação de ensaio é feita pelo cliente ou segue alguma lógica?
    RAQS = Numeração auto incrementavel correspondente à solicitação total.
    
    Lógica de preenchimento da solicitação de qualificação de soldadores:
    
     - Usar HTMX para criar um formulário que adicione automaticamente as solicitações como abaixo
            -- Cabeçalho
            |-- Empresa
            |-- Soldador - Cadastrar - Autocomplete para Existentes
            -- Formulário de Solicitação de Qualificação
            |-- Confirmação
            -- Lista de Solicitações
    
    '''


class EnsaioUltrassom(models.Model):
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
    data_teste = models.DateField(auto_now=True)
    aprovado = models.BooleanField()

    class Meta:
        verbose_name = 'Ensaio Ultrassom'
        verbose_name_plural = 'Ensaios Ultrassom'

    def __str__(self):
        return f"Ensaio de {self.soldador} em {self.data_teste}"


class Raqs(models.Model):
    soldador = models.ForeignKey(Soldador, on_delete=models.PROTECT)
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
    lista_de_verificacoes = models.CharField(max_length=1, choices=LISTA_VERIFICA_CHOICES)

# TODO: Redução de Informação nos Certificados.
