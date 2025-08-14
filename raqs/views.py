from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from raqs.forms import SoldadorForm, SolicitacaoCadastroSoldadorForm
from raqs.models import *
from django.contrib.auth.decorators import user_passes_test
from collections import defaultdict


@login_required
def dashboard_redirect(request):
    """
    Redireciona para o dashboard apropriado baseado na empresa do usuário:
    - Grupo Master → master_dashboard
    - Outras empresas → empresa-dashboard
    """
    if hasattr(request.user, 'empresa') and request.user.empresa:
        if request.user.empresa.nome == "Grupo Master":
            return redirect("master_dashboard")
        else:
            return redirect("empresa-dashboard")
    else:
        # Se não tem empresa definida, vai para dashboard empresa por padrão
        return redirect("empresa-dashboard")


def solicitacao_qualificacao_soldador(request, soldador_id=None):
    soldador = get_object_or_404(Soldador, id=soldador_id) if soldador_id else None
    empresa = get_object_or_404(
        Empresa, usuarios__id=request.user.id
    )  # Get the company via the current user

    if request.method == "POST":
        form = SolicitacaoCadastroSoldadorForm(request.POST)
        if form.is_valid():
            # Save the form, setting the empresa and soldador fields explicitly
            solicitacao = form.save(commit=False)
            solicitacao.soldador = soldador
            solicitacao.empresa = empresa
            solicitacao.save()

            if "add_another" in request.POST:
                return redirect(
                    "solicitacao-qualificacao-soldador", soldador_id=soldador_id
                )
            elif "save_and_return" in request.POST:
                return redirect("empresa-dashboard")
        else:
            print(form.errors)  # For debugging, remove in production

    else:
        # Pre-fill the empresa and soldador fields in the form
        form = SolicitacaoCadastroSoldadorForm(
            initial={"soldador": soldador, "empresa": empresa}
        )

    return render(
        request,
        "solicitacao_qualificacao_soldador.html",
        {
            "form": form,
            "soldador": soldador,
            "empresa": empresa,
            "error_messages": form.errors,
        },
    )


def cadastro_soldador(request):
    if request.method == "POST":
        form = SoldadorForm(request.POST)
        if form.is_valid():
            soldador = form.save()
            if "add_solicitacao" in request.POST:
                return redirect(
                    "solicitacao-qualificacao-soldador", soldador_id=soldador.id
                )
            elif "add_another" in request.POST:
                return render(
                    request, "cadastro_soldador.html", {"form": SoldadorForm()}
                )
            return redirect(
                "solicitacao_qualificacao_soldador", soldador_id=soldador.id
            )  # Redirect to next form
    else:
        form = SoldadorForm()
    return render(request, "cadastro_soldador.html", {"form": form})


def update_ensaio_choices(request):
    norma_projeto = request.GET.get("norma_projeto", "").strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("Norma de projeto:", norma_projeto)

    # Dynamically adjust the `ensaio` field based on `norma_projeto`
    if norma_projeto in ["AWS_D1-1", "AWS D1.1 - 2020"]:
        form.fields["ensaio"].choices = [("DOBRAMENTO", "Dobramento Mecânico")]
    else:
        form.fields["ensaio"].choices = [
            ("DOBRAMENTO", "Dobramento Mecânico"),
            ("ULTRASSOM", "Ultrassom"),
        ]

    # Render the updated `ensaio` field

    return render(request, "partials/ensaio_field.html", {"field": form["ensaio"]})


def list_soldadores(request):
    soldadores = Soldador.objects.all()
    return render(request, "list_soldadores.html", {"soldadores": soldadores})


