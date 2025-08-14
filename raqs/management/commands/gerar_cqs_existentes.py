from django.core.management.base import BaseCommand
from raqs.models import SolicitacaoCadastroSoldador, CQS, EnsaioMecanicoDobramento, EnsaioUltrassom, TesteVisual
from django.utils import timezone


class Command(BaseCommand):
    help = 'Gera CQS para solicitações aprovadas que ainda não possuem certificado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantos CQS seriam criados sem criar de fato',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se já existir CQS',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        # Buscar solicitações aprovadas sem CQS
        solicitacoes_aprovadas = []
        
        for solicitacao in SolicitacaoCadastroSoldador.objects.all():
            # Verificar se já tem CQS (pular se tiver, exceto se --force)
            if hasattr(solicitacao, 'cqs') and not force:
                continue
                
            # Verificar se está aprovada
            aprovada = self.verificar_aprovacao(solicitacao)
            
            if aprovada:
                solicitacoes_aprovadas.append(solicitacao)
        
        self.stdout.write(
            f'Encontradas {len(solicitacoes_aprovadas)} solicitações aprovadas '
            f'{"sem CQS" if not force else "(incluindo com CQS existente)"}'
        )
        
        if dry_run:
            self.stdout.write("=== DRY RUN - Nenhum CQS será criado ===")
            for solicitacao in solicitacoes_aprovadas:
                self.stdout.write(f"- Criaria CQS para: {solicitacao.soldador.nome} ({solicitacao.empresa.nome})")
            return
        
        # Criar CQS para solicitações aprovadas
        criados = 0
        for solicitacao in solicitacoes_aprovadas:
            try:
                if force and hasattr(solicitacao, 'cqs'):
                    # Deletar CQS existente se --force
                    solicitacao.cqs.delete()
                
                cqs = CQS.objects.create(
                    solicitacao=solicitacao,
                    data_emissao=timezone.now().date(),
                    # Campos técnicos serão preenchidos pelo signal
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ CQS criado: {cqs.numero} para {solicitacao.soldador.nome}')
                )
                criados += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar CQS para {solicitacao.soldador.nome}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total de CQS criados: {criados}')
        )
    
    def verificar_aprovacao(self, solicitacao):
        """
        Verifica se uma solicitação está aprovada baseado nos critérios:
        - Teste Visual aprovado E
        - Ensaio Mecânico (Dobramento OU Ultrassom) aprovado
        """
        try:
            # Verificar Teste Visual
            teste_visual = TesteVisual.objects.get(solicitacao=solicitacao)
            if teste_visual.resultado != "Aprovado":
                return False
            
            # Verificar Ensaios Mecânicos
            if solicitacao.ensaio == "DOBRAMENTO":
                ensaio = EnsaioMecanicoDobramento.objects.filter(
                    solicitacao=solicitacao, 
                    aprovado=True, 
                    realizado=True
                ).exists()
            elif solicitacao.ensaio == "ULTRASSOM":
                ensaio = EnsaioUltrassom.objects.filter(
                    solicitacao=solicitacao, 
                    aprovado=True, 
                    realizado=True
                ).exists()
            else:
                return False
            
            return ensaio
            
        except TesteVisual.DoesNotExist:
            return False