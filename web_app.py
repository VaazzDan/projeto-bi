import streamlit as st
import pandas as pd
import plotly.express as px
import re
import unicodedata
import io
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portal Dash Cloud", layout="wide")

# Inicializa estado de sincronização para resetar filtros
if 'sync_count' not in st.session_state:
    st.session_state.sync_count = 0

# --- CONSTANTES E LINKS ---
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1s8xsAxURlMzZrD5Q9hyQP4lsx0hR6udRqmu7quyRiEs/edit?usp=sharing"
# Link Público do Power BI
LINK_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiMzM0YTg4NjEtZjkyNy00NGNkLTgwZmUtNzM0MDRmNGQ0MzcwIiwidCI6IjY1OWNlMmI4LTA3MTQtNDE5OC04YzM4LWRjOWI2MGFhYmI1NyJ9"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONEXÃO COM CACHE CURTO (1 min) ---
@st.cache_data(ttl=60)
def buscar_dados_google(url, nome_log):
    try:
        df = conn.read(spreadsheet=url)
        if df.empty:
            st.warning(f"⚠️ A planilha '{nome_log}' retornou vazia.")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao conectar em '{nome_log}': {e}")
        return pd.DataFrame()

# --- FUNÇÕES DO MOTOR (REGRAS DE NEGÓCIO) ---

def limpar_valor(valor):
    """Converte moeda (texto) para float, evitando erro de abs()."""
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(texto)
    except ValueError:
        return 0.0

def normalizar_texto(texto):
    """Remove acentos e caracteres especiais (inclusive º e ª)."""
    if pd.isna(texto) or str(texto).strip() == "": return ""
    texto = str(texto).replace('º', ' ').replace('ª', ' ')
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    texto = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto)
    return " ".join(texto.split()).lower()

def extrair_id(texto):
    """Extrai o ID numérico à esquerda."""
    match = re.search(r'^\d+', str(texto).strip())
    return match.group(0) if match else None

def gerar_sugestao(texto):
    """Remove sufixos numéricos à direita."""
    sugestao = re.sub(r'\s+\d+[\d\s.]*$', '', str(texto))
    return sugestao.upper().strip()

# --- INTERFACE E NAVEGAÇÃO ---

st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["Processador de Dados", "Relatório Power BI"])

# ---------------------------------------------------------
# PÁGINA 1: RELATÓRIO POWER BI (CORRIGIDO PARA FILTROS)
# ---------------------------------------------------------
if pagina == "Relatório Power BI":
    st.title("📊 RELATÓRIOS FRAME 2025")
    st.markdown("Visualização oficial integrada.")
    
    # Uso de HTML direto para garantir que scripts de filtros funcionem
    st.markdown(
        f"""
        <iframe 
            title="Relatório Power BI" 
            width="100%" 
            height="800" 
            src="{LINK_POWER_BI}" 
            frameborder="0" 
            allowFullScreen="true">
        </iframe>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# PÁGINA 2: MOTOR DE PROCESSAMENTO
# ---------------------------------------------------------
elif pagina == "Processador de Dados":
    st.title("🛠️ Motor de Tratamento Financeiro")
    
    # Botão de Sincronização com Versionamento para Filtros
    if st.sidebar.button("🔄 Sincronizar Tudo"):
        st.cache_data.clear()
        st.session_state.sync_count += 1
        st.sidebar.success(f"Dados atualizados! (v{st.session_state.sync_count})")
        st.rerun()

    # Carregamento
    with st.spinner("Buscando dados no Google Sheets..."):
        df_map_bruto = buscar_dados_google(URL_MAPEAMENTO, "Mapeamento")
        df_fin_bruto = buscar_dados_google(URL_FINANCEIRO, "Financeiro")

    if not df_fin_bruto.empty:
        # QA: Validação de Colunas Obrigatórias
        cols_obrigatorias = ['Nº Controle 1', 'Tipo', 'Valor']
        cols_atuais = [str(c).strip() for c in df_fin_bruto.columns]
        falta = [c for c in cols_obrigatorias if c not in cols_atuais]
        
        if falta:
            st.error(f"🚨 ERRO CRÍTICO: Colunas não encontradas na planilha financeira: {falta}")
            st.stop()

        # A. Preparação do Mapeamento
        df_map = df_map_bruto.copy()
        mapa_id = {}
        if not df_map.empty:
            df_map.columns = [str(c).strip().capitalize() for c in df_map.columns]
            if 'De' in df_map.columns and 'Para' in df_map.columns:
                df_validos = df_map.dropna(subset=['Para'])
                for _, row in df_validos.iterrows():
                    id_vinc = extrair_id(row['De'])
                    if id_vinc: mapa_id[id_vinc] = str(row['Para']).upper()

        # B. Processamento Financeiro
        df_dados = df_fin_bruto.copy()
        df_dados.columns = [str(c).strip() for c in df_dados.columns]
        
        # Tratamento seguro de valores
        df_dados['Valor_Limpo'] = df_dados['Valor'].apply(limpar_valor)
        df_dados['Recebido'] = df_dados.apply(lambda x: x['Valor_Limpo'] if str(x['Tipo']).lower() == 'recebido' else 0, axis=1)
        df_dados['Pago'] = df_dados.apply(lambda x: abs(x['Valor_Limpo']) if str(x['Tipo']).lower() == 'pago' else 0, axis=1)
        
        # Lógica de Padronização
        def aplicar_padrao(val):
            id_at = extrair_id(val)
            if not id_at: return "NÃO INFORMADO"
            if id_at in mapa_id: return mapa_id[id_at]
            return gerar_sugestao(val)

        df_dados['Turma_Padronizada'] = df_dados['Nº Controle 1'].apply(aplicar_padrao)

        # C. KPIs e Métricas
        rec, pag = df_dados['Recebido'].sum(), df_dados['Pago'].sum()
        lucro = rec - pag
        roi = (lucro / pag * 100) if pag > 0 else 0

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Receita Total", f"R$ {rec:,.2f}")
        c2.metric("Despesa Total", f"R$ {pag:,.2f}")
        c3.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
        c4.metric("ROI Geral", f"{roi:.1f}%")

        # D. Visualização Interativa
        turmas_atuais = sorted(df_dados['Turma_Padronizada'].unique())
        
        # Filtro com chave dinâmica para forçar atualização visual
        selecao = st.multiselect(
            "Filtrar Turmas:", 
            options=turmas_atuais, 
            default=turmas_atuais[:5] if len(turmas_atuais) > 5 else turmas_atuais,
            key=f"filtro_turmas_{st.session_state.sync_count}"
        )
        
        if selecao:
            df_f = df_dados[df_dados['Turma_Padronizada'].isin(selecao)]
            
            # Gráfico
            resumo = df_f.groupby('Turma_Padronizada')['Recebido'].sum().reset_index()
            fig = px.bar(
                resumo.sort_values(by='Recebido', ascending=False), 
                x='Turma_Padronizada', y='Recebido', 
                text_auto='.2s', color='Recebido', 
                color_continuous_scale='Viridis', title="Faturamento por Turma"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tabela de Auditoria
            st.subheader("📋 Auditoria de Dados")
            st.dataframe(df_f[['Nº Controle 1', 'Turma_Padronizada', 'Tipo', 'Valor']], use_container_width=True)

    else:
        st.warning("⚠️ Aguardando dados do Google Sheets...")