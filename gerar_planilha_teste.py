import pandas as pd
import random

# Vamos simular o caos que acontece na vida real!
# Note que "Medicina 2024" aparece escrito de 3 formas diferentes.

dados = {
    'Nº Controle 1': [
        'Medicina 2024', 'MEDICINA 24', 'Med 2024', # Mesma turma
        'Direito USP', 'Dir. USP 23', 'Direito USP 2023', # Outra turma
        'Engenharia Civil', 'Eng Civil', 'Civil 2025' # Outra turma
    ] * 50, # Repetimos isso 50 vezes para dar volume
    
    'Recebido': [random.uniform(5000, 15000) for _ in range(450)],
    'Pago': [random.uniform(2000, 10000) for _ in range(450)],
    'Instituicao': ['Universidade A'] * 450
}

# Criamos um DataFrame (uma tabela na memória)
df = pd.DataFrame(dados)

# Salvamos como Excel
df.to_excel("dados_financeiros.xlsx", index=False)
print("Planilha 'dados_financeiros.xlsx' criada com sucesso! Pode conferir na pasta.")