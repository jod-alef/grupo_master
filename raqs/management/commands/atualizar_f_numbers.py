from django.core.management.base import BaseCommand
from django.db import models
from raqs.models import SolicitacaoCadastroSoldador


class Command(BaseCommand):
    help = 'Atualiza f_numbers das solicitações existentes baseado no consumível'

    def handle(self, *args, **options):
        # Mapeamento de consumível para f_number (baseado em CONSUMIVEL_CLASS_CHOICES)
        f_number_mapping = {
            "E7018": "4",
            "E6010": "3",
            "E-71T-1": "6",
            "E-309L": "5",
            "ER-70S-3": "6",
            "ER-70S-6": "6",
            "ER-309L": "6",
            "ER-308L": "6",
            "ER-NiCrFe3": "43",
            "E-NiCrFe3": "43",
            "ER-NiCrMo3": "43",
        }
        
        solicitacoes = SolicitacaoCadastroSoldador.objects.filter(
            models.Q(f_number__isnull=True) | models.Q(f_number='')
        )
        
        self.stdout.write(f'Encontradas {solicitacoes.count()} solicitações sem f_number')
        
        atualizadas = 0
        for sol in solicitacoes:
            classificacao = sol.consumivel_classificacao
            if classificacao in f_number_mapping:
                sol.f_number = f_number_mapping[classificacao]
                sol.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {classificacao} → f_number={sol.f_number}')
                )
                atualizadas += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Consumível não mapeado: {classificacao}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total atualizadas: {atualizadas}')
        )