def update_metal_fields(request):
    # Obtenha o valor enviado pelo HTMX
    metal_base_spec = request.GET.get("metal_base_spec", "").strip()
    form = SolicitacaoCadastroSoldadorForm()
    # print("A escolha foi:", metal_base_spec)  # Para depuração

    # Ajuste os campos com base na escolha
    if metal_base_spec in ["A-36", "SB536", "A-309", "A-312"]:
        form.fields["metal_base_espessura"].disabled = False
        form.fields["metal_base_diametro"].disabled = True
        form.fields["posicao_soldagem"].choices = [
            choice
            for choice in form.fields["posicao_soldagem"].choices
            if choice[0] not in ["5G", "6G"]
        ]
    elif metal_base_spec in ["A-106", "16MO3"]:
        form.fields["metal_base_espessura"].disabled = True
        form.fields["metal_base_diametro"].disabled = False
        form.fields["posicao_soldagem"].choices = [
            choice
            for choice in form.fields["posicao_soldagem"].choices
            if choice[0] not in ["3G", "4G"]
        ]

    # Renderize os campos dinâmicos
    return render(request, "partials/metal_fields.html", {"form": form})


def update_progressao_choices(request):
    posicao_soldagem = request.GET.get("posicao_soldagem", "").strip()
    form = SolicitacaoCadastroSoldadorForm()
    # print("Posição de Soldagem:", posicao_soldagem) # Depuração

    # Ajustar dinâmicamente a posição com base na progressão
    if posicao_soldagem in ["6G"]:
        form.fields["posicao_soldagem_progressao"].disabled = False
        form.fields["posicao_soldagem_progressao"].choices = [
            ("ASCENDENTE", "Ascendente")
        ]
    elif posicao_soldagem in ["3G", "3F", "5G"]:
        form.fields["posicao_soldagem_progressao"].disabled = False
        form.fields["posicao_soldagem_progressao"].choices = [
            ("ASCENDENTE", "Ascendente"),
            ("DESCENDENTE", "Descendente"),
        ]
    else:
        form.fields["posicao_soldagem_progressao"].readonly = True

    # Renderiza o campo de progressão

    return render(
        request,
        "partials/progressao_field.html",
        {"field": form["posicao_soldagem_progressao"]},
    )


@login_required
def solicitacoes_soldador(request, soldador_id):
    empresa = get_object_or_404(Empresa, usuarios__id=request.user.id)
    soldador = get_object_or_404(Soldador, id=soldador_id)
    solicitacoes = SolicitacaoCadastroSoldador.objects.filter(
        soldador=soldador, empresa=empresa
    )

    soldador_status = {}
    solicitacoes_abertas = []
    solicitacoes_finalizadas = []
    
    for solicitacao in solicitacoes:
        status = "Aguardando Teste"
        
        # Verificar se há teste visual
        try:
            teste_visual = TesteVisual.objects.get(solicitacao=solicitacao)
            if teste_visual.resultado == "Reprovado":
                status = "Reprovado Teste Visual"
            elif teste_visual.resultado == "Aprovado":
                # Se aprovado no teste visual, verificar ensaios
                if solicitacao.ensaio == "DOBRAMENTO":
                    if EnsaioMecanicoDobramento.objects.filter(
                        solicitacao=solicitacao, aprovado=True, realizado=True
                    ).exists():
                        status = "Aprovado - DM"
                    elif EnsaioMecanicoDobramento.objects.filter(
                        solicitacao=solicitacao, aprovado=False, realizado=True
                    ).exists():
                        status = "Reprovado - DM"
                elif solicitacao.ensaio == "ULTRASSOM":
                    if EnsaioUltrassom.objects.filter(
                        solicitacao=solicitacao, aprovado=True, realizado=True
                    ).exists():
                        status = "Aprovado - UT"
                    elif EnsaioUltrassom.objects.filter(
                        solicitacao=solicitacao, aprovado=False, realizado=True
                    ).exists():
                        status = "Reprovado - UT"
        except TesteVisual.DoesNotExist:
            # Se não há teste visual, verificar apenas ensaios (lógica antiga)
            if EnsaioMecanicoDobramento.objects.filter(
                solicitacao=solicitacao, aprovado=True
            ).exists():
                status = "Aprovado - DM"
            elif EnsaioUltrassom.objects.filter(
                solicitacao=solicitacao, aprovado=True
            ).exists():
                status = "Aprovado - UT"

        soldador_status[solicitacao.id] = status
        
        # Separar solicitações por status
        if "Aguardando" in status:
            solicitacoes_abertas.append(solicitacao)
        elif "Aprovado" in status or "Reprovado" in status:
            solicitacoes_finalizadas.append(solicitacao)

    return render(
        request,
        "partials/solicitacoes_soldador.html",
        {
            "soldador": soldador,
            "solicitacoes": solicitacoes,
            "solicitacoes_abertas": solicitacoes_abertas,
            "solicitacoes_finalizadas": solicitacoes_finalizadas,
            "soldador_status": soldador_status,
            "empresa": empresa,
        },
    )


