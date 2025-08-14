import csv
from django.core.management.base import BaseCommand
from raqs.models import SolicitacaoCadastroSoldador


class Command(BaseCommand):
    help = 'Corrige consumíveis no banco baseado no CSV de regras'

    def handle(self, *args, **options):
        # Mapeamento de correção (banco → CSV)
        correcoes = {
            "E6010": "E-6010",
            "E-71T-1": "E-71T1", 
            "ER-70S-3": "ER-70S3",
            "ER-309": "ER-309L",  # Assumindo que ER-309 deveria ser ER-309L
            "E-309": "E-309L",    # Assumindo que E-309 deveria ser E-309L
        }
        
        # Ler F-numbers do CSV
        f_numbers_csv = {}
        with open('static/regras_classificacao.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                f_numbers_csv[row['Classificação']] = row['F N°']
        
        self.stdout.write("=== CORREÇÕES PLANEJADAS ===")
        for antigo, novo in correcoes.items():
            count = SolicitacaoCadastroSoldador.objects.filter(consumivel_classificacao=antigo).count()
            f_number = f_numbers_csv.get(novo, "N/A")
            self.stdout.write(f"{antigo} → {novo} (F#{f_number}) - {count} registros")
        
        confirma = input("\nConfirma as correções? (s/N): ")
        if confirma.lower() != 's':
            self.stdout.write("Operação cancelada")
            return
        
        # Aplicar correções
        total_corrigidas = 0
        for antigo, novo in correcoes.items():
            solicitacoes = SolicitacaoCadastroSoldador.objects.filter(consumivel_classificacao=antigo)
            count = solicitacoes.count()
            
            if count > 0:
                # Atualizar consumível e f_number
                for sol in solicitacoes:
                    sol.consumivel_classificacao = novo
                    sol.f_number = f_numbers_csv.get(novo, "")
                    sol.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {count} registros: {antigo} → {novo}')
                )
                total_corrigidas += count
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total corrigidas: {total_corrigidas} solicitações')
        )
        
        # Mostrar status final
        self.stdout.write("\n=== STATUS FINAL ===")
        consumiveis_finais = SolicitacaoCadastroSoldador.objects.values_list(
            'consumivel_classificacao', flat=True
        ).distinct()
        
        for c in consumiveis_finais:
            if c in f_numbers_csv:
                self.stdout.write(f"✅ {c} (F#{f_numbers_csv[c]})")
            else:
                self.stdout.write(f"❌ {c} (não mapeado)")