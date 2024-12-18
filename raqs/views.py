from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from raqs.forms import SoldadorForm, SolicitacaoCadastroSoldadorForm
from raqs.models import *


def solicitacao_qualificacao_soldador(request, soldador_id=None):
    soldador = get_object_or_404(Soldador, id=soldador_id) if soldador_id else None
    empresa = get_object_or_404(Empresa, usuarios__id=request.user.id)  # Get the company via the current user

    if request.method == "POST":
        form = SolicitacaoCadastroSoldadorForm(request.POST)
        if form.is_valid():
            # Save the form, setting the empresa and soldador fields explicitly
            solicitacao = form.save(commit=False)
            solicitacao.soldador = soldador
            solicitacao.empresa = empresa
            solicitacao.save()

            if 'add_another' in request.POST:
                return redirect('solicitacao-qualificacao-soldador', soldador_id=soldador_id)
            elif "save_and_return" in request.POST:
                return redirect('empresa-dashboard')
        else:
            print(form.errors)  # For debugging, remove in production

    else:
        # Pre-fill the empresa and soldador fields in the form
        form = SolicitacaoCadastroSoldadorForm(initial={'soldador': soldador, 'empresa': empresa})

    return render(request, 'solicitacao_qualificacao_soldador.html', {
        'form': form,
        'soldador': soldador,
        'empresa': empresa,
        'error_messages': form.errors,
    })


def cadastro_soldador(request):
    if request.method == "POST":
        form = SoldadorForm(request.POST)
        if form.is_valid():
            soldador = form.save()
            if "add_solicitacao" in request.POST:
                return redirect("solicitacao-qualificacao-soldador", soldador_id=soldador.id)
            elif "add_another" in request.POST:
                return render(request, "cadastro_soldador.html", {'form': form})
            return redirect('solicitacao_qualificacao_soldador', soldador_id=soldador.id)  # Redirect to next form
    else:
        form = SoldadorForm()
    return render(request, 'cadastro_soldador.html', {'form': form})


def update_ensaio_choices(request):
    norma_projeto = request.GET.get('norma_projeto', '').strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("Norma de projeto:", norma_projeto)

    # Dynamically adjust the `ensaio` field based on `norma_projeto`
    if norma_projeto in ["AWS_D1-1", "AWS D1.1 - 2020"]:
        form.fields['ensaio'].choices = [
            ("DOBRAMENTO", "Dobramento Mecânico")
        ]
    else:
        form.fields['ensaio'].choices = [
            ("DOBRAMENTO", "Dobramento Mecânico"),
            ("ULTRASSOM", "Ultrassom")
        ]

    # Render the updated `ensaio` field

    return render (request,'partials/ensaio_field.html', {'field': form['ensaio']})


def list_soldadores(request):
    soldadores = Soldador.objects.all()
    return render(request, 'list_soldadores.html', {'soldadores': soldadores})


def update_metal_fields(request):
    # Obtenha o valor enviado pelo HTMX
    metal_base_spec = request.GET.get('metal_base_spec', '').strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("A escolha foi:", metal_base_spec)  # Para depuração

    # Ajuste os campos com base na escolha
    if metal_base_spec in ["A-36", "SB536", "A-309", "A-312"]:
        form.fields['metal_base_espessura'].disabled = False
        form.fields['metal_base_diametro'].disabled = True
        form.fields['posicao_soldagem'].choices = [
            choice for choice in form.fields['posicao_soldagem'].choices
            if choice[0] not in ["5G", "6G"]
        ]
    elif metal_base_spec in ["A-106", "16MO3"]:
        form.fields['metal_base_espessura'].disabled = True
        form.fields['metal_base_diametro'].disabled = False
        form.fields['posicao_soldagem'].choices = [
            choice for choice in form.fields['posicao_soldagem'].choices
            if choice[0] not in ["3G", "4G"]
        ]

    # Renderize os campos dinâmicos
    return render(request, 'partials/metal_fields.html', {'form': form})

def update_progressao_choices(request):
    posicao_soldagem = request.GET.get('posicao_soldagem', '').strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("Posição de Soldagem:", posicao_soldagem)

    # Dynamically adjust the `ensaio` field based on `norma_projeto`
    if posicao_soldagem in ["6G"]:
        form.fields['posicao_soldagem_progressao'].disabled = False
        form.fields['posicao_soldagem_progressao'].choices = [
            ("ASCENDENTE", "Ascendente")
        ]
    elif posicao_soldagem in ["3G", "3F", "5G"]:
        form.fields['posicao_soldagem_progressao'].disabled = False
        form.fields['posicao_soldagem_progressao'].choices = [
            ("ASCENDENTE", "Ascendente"),
            ("DESCENDENTE", "Descendente"),
        ]
    else:
        form.fields['posicao_soldagem_progressao'].readonly = True

    # Render the updated `ensaio` field

    return render (request,'partials/progressao_field.html', {'field': form['posicao_soldagem_progressao']})


def update_gas_protecao(request):
    processo_soldagem = request.GET.get('processo_soldagem', '').strip()
    form = SolicitacaoCadastroSoldadorForm()
    print("Processo de Soldagem:", processo_soldagem)

    # Dynamically adjust the `ensaio` field based on `norma_projeto`
    if processo_soldagem in ["GTAW"]:
        form.fields['gas_protecao'].disabled = False
        form.fields['gas_protecao'].choices = [
            ("ARGONIO", "Argônio")
        ]
    elif processo_soldagem in ["GMAW"]:
        form.fields['gas_protecao'].disabled = False
        form.fields['gas_protecao'].choices = [
            ("ARCO2", "Ar+CO²"),
        ]
    elif processo_soldagem in ["FCAW"]:
        form.fields['gas_protecao'].disabled = False
        form.fields['gas_protecao'].choices = [
            ("CO2", "CO²"),
        ]
    else:
        form.fields['gas_protecao'].readonly = True
        form.fields['gas_protecao'].choices = [
            ("NA", "N/A"),
        ]

    # Render the updated `ensaio` field

    return render (request,'partials/gas_protec_field.html', {'field': form['gas_protecao']})


@login_required
def empresa_dashboard(request):
    empresa = get_object_or_404(Empresa, usuarios__id=request.user.id)
    soldadores = SolicitacaoCadastroSoldador.objects.filter(empresa=empresa)

    soldador_status = {}
    for solicitacao in soldadores:
        status = "Aguardando Teste"
        if EnsaioMecanicoDobramento.objects.filter(solicitacao=solicitacao, aprovado=True).exists():
            status = "Aprovado - DM"
        elif EnsaioUltrassom.objects.filter(solicitacao=solicitacao, aprovado=True).exists():
            status = "Aprovado - UT"

        soldador_status[solicitacao.soldador.id] = status
        print(status)

    return render(request, 'empresa_dashboard.html', {
        'empresa': empresa,
        'soldadores': soldadores,
        'soldador_status': soldador_status
    })


def verificar_cpf_htmx(request):
    cpf = request.GET.get('cpf', '').strip()
    soldador = Soldador.objects.filter(cpf=cpf).first()

    if soldador:
        return render(request, 'partials/existente_soldador.html', {'soldador': soldador})
    return render(request, 'partials/novo_soldador.html')