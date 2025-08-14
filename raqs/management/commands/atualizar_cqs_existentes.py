from django.core.management.base import BaseCommand
from django.db import models
from raqs.models import CQS


class Command(BaseCommand):
    help = 'Atualiza campos técnicos dos CQS existentes que estão vazios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quantos CQS seriam atualizados sem atualizar de fato',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar CQS com campos vazios ou None
        cqs_para_atualizar = CQS.objects.filter(
            # Pelo menos um campo técnico vazio
            models.Q(fq_consumivel__isnull=True) | 
            models.Q(fq_consumivel='') |
            models.Q(fq_metal_de_base__isnull=True) | 
            models.Q(fq_metal_de_base='') |
            models.Q(pn_metal_de_base__isnull=True) | 
            models.Q(pn_metal_de_base='')
        ).exclude(solicitacao__isnull=True)  # Só CQS com solicitação
        
        self.stdout.write(f'Encontrados {cqs_para_atualizar.count()} CQS para atualizar')
        
        if dry_run:
            self.stdout.write("=== DRY RUN - Nenhum CQS será atualizado ===")
            for cqs in cqs_para_atualizar:
                soldador = cqs.solicitacao.soldador.nome if cqs.solicitacao else "N/A"
                self.stdout.write(f"- Atualizaria: {cqs.numero} ({soldador})")
            return
        
        # Atualizar CQS
        atualizados = 0
        for cqs in cqs_para_atualizar:
            try:
                # Re-salvar para disparar o signal
                cqs.save()
                
                soldador = cqs.solicitacao.soldador.nome if cqs.solicitacao else "N/A"
                self.stdout.write(
                    self.style.SUCCESS(f'✅ CQS atualizado: {cqs.numero} ({soldador})')
                )
                atualizados += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao atualizar {cqs.numero}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total de CQS atualizados: {atualizados}')
        )