def is_grupo_master(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or (hasattr(user, "empresa") and user.empresa and user.empresa.nome == "Grupo Master")
        )
    )


@user_passes_test(is_grupo_master)
def master_dashboard(request):
    """
    Cria o Dashboard baseado em solicitações, agrupando os dados por empresa e por soldador.
    Mostra apenas solicitações que não estão em RAQS fechados.
    """
    # Inicializamos uma estrutura de dados para juntar as informações
    empresas_data = defaultdict(
        lambda: defaultdict(list)
    )  # {empresa: {soldador: [solicitacoes]}}

    # Obter todas as empresas
    empresas = Empresa.objects.all()
    
    empresas_data_list = []
    for empresa in empresas:
        # Verificar se há RAQS aberto para esta empresa
        raqs_aberto = Raqs.objects.filter(empresa=empresa, aberto=True).first()
        
        # Verificar se há RAQS fechados para esta empresa
        raqs_fechados = Raqs.objects.filter(empresa=empresa, aberto=False).order_by('-data')
        
        # Filtrar solicitações que não estão em nenhum RAQS (disponíveis para criação de RAQS)
        solicitacoes_disponiveis = SolicitacaoCadastroSoldador.objects.filter(
            empresa=empresa,
            raqs__isnull=True
        ).select_related("soldador")
        
        # Organizar por soldador
        soldadores_dict = defaultdict(list)
        for solicitacao in solicitacoes_disponiveis:
            soldadores_dict[solicitacao.soldador].append(solicitacao)
        
        # Verificar se há soldadores com solicitações disponíveis para RAQS
        tem_soldadores_para_raqs = bool(soldadores_dict)
        
        # Se há RAQS fechado, mostrar os RAQS em vez das solicitações individuais
        if raqs_fechados.exists() and not raqs_aberto:
            empresas_data_list.append({
                "empresa": empresa,
                "raqs_aberto": False,
                "raqs": None,
                "raqs_fechados": raqs_fechados,
                "soldadores": [],  # Não mostrar soldadores individuais se há RAQS fechado
                "tem_raqs_fechados": True,
                "tem_soldadores_para_raqs": tem_soldadores_para_raqs,
            })
        else:
            # Mostrar solicitações individuais apenas se não há RAQS fechados ou há RAQS aberto
            empresas_data_list.append({
                "empresa": empresa,
                "raqs_aberto": bool(raqs_aberto),
                "raqs": raqs_aberto,
                "raqs_fechados": [],
                "soldadores": [
                    {"soldador": soldador, "solicitacoes": solicitacoes}
                    for soldador, solicitacoes in soldadores_dict.items()
                ] if soldadores_dict else [],
                "tem_raqs_fechados": False,
                "tem_soldadores_para_raqs": tem_soldadores_para_raqs,
            })

    # Enviamos os dados processados para o template
    return render(
        request, "master_dashboard.html", {"empresas_data": empresas_data_list}
    )


@login_required
def empresa_dashboard(request):
    empresa = get_object_or_404(Empresa, usuarios__id=request.user.id)
    soldadores = Soldador.objects.filter(
        solicitacaocadastrosoldador__empresa=empresa
    ).distinct()
    solicitacoes = SolicitacaoCadastroSoldador.objects.filter(empresa=empresa)
    
    # Buscar RAQS fechados da empresa
    raqs_fechados = Raqs.objects.filter(empresa=empresa, aberto=False).order_by('-data')

    return render(
        request,
        "empresa_dashboard.html",
        {
            "empresa": empresa,
            "soldadores": soldadores,
            "solicitacoes": solicitacoes,
            "raqs_fechados": raqs_fechados,
        },
    )


