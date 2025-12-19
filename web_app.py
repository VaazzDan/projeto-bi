import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import unicodedata
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO VISUAL (TEMA) ---
st.set_page_config(
    page_title="Portal Dash Cloud", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa estado de sincronização
if 'sync_count' not in st.session_state:
    st.session_state.sync_count = 0

# --- LINKS ---
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1s8xsAxURlMzZrD5Q9hyQP4lsx0hR6udRqmu7quyRiEs/edit?usp=sharing"

# LINK ATUALIZADO (PÚBLICO)
LINK_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiMzM0YTg4NjEtZjkyNy00NGNkLTgwZmUtNzM0MDRmNGQ0MzcwIiwidCI6IjY1OWNlMmI4LTA3MTQtNDE5OC04YzM4LWRjOWI2MGFhYmI1NyJ9"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    /* Estilo para os Cards de KPI */
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Ajuste para o Iframe do Power BI ocupar bem a tela */
    iframe {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def buscar_dados_google(url, nome_log):
    try:
        df = conn.read(spreadsheet=url)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# --- FUNÇÕES MOTOR ---
def limpar_valor(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try: return float(texto)
    except: return 0.0

def normalizar_texto(texto):
    if pd.isna(texto): return ""
    texto = str(texto).replace('º', ' ').replace('ª', ' ')
    nfkd = unicodedata.normalize('NFKD', texto)
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', "".join([c for c in nfkd if not unicodedata.combining(c)])).lower()

def extrair_id(texto):
    match = re.search(r'^\d+', str(texto).strip())
    return match.group(0) if match else None

def gerar_sugestao(texto):
    return re.sub(r'\s+\d+[\d\s.]*$', '', str(texto)).upper().strip()

# --- INTERFACE ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2920/2920323.png", width=40)
st.sidebar.title("Navegação")
# Reorganizei para o Power BI ser a primeira opção, já que é o foco visual
pagina = st.sidebar.radio("Ir para:", ["Relatório Power BI", "Dashboard Executivo (Python)", "Auditoria de Dados"])

if pagina == "Relatório Power BI":
    st.title("📊 RELATÓRIOS FRAME 2025")
    # Uso de HTML direto para garantir responsividade (width=100%) e tela cheia
    st.markdown(f'''
        <iframe 
            title="RELATORIOS FRAME 2025" 
            width="100%" 
            height="700" 
            src="{LINK_POWER_BI}" 
            frameborder="0" 
            allowFullScreen="true">
        </iframe>
    ''', unsafe_allow_html=True)

elif pagina in ["Dashboard Executivo (Python)", "Auditoria de Dados"]:
    # Botão Sincronizar na Sidebar
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.session_state.sync_count += 1
        st.sidebar.success(f"Dados atualizados! (v{st.session_state.sync_count})")
        st.rerun()

    df_map_bruto = buscar_dados_google(URL_MAPEAMENTO, "Map")
    df_fin_bruto = buscar_dados_google(URL_FINANCEIRO, "Fin")

    if not df_fin_bruto.empty:
        # PROCESSAMENTO
        df_map = df_map_bruto.copy()
        mapa_id = {}
        if not df_map.empty:
            df_map.columns = [str(c).strip().capitalize() for c in df_map.columns]
            if 'De' in df_map.columns and 'Para' in df_map.columns:
                for _, row in df_map.dropna(subset=['Para']).iterrows():
                    id_v = extrair_id(row['De'])
                    if id_v: mapa_id[id_v] = str(row['Para']).upper()

        df_dados = df_fin_bruto.copy()
        df_dados.columns = [str(c).strip() for c in df_dados.columns]
        df_dados['Valor_Limpo'] = df_dados['Valor'].apply(limpar_valor)
        df_dados['Recebido'] = df_dados.apply(lambda x: x['Valor_Limpo'] if str(x['Tipo']).lower() == 'recebido' else 0, axis=1)
        df_dados['Pago'] = df_dados.apply(lambda x: abs(x['Valor_Limpo']) if str(x['Tipo']).lower() == 'pago' else 0, axis=1)
        
        def padronizar(val):
            id_at = extrair_id(val)
            if not id_at: return "NÃO INFORMADO"
            if id_at in mapa_id: return mapa_id[id_at]
            return gerar_sugestao(val)
        
        df_dados['Turma_Padronizada'] = df_dados['Nº Controle 1'].apply(padronizar)

        # --- PÁGINA 2: DASHBOARD EXECUTIVO (PYTHON) ---
        if pagina == "Dashboard Executivo (Python)":
            st.title("🚀 Visão Geral Financeira (Motor Interno)")
            
            with st.expander("🔍 Filtros Avançados", expanded=True):
                col_f1, col_f2 = st.columns([1, 3])
                turmas_unicas = sorted(df_dados['Turma_Padronizada'].unique())
                
                with col_f1:
                    ver_todas = st.toggle("Selecionar Todas as Turmas", value=False)
                
                with col_f2:
                    if ver_todas:
                        st.info(f"📊 Visualizando todas as {len(turmas_unicas)} turmas.")
                        selecao = turmas_unicas
                    else:
                        selecao = st.multiselect(
                            "Selecione as Turmas:", 
                            options=turmas_unicas,
                            default=turmas_unicas[:5] if len(turmas_unicas) > 5 else turmas_unicas,
                            key=f"filtro_pro_{st.session_state.sync_count}"
                        )

            df_filtrado = df_dados[df_dados['Turma_Padronizada'].isin(selecao)] if selecao else df_dados.head(0)

            if not df_filtrado.empty:
                rec = df_filtrado['Recebido'].sum()
                pag = df_filtrado['Pago'].sum()
                lucro = rec - pag
                roi = (lucro / pag * 100) if pag > 0 else 0
                
                st.divider()
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Receita Total", f"R$ {rec:,.2f}", delta="Faturamento")
                kpi2.metric("Despesa Total", f"R$ {pag:,.2f}", delta="Custo", delta_color="inverse")
                kpi3.metric("Lucro Líquido", f"R$ {lucro:,.2f}", delta="Margem")
                kpi4.metric("ROI Geral", f"{roi:.1f}%", delta="Retorno")
                
                g1, g2 = st.columns([2, 1])
                with g1:
                    resumo_barras = df_filtrado.groupby('Turma_Padronizada')['Recebido'].sum().reset_index().sort_values('Recebido', ascending=True)
                    fig_bar = px.bar(
                        resumo_barras, x='Recebido', y='Turma_Padronizada', orientation='h',
                        text_auto='.2s', title="Ranking de Faturamento", color='Recebido', color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(xaxis_title="", yaxis_title="", height=450)
                    st.plotly_chart(fig_bar, use_container_width=True)

                with g2:
                    st.subheader("🏆 Top Lucratividade")
                    df_top = df_filtrado.groupby('Turma_Padronizada')[['Recebido', 'Pago']].sum().reset_index()
                    df_top['Lucro'] = df_top['Recebido'] - df_top['Pago']
                    st.dataframe(df_top.nlargest(10, 'Lucro')[['Turma_Padronizada', 'Lucro']], use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhuma turma selecionada.")

        # --- PÁGINA 3: AUDITORIA ---
        elif pagina == "Auditoria de Dados":
            st.title("📋 Auditoria de Qualidade")
            tab1, tab2 = st.tabs(["Base Completa", "Padrões Novos"])
            with tab1: st.dataframe(df_dados, use_container_width=True)
            with tab2:
                if mapa_id:
                    novos = df_dados[~df_dados['Turma_Padronizada'].isin(mapa_id.values())]
                    if not novos.empty: st.dataframe(novos[['Nº Controle 1', 'Turma_Padronizada']].drop_duplicates(), hide_index=True)
                    else: st.success("Sem novos padrões.")

    else:
        st.info("Aguardando conexão com Google Sheets...")