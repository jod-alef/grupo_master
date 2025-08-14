from django.core.management.base import BaseCommand
from raqs.models import CQS, EnsaioMecanicoDobramento, EnsaioUltrassom
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
    help = 'Atualiza data de validade dos CQS existentes (6 meses após aprovação dos ensaios)'

    def handle(self, *args, **options):
        cqs_sem_validade = CQS.objects.filter(data_validade__isnull=True)
        total_cqs = cqs_sem_validade.count()
        
        self.stdout.write(f"Encontrados {total_cqs} CQS sem data de validade")
        
        if total_cqs == 0:
            self.stdout.write("Nenhum CQS para atualizar.")
            return
        
        atualizados = 0
        nao_encontrados = 0
        
        for cqs in cqs_sem_validade:
            if not cqs.solicitacao:
                self.stdout.write(f"⚠️ CQS {cqs.numero} sem solicitação vinculada")
                continue
                
            solicitacao = cqs.solicitacao
            data_aprovacao = None
            tipo_ensaio = ""
            
            # Buscar data de aprovação do ensaio mecânico
            try:
                ensaio_mecanico = EnsaioMecanicoDobramento.objects.get(
                    solicitacao=solicitacao, aprovado=True
                )
                data_aprovacao = ensaio_mecanico.data_teste
                tipo_ensaio = "Mecânico"
            except EnsaioMecanicoDobramento.DoesNotExist:
                pass
            
            # Se não encontrou mecânico aprovado, buscar ultrassom
            if not data_aprovacao:
                try:
                    ensaio_ultrassom = EnsaioUltrassom.objects.get(
                        solicitacao=solicitacao, aprovado=True
                    )
                    data_aprovacao = ensaio_ultrassom.data_teste
                    tipo_ensaio = "Ultrassom"
                except EnsaioUltrassom.DoesNotExist:
                    pass
            
            # Se encontrou data de aprovação, calcular validade
            if data_aprovacao:
                data_validade = data_aprovacao + relativedelta(months=6)
                cqs.data_validade = data_validade
                cqs.save()
                
                self.stdout.write(
                    f"✅ {cqs.numero}: {data_aprovacao} ({tipo_ensaio}) → Válido até {data_validade}"
                )
                atualizados += 1
            else:
                self.stdout.write(
                    f"❌ {cqs.numero}: Nenhum ensaio aprovado encontrado"
                )
                nao_encontrados += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Resumo:')
        )
        self.stdout.write(f"✅ {atualizados} CQS atualizados com data de validade")
        self.stdout.write(f"❌ {nao_encontrados} CQS sem ensaios aprovados")
        
        if nao_encontrados > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\nAtenção: {nao_encontrados} CQS não puderam ser atualizados "
                    "por não terem ensaios aprovados vinculados."
                )
            )