def verificar_cpf_htmx(request):
    cpf = request.GET.get("cpf", "").strip()
    soldador = Soldador.objects.filter(cpf=cpf).first()

    if soldador:
        return render(
            request, "partials/existente_soldador.html", {"soldador": soldador}
        )
    return render(request, "partials/novo_soldador.html")


def custom_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirect based on user's company
                if hasattr(user, 'empresa') and user.empresa and user.empresa.nome == "Grupo Master":
                    return redirect("master_dashboard")
                else:
                    return redirect("empresa-dashboard")
            else:
                messages.error(request, "Senha ou usuário inválidos. Tente novamente..")
        else:
            messages.error(request, "Senha ou usuário inválidos. Tente novamente..")
    else:
        form = AuthenticationForm(request=request)

    return render(request, "login.html", {"form": form})


@login_required
def apagar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoCadastroSoldador, id=solicitacao_id)
    solicitacao.delete()
    return redirect("empresa-dashboard")


def update_consumivel_classificacao(request):
    processo_soldagem = request.GET.get("processo_soldagem", "").strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("Processo de Soldagem:", processo_soldagem)

    if processo_soldagem == "SMAW":
        form.fields["consumivel_classificacao"].choices = [
            ("E-6010", "E-6010"),
            ("E-7018", "E-7018"),
            ("E-NiCrFe3", "E-NiCrFe3"),
            ("E-309L", "E-309L"),
        ]
        form.fields["consumivel_spec"].choices = [
            ("SFA_5-1", "SFA 5.1"),
            ("SFA_5-4", "SFA 5.4"),
            ("SFA_5-11", "SFA 5.11"),
        ]
    elif processo_soldagem == "GTAW":
        form.fields["consumivel_classificacao"].choices = [
            ("ER-70S3", "ER-70S3"),
            ("ER-309L", "ER-309L"),
            ("ER-308L", "ER-308L"),
            ("ER-NiCrFe3", "ER-NiCrFe3"),
            ("ER-NiCrMo3", "ER-NiCrMo3"),
        ]
        form.fields["consumivel_spec"].choices = [
            ("SFA_5-9", "SFA 5.9"),
            ("SFA_5-14", "SFA 5.14"),
            ("SFA_5-18", "SFA 5.18"),
        ]
        form.fields["gas_protecao"].disabled = False
        form.fields["gas_protecao"].choices = [("ARGONIO", "Argônio")]
    elif processo_soldagem == "GMAW":
        form.fields["consumivel_classificacao"].choices = [
            ("ER-70S6", "ER-70S6"),
        ]
        form.fields["consumivel_spec"].choices = [
            ("SFA_5-18", "SFA 5.18"),
        ]
        form.fields["gas_protecao"].disabled = False
        form.fields["gas_protecao"].choices = [
            ("ARCO2", "Ar+CO²"),
        ]
    elif processo_soldagem == "FCAW":
        form.fields["consumivel_classificacao"].choices = [("E-71T1", "E-71T1")]
        form.fields["consumivel_spec"].choices = [
            ("SFA_5-20", "SFA 5.20"),
        ]
        form.fields["gas_protecao"].disabled = False
        form.fields["gas_protecao"].choices = [
            ("CO2", "CO²"),
        ]
    else:
        form.fields["consumivel_classificacao"].choices = []
        form.fields["consumivel_spec"].choices = []
        form.fields["gas_protecao"].readonly = True
        form.fields["gas_protecao"].choices = [
            ("NA", "N/A"),
        ]

    return render(
        request,
        "partials/consumivel_classificacao_field.html",
        {
            "field": form["consumivel_classificacao"],
            "spec_field": form["consumivel_spec"],
            "field_gprotec": form["gas_protecao"],
        },
    )


