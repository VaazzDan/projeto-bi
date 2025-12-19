import pandas as pd
import re
import os
import unicodedata
from rapidfuzz import process, fuzz

# --- 1. FUNÇÕES DE NORMALIZAÇÃO E EXTRAÇÃO ---

def remover_acentos(texto):
    if pd.isna(texto): return ""
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def extrair_id_esquerda(texto):
    """Extrai apenas o primeiro número que aparece à esquerda."""
    match = re.search(r'^\d+', str(texto).strip())
    return match.group(0) if match else None

def gerar_sugestao_para(texto_de):
    """Remove números à direita e limpa o texto para sugestão."""
    if not texto_de: return ""
    # Remove números, pontos e espaços no final da string
    sugestao = re.sub(r'\s+\d+[\d\s.]*$', '', str(texto_de))
    return sugestao.upper().strip()

# --- 2. LÓGICA DE INTELIGÊNCIA POR ID ---

def aplicar_logica_id(texto_bruto, mapa_id, novos_termos_dict):
    """
    Regra: Se o ID à esquerda for igual, a padronização DEVE ser a mesma.
    """
    id_atual = extrair_id_esquerda(texto_bruto)
    texto_normalizado = remover_acentos(texto_bruto).lower().strip()
    
    if not id_atual:
        return "NÃO INFORMADO"

    # 1. Se o ID já existe no mapeamento ou foi descoberto nesta execução
    if id_atual in mapa_id:
        return mapa_id[id_atual]

    # 2. Se é um ID novo, gera a sugestão e salva na memória
    sugestao = gerar_sugestao_para(texto_normalizado)
    mapa_id[id_atual] = sugestao # Registra para as próximas linhas
    
    # Adiciona ao dicionário que será salvo no mapeamento_termos.xlsx
    novos_termos_dict[texto_normalizado] = sugestao
    
    return sugestao

# --- 3. EXECUÇÃO DO PROCESSO ---

def gerenciar_mapeamento():
    caminho = "mapeamento_termos.xlsx"
    if not os.path.exists(caminho):
        pd.DataFrame(columns=['De', 'Para']).to_excel(caminho, index=False)
        return pd.DataFrame(), {}

    df_map = pd.read_excel(caminho)
    df_map.columns = [str(c).strip().capitalize() for c in df_map.columns]
    
    # Criamos um mapa de ID -> PARA
    # Pegamos o ID da coluna 'De' e vinculamos ao valor da coluna 'Para'
    mapa_id = {}
    df_preenchidos = df_map.dropna(subset=['Para'])
    
    for _, row in df_preenchidos.iterrows():
        id_vinculado = extrair_id_esquerda(row['De'])
        if id_vinculado:
            mapa_id[id_vinculado] = str(row['Para']).upper()
            
    return df_map, mapa_id

def executar_processamento():
    print("🚀 Motor Projuris: Iniciando Padronização por ID...")
    try:
        df_dados = pd.read_excel("dados_financeiros.xlsx")
        df_map_original, mapa_id = gerenciar_mapeamento()
        novos_termos_descobertos = {} # {'De': 'Para_Sugerido'}

        # Processamento Financeiro
        df_dados['Recebido'] = df_dados.apply(lambda x: x['Valor'] if x['Tipo'] == 'Recebido' else 0, axis=1)
        df_dados['Pago'] = df_dados.apply(lambda x: abs(x['Valor']) if x['Tipo'] == 'Pago' else 0, axis=1)
        
        # Aplicação da Regra de ID
        print("🔍 Vinculando turmas por ID numérico...")
        df_dados['Turma_Padronizada'] = df_dados['Nº Controle 1'].apply(
            lambda x: aplicar_logica_id(x, mapa_id, novos_termos_descobertos)
        )

        df_dados.to_excel("Resultado_Consultoria_Final.xlsx", index=False)
        
        # Atualização do Mapeamento
        if novos_termos_descobertos:
            novas_linhas = pd.DataFrame([
                {'De': k, 'Para': v} for k, v in novos_termos_descobertos.items()
            ])
            df_final_map = pd.concat([df_map_original, novas_linhas]).drop_duplicates(subset=['De'], keep='first')
            df_final_map.to_excel("mapeamento_termos.xlsx", index=False)
            print(f"✨ {len(novos_termos_descobertos)} novos IDs padronizados.")
        
        print("✅ Processo concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")

if __name__ == "__main__":
    executar_processamento()