import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import unicodedata
import hmac
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Portal Dash Cloud", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE LOGIN (CORRIGIDO) ---
def check_password():
    """Gerencia a autenticação segura."""
    
    def password_entered():
        """Callback: Verifica a senha digitada."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["passwords"]["admin"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Limpa o campo de senha da memória
        else:
            st.session_state["password_correct"] = False

    # Se a chave existe e é True, libera o acesso
    if st.session_state.get("password_correct", False):
        return True

    # Layout da Tela de Login
    st.markdown("""
    <style>
        .stTextInput { max-width: 400px; margin: 0 auto; }
        .stButton { max-width: 400px; margin: 0 auto; display: block; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🔒 Portal Projuris - Acesso Restrito")
    st.markdown("Por favor, autentique-se para visualizar os dados financeiros.")
    
    st.text_input("Senha de Acesso:", type="password", on_change=password_entered, key="password")
    
    # LÓGICA CORRIGIDA: Só mostra erro se a chave existir E for False
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Senha incorreta. Verifique suas credenciais.")

    return False

if not check_password():
    st.stop()

# =========================================================
#  ÁREA RESTRITA (LOGADA)
# =========================================================

# Abre a sidebar automaticamente após login
if st.session_state.get("password_correct", False):
    st.markdown("<script>document.getElementsByClassName('stSidebar')[0].style.display = 'block';</script>", unsafe_allow_html=True)

# Inicializa estado
if 'sync_count' not in st.session_state:
    st.session_state.sync_count = 0

# CONSTANTES
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1s8xsAxURlMzZrD5Q9hyQP4lsx0hR6udRqmu7quyRiEs/edit?usp=sharing"
LINK_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiMzM0YTg4NjEtZjkyNy00NGNkLTgwZmUtNzM0MDRmNGQ0MzcwIiwidCI6IjY1OWNlMmI4LTA3MTQtNDE5OC04YzM4LWRjOWI2MGFhYmI1NyJ9"

conn = st.connection("gsheets", type=GSheetsConnection)

# CSS
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
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

# FUNÇÕES MOTOR
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

pagina = st.sidebar.radio("Ir para:", ["Relatório Power BI", "Dashboard Executivo (Python)", "Auditoria de Dados"])

# BOTÃO DE LOGOUT CORRIGIDO (Lógica de QA)
if st.sidebar.button("🔒 Sair / Logout"):
    # Remove as chaves de autenticação para resetar o estado para "Neutro"
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    if "password" in st.session_state:
        del st.session_state["password"]
    st.rerun()

# -------------------------------------
# PÁGINAS DO SISTEMA
# -------------------------------------

if pagina == "Relatório Power BI":
    st.title("📊 RELATÓRIOS FRAME 2025")
    st.markdown(f'<iframe title="Relatório Power BI" width="100%" height="700" src="{LINK_POWER_BI}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)

elif pagina in ["Dashboard Executivo (Python)", "Auditoria de Dados"]:
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.session_state.sync_count += 1
        st.sidebar.success(f"Dados atualizados! (v{st.session_state.sync_count})")
        st.rerun()

    df_map_bruto = buscar_dados_google(URL_MAPEAMENTO, "Map")
    df_fin_bruto = buscar_dados_google(URL_FINANCEIRO, "Fin")

    if not df_fin_bruto.empty:
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

        if pagina == "Dashboard Executivo (Python)":
            st.title("🚀 Visão Geral Financeira (Motor Interno)")
            
            with st.expander("🔍 Filtros Avançados", expanded=True):
                col_f1, col_f2 = st.columns([1, 3])
                turmas_unicas = sorted(df_dados['Turma_Padronizada'].unique())
                
                with col_f1: ver_todas = st.toggle("Selecionar Todas as Turmas", value=False)
                with col_f2:
                    selecao = turmas_unicas if ver_todas else st.multiselect("Selecione as Turmas:", turmas_unicas, default=turmas_unicas[:5], key=f"filtro_{st.session_state.sync_count}")

            df_filtrado = df_dados[df_dados['Turma_Padronizada'].isin(selecao)] if selecao else df_dados.head(0)
            
            if not df_filtrado.empty:
                rec, pag = df_filtrado['Recebido'].sum(), df_filtrado['Pago'].sum()
                lucro = rec - pag
                roi = (lucro / pag * 100) if pag > 0 else 0
                st.divider()
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Receita", f"R$ {rec:,.2f}", delta="Faturamento")
                k2.metric("Despesa", f"R$ {pag:,.2f}", delta="Custo", delta_color="inverse")
                k3.metric("Lucro", f"R$ {lucro:,.2f}", delta="Margem")
                k4.metric("ROI", f"{roi:.1f}%", delta="Retorno")
                
                g1, g2 = st.columns([2, 1])
                with g1:
                    fig = px.bar(df_filtrado.groupby('Turma_Padronizada')['Recebido'].sum().reset_index().sort_values('Recebido'), x='Recebido', y='Turma_Padronizada', orientation='h', text_auto='.2s', title="Ranking", color='Recebido')
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.subheader("🏆 Top Lucratividade")
                    top = df_filtrado.groupby('Turma_Padronizada')[['Recebido','Pago']].sum().reset_index()
                    top['Lucro'] = top['Recebido'] - top['Pago']
                    st.dataframe(top.nlargest(10, 'Lucro')[['Turma_Padronizada','Lucro']], use_container_width=True, hide_index=True)
            else: st.warning("Selecione uma turma.")

        elif pagina == "Auditoria de Dados":
            st.title("📋 Auditoria de Qualidade")
            t1, t2 = st.tabs(["Base Completa", "Padrões Novos"])
            with t1: st.dataframe(df_dados, use_container_width=True)
            with t2:
                if mapa_id:
                    novos = df_dados[~df_dados['Turma_Padronizada'].isin(mapa_id.values())]
                    if not novos.empty: st.dataframe(novos[['Nº Controle 1', 'Turma_Padronizada']].drop_duplicates(), hide_index=True)
                    else: st.success("Sem novos padrões.")
    else:
        st.info("Conectando ao Google Sheets...")