# RAQS


def criar_raqs(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    existente_aberto = Raqs.objects.filter(empresa=empresa, aberto=True).exists()

    if existente_aberto:
        messages.error(request, "Já existe um RAQS aberto para esta empresa.")
        return redirect("master_dashboard")

    # Buscar solicitações disponíveis (que não estão em nenhum RAQS)
    solicitacoes_disponiveis = SolicitacaoCadastroSoldador.objects.filter(
        empresa=empresa,
        raqs__isnull=True
    )
    
    if not solicitacoes_disponiveis.exists():
        messages.error(request, "Não há solicitações disponíveis para criar um RAQS para esta empresa.")
        return redirect("master_dashboard")

    # Criar o novo RAQS
    novo_raqs = Raqs.objects.create(empresa=empresa, aberto=True)
    
    # Adicionar automaticamente todas as solicitações disponíveis
    novo_raqs.solicitacoes.add(*solicitacoes_disponiveis)
    novo_raqs.save()
    
    messages.success(request, f"RAQS criado com sucesso! {solicitacoes_disponiveis.count()} solicitações adicionadas automaticamente.")
    return redirect("raqs_detail", raqs_id=novo_raqs.id)


def adicionar_solicitacao_raqs(request, raqs_id, solicitacao_id=None):
    raqs = get_object_or_404(Raqs, id=raqs_id, aberto=True)

    if solicitacao_id:
        solicitacao = get_object_or_404(
            SolicitacaoCadastroSoldador, id=solicitacao_id, empresa=raqs.empresa
        )
        raqs.solicitacoes.add(
            solicitacao
        )  # supondo que exista um ManyToMany "solicitacoes"
    else:
        solicitacoes_empresa = SolicitacaoCadastroSoldador.objects.filter(
            empresa=raqs.empresa
        )
        raqs.solicitacoes.add(*solicitacoes_empresa)

    raqs.save()
    messages.success(request, "Solicitação(ões) adicionada(s) ao RAQS com sucesso.")
    return redirect("raqs_detail", raqs_id=raqs.id)


def fechar_raqs(request, raqs_id):
    raqs = get_object_or_404(Raqs, id=raqs_id)
    raqs.aberto = False
    raqs.save()
    messages.success(request, "RAQS fechado com sucesso!")
    return redirect("master_dashboard")


def raqs_detail(request, raqs_id):
    raqs = get_object_or_404(Raqs, id=raqs_id)
    if request.method == "POST":
        if not raqs.aberto:
            messages.error(request, "Este RAQS está fechado e não pode ser modificado.")
            return redirect("raqs_detail", raqs_id=raqs.id)
        
        for solicitacao in raqs.solicitacoes.all():
            # Teste Visual (agora individual por solicitação)
            teste_visual_key = f"teste_visual_{solicitacao.id}"
            if teste_visual_key in request.POST:
                teste_visual, _ = TesteVisual.objects.get_or_create(solicitacao=solicitacao)
                teste_visual.resultado = request.POST[teste_visual_key]
                
                # Processar motivos de reprovação se o teste visual foi reprovado
                motivos_key = f"motivos_reprovacao_{solicitacao.id}"
                if request.POST[teste_visual_key] == "Reprovado" and motivos_key in request.POST:
                    teste_visual.motivos_reprovacao = request.POST[motivos_key]
                elif request.POST[teste_visual_key] == "Aprovado":
                    teste_visual.motivos_reprovacao = ""  # Limpar motivos se aprovado
                
                teste_visual.save()
                
                # Se teste visual reprovado, marcar ensaio como "Não Realizado" automaticamente
                if request.POST[teste_visual_key] == "Reprovado":
                    if solicitacao.ensaio == "DOBRAMENTO":
                        ensaio, _ = EnsaioMecanicoDobramento.objects.get_or_create(solicitacao=solicitacao)
                        ensaio.realizado = False
                        ensaio.aprovado = False
                        ensaio.save()
                    elif solicitacao.ensaio == "ULTRASSOM":
                        ensaio, _ = EnsaioUltrassom.objects.get_or_create(solicitacao=solicitacao)
                        ensaio.realizado = False
                        ensaio.aprovado = False
                        ensaio.save()

            # Ensaio Mecânico Dobramento (apenas se teste visual não for reprovado)
            if solicitacao.ensaio == "DOBRAMENTO":
                aprovado_key = f"dobramento_aprovado_{solicitacao.id}"
                if aprovado_key in request.POST and request.POST[aprovado_key]:
                    ensaio, _ = EnsaioMecanicoDobramento.objects.get_or_create(solicitacao=solicitacao)
                    resultado = request.POST[aprovado_key]
                    if resultado == "Nao_Realizado":
                        ensaio.realizado = False
                        ensaio.aprovado = False
                    else:
                        ensaio.realizado = True
                        ensaio.aprovado = resultado == "Aprovado"
                    ensaio.save()

            # Ensaio Ultrassom (apenas se teste visual não for reprovado)
            if solicitacao.ensaio == "ULTRASSOM":
                aprovado_key = f"ultrassom_aprovado_{solicitacao.id}"
                if aprovado_key in request.POST and request.POST[aprovado_key]:
                    ensaio, _ = EnsaioUltrassom.objects.get_or_create(solicitacao=solicitacao)
                    resultado = request.POST[aprovado_key]
                    if resultado == "Nao_Realizado":
                        ensaio.realizado = False
                        ensaio.aprovado = False
                    else:
                        ensaio.realizado = True
                        ensaio.aprovado = resultado == "Aprovado"
                    ensaio.save()
        messages.success(request, "Alterações salvas com sucesso!")
        return redirect("raqs_detail", raqs_id=raqs.id)

    # Group solicitações by soldador
    soldadores_dict = {}
    for solicitacao in raqs.solicitacoes.all().select_related('soldador').order_by('soldador__nome'):
        if solicitacao.soldador not in soldadores_dict:
            soldadores_dict[solicitacao.soldador] = []
        soldadores_dict[solicitacao.soldador].append(solicitacao)

    # Convert to list of tuples (soldador, solicitações) and sort by soldador name
    soldadores_list = sorted(soldadores_dict.items(), key=lambda x: x[0].nome)

    # Get all teste visual for solicitações in this RAQS
    testes_visuais = {}
    for solicitacao in raqs.solicitacoes.all():
        try:
            teste_visual = TesteVisual.objects.get(solicitacao=solicitacao)
            testes_visuais[solicitacao.id] = teste_visual
        except TesteVisual.DoesNotExist:
            testes_visuais[solicitacao.id] = None

    # Verificar se todos os testes foram preenchidos
    todos_testes_completos = True
    for solicitacao in raqs.solicitacoes.all():
        # Verificar teste visual
        teste_visual = testes_visuais.get(solicitacao.id)
        if not teste_visual or not teste_visual.resultado:
            todos_testes_completos = False
            break
        
        # Verificar ensaio específico
        if solicitacao.ensaio == 'DOBRAMENTO':
            ensaio_dobramento = EnsaioMecanicoDobramento.objects.filter(solicitacao=solicitacao).first()
            # Ensaio deve existir (indicando que foi processado no template)
            if not ensaio_dobramento:
                todos_testes_completos = False
                break
        elif solicitacao.ensaio == 'ULTRASSOM':
            ensaio_ultrassom = EnsaioUltrassom.objects.filter(solicitacao=solicitacao).first()
            # Ensaio deve existir (indicando que foi processado no template)
            if not ensaio_ultrassom:
                todos_testes_completos = False
                break

    context = {
        "raqs": raqs,
        "soldadores_list": soldadores_list,
        "lista_verificacoes_choices": TesteVisual.LISTA_VERIFICA_CHOICES,
        "testes_visuais": testes_visuais,
        "todos_testes_completos": todos_testes_completos,
    }
    return render(request, "raqs/raqs_detail.html", context)
