import streamlit as st
import pandas as pd
import plotly.express as px
import re
import unicodedata
import io
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="BI Dash Cloud", layout="wide")

# Inicializa o contador de sincronização na memória da sessão (Session State)
if 'sync_count' not in st.session_state:
    st.session_state.sync_count = 0

# LINKS DAS PLANILHAS GOOGLE
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1s8xsAxURlMzZrD5Q9hyQP4lsx0hR6udRqmu7quyRiEs/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) # Reduzido para 1 minuto para maior sensibilidade
def buscar_dados_google(url):
    try:
        return conn.read(spreadsheet=url)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

# --- FUNÇÕES DE MOTOR ---

def limpar_valor(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(texto)
    except ValueError:
        return 0.0

def extrair_id(texto):
    match = re.search(r'^\d+', str(texto).strip())
    return match.group(0) if match else None

def gerar_sugestao(texto):
    sugestao = re.sub(r'\s+\d+[\d\s.]*$', '', str(texto))
    return sugestao.upper().strip()

# --- INTERFACE E PROCESSAMENTO ---

st.title("📊 BI Financeiro: Atualização Automática")

# BOTÃO DE SINCRONIZAÇÃO (MELHORADO)
if st.sidebar.button("🔄 Sincronizar Tudo"):
    st.cache_data.clear()
    st.session_state.sync_count += 1 # Incrementa a versão para resetar o filtro
    st.sidebar.success(f"Sincronização v{st.session_state.sync_count} concluída!")
    st.rerun()

df_map_bruto = buscar_dados_google(URL_MAPEAMENTO)
df_fin_bruto = buscar_dados_google(URL_FINANCEIRO)

if not df_fin_bruto.empty:
    # A. Processamento do Mapeamento
    df_map = df_map_bruto.copy()
    df_map.columns = [str(c).strip().capitalize() for c in df_map.columns]
    mapa_id = {}
    if 'De' in df_map.columns and 'Para' in df_map.columns:
        df_validos = df_map.dropna(subset=['Para'])
        for _, row in df_validos.iterrows():
            id_vinc = extrair_id(row['De'])
            if id_vinc: mapa_id[id_vinc] = str(row['Para']).upper()

    # B. Processamento Financeiro
    df_dados = df_fin_bruto.copy()
    df_dados.columns = [str(c).strip() for c in df_dados.columns]
    df_dados['Valor_Limpo'] = df_dados['Valor'].apply(limpar_valor)
    
    # Cálculos Financeiros
    df_dados['Recebido'] = df_dados.apply(lambda x: x['Valor_Limpo'] if str(x['Tipo']).lower() == 'recebido' else 0, axis=1)
    df_dados['Pago'] = df_dados.apply(lambda x: abs(x['Valor_Limpo']) if str(x['Tipo']).lower() == 'pago' else 0, axis=1)
    
    # Padronização Dinâmica (Regra do ID)
    def aplicar_padrao(val):
        id_at = extrair_id(val)
        if not id_at: return "NÃO INFORMADO"
        if id_at in mapa_id: return mapa_id[id_at]
        return gerar_sugestao(val)

    df_dados['Turma_Padronizada'] = df_dados['Nº Controle 1'].apply(aplicar_padrao)

    # --- C. EXIBIÇÃO DE MÉTRICAS ---
    rec, pag = df_dados['Recebido'].sum(), df_dados['Pago'].sum()
    lucro = rec - pag
    roi = (lucro / pag * 100) if pag > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Receita Total", f"R$ {rec:,.2f}")
    m2.metric("Despesa Total", f"R$ {pag:,.2f}")
    m3.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
    m4.metric("ROI Geral", f"{roi:.1f}%")

    # --- D. FILTRO DINÂMICO (CORREÇÃO) ---
    st.markdown("### 🔍 Detalhamento por Turma")
    
    # Pega todas as turmas agora presentes no dataframe atualizado
    turmas_atuais = sorted(df_dados['Turma_Padronizada'].unique())
    
    # O segredo está no 'key': ao mudar o sync_count, o filtro é forçado a atualizar a lista
    selecao = st.multiselect(
        "Selecione as turmas para filtrar:", 
        options=turmas_atuais, 
        default=turmas_atuais[:5] if len(turmas_atuais) > 5 else turmas_atuais,
        key=f"filtro_turmas_{st.session_state.sync_count}" # FIX: Resolve o problema de sincronização
    )

    if selecao:
        df_f = df_dados[df_dados['Turma_Padronizada'].isin(selecao)]
        
        # Gráfico
        resumo = df_f.groupby('Turma_Padronizada')['Recebido'].sum().reset_index()
        fig = px.bar(resumo.sort_values(by='Recebido', ascending=False), 
                     x='Turma_Padronizada', y='Recebido', text_auto='.2s', 
                     color='Recebido', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

        # Tabela (QA)
        st.subheader("📋 Auditoria de Dados")
        st.dataframe(df_f[['Nº Controle 1', 'Turma_Padronizada', 'Tipo', 'Valor']], use_container_width=True)

else:
    st.warning("⚠️ Planilha financeira vazia ou não encontrada. Verifique os dados no Google Sheets.")