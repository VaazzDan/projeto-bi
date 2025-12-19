import streamlit as st
import pandas as pd
import plotly.express as px
import re
import unicodedata
import io
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="BI Dash Automático", layout="wide")

# LINKS DAS PLANILHAS GOOGLE
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1s8xsAxURlMzZrD5Q9hyQP4lsx0hR6udRqmu7quyRiEs/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def buscar_dados_google(url):
    try:
        return conn.read(spreadsheet=url)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

# --- FUNÇÕES DE MOTOR (REVISADAS PARA TESTES) ---

def limpar_valor(valor):
    """Converte texto de moeda para número decimal. Resolve erro da imagem 71dace."""
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(texto)
    except ValueError:
        return 0.0

def normalizar_texto(texto):
    """
    Remove acentos e caracteres especiais. 
    CORREÇÃO (image_71ea14): Remove símbolos ordinais antes da decomposição Unicode.
    """
    if pd.isna(texto) or str(texto).strip() == "": return ""
    
    # Remove símbolos ordinais (º, ª) para evitar que se tornem 'o' ou 'a'
    texto = str(texto).replace('º', ' ').replace('ª', ' ')
    
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Mantém apenas letras, números e espaços
    texto = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto)
    return " ".join(texto.split()).lower()

def extrair_id(texto):
    """Identifica o ID numérico à esquerda."""
    match = re.search(r'^\d+', str(texto).strip())
    return match.group(0) if match else None

def gerar_sugestao(texto):
    """Limpa o nome da turma removendo sufixos numéricos."""
    sugestao = re.sub(r'\s+\d+[\d\s.]*$', '', str(texto))
    return sugestao.upper().strip()

# --- INTERFACE E PROCESSAMENTO ---

st.title("📊 BI Financeiro: Atualização Automática")

if st.sidebar.button("🔄 Sincronizar Tudo"):
    st.cache_data.clear()
    st.rerun()

df_map_bruto = buscar_dados_google(URL_MAPEAMENTO)
df_fin_bruto = buscar_dados_google(URL_FINANCEIRO)

if not df_fin_bruto.empty:
    # A. Mapeamento Cloud
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
    
    df_dados['Recebido'] = df_dados.apply(lambda x: x['Valor_Limpo'] if str(x['Tipo']).lower() == 'recebido' else 0, axis=1)
    df_dados['Pago'] = df_dados.apply(lambda x: abs(x['Valor_Limpo']) if str(x['Tipo']).lower() == 'pago' else 0, axis=1)
    
    def aplicar_padrao(val):
        id_at = extrair_id(val)
        if not id_at: return "NÃO INFORMADO"
        if id_at in mapa_id: return mapa_id[id_at]
        return gerar_sugestao(val)

    df_dados['Turma_Padronizada'] = df_dados['Nº Controle 1'].apply(aplicar_padrao)

    # --- MÉTRICAS ---
    rec, pag = df_dados['Recebido'].sum(), df_dados['Pago'].sum()
    lucro = rec - pag
    roi = (lucro / pag * 100) if pag > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Receita Total", f"R$ {rec:,.2f}")
    m2.metric("Despesa Total", f"R$ {pag:,.2f}")
    m3.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
    m4.metric("ROI Geral", f"{roi:.1f}%")

    # --- DASHBOARD ---
    turmas = sorted(df_dados['Turma_Padronizada'].unique())
    sel = st.multiselect("Filtrar Turmas:", options=turmas, default=turmas[:5])
    
    if sel:
        df_f = df_dados[df_dados['Turma_Padronizada'].isin(sel)]
        st.plotly_chart(px.bar(df_f.groupby('Turma_Padronizada')['Recebido'].sum().reset_index(), 
                               x='Turma_Padronizada', y='Recebido', text_auto='.2s', color_discrete_sequence=['#1F77B4']), use_container_width=True)
        st.dataframe(df_f[['Nº Controle 1', 'Turma_Padronizada', 'Tipo', 'Valor']], use_container_width=True)

else:
    st.warning("⚠️ Aguardando sincronização com as planilhas do Google Sheets...")