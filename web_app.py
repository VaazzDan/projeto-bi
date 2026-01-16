import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import hmac

# ==============================================================================
# 1. CONFIGURAÇÃO GERAL E ESTILO
# ==============================================================================
st.set_page_config(
    page_title="Ohana Soluções Financeiras",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# --- ATIVOS (LOGO ATUALIZADA) ---
LOGO_URL = "https://i.ibb.co/xZGzw7F/ohana.png"

# --- CORES DA MARCA ---
COR_FUNDO = "#0e1117"
COR_SIDEBAR = "#161b24"
COR_CARD = "#1f2937"
COR_PRIMARIA = "#EB5283"    # Magenta/Rosa
COR_SECUNDARIA = "#2497BF"  # Azul Ciano
COR_TEXTO = "#FFFFFF"
COR_SUBTEXTO = "#B0B8C8"

# --- ÍCONES SVG ---
ICONS = {
    "money": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
    "down": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>""",
    "profit": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
    "chart": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_TEXTO}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>""",
    "rocket": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.1 4-1 4-1"/><path d="M12 15v5s3.03-.55 4-2c1.1-1.62 1-4 1-4"/></svg>"""
}

# --- CSS GLOBAL ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;600;700&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; color: {COR_TEXTO}; }}
    h1, h2, h3, p, div, span {{ font-family: 'Noto Sans', sans-serif; }}
    
    section[data-testid="stSidebar"] {{ background-color: {COR_SIDEBAR}; border-right: 1px solid rgba(235, 82, 131, 0.1); }}
    
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(235, 82, 131, 0.3) !important;
    }}
    .stTextInput input:focus {{ border-color: {COR_PRIMARIA} !important; }}

    .kpi-card {{
        background-color: {COR_CARD}; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid rgba(255,255,255,0.05);
        border-left: 4px solid {COR_PRIMARIA}; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px; 
        display: flex; 
        align-items: center; 
        justify-content: space-between;
        transition: transform 0.2s;
    }}
    .kpi-card:hover {{ transform: translateY(-3px); border-color: {COR_SECUNDARIA}; }}
    .kpi-title {{ color: {COR_SUBTEXTO}; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }}
    .kpi-value {{ color: {COR_TEXTO}; font-size: 24px; font-weight: 800; }}
    .kpi-sub {{ color: {COR_SECUNDARIA}; font-size: 11px; margin-top: 2px; }}
    .kpi-icon-box {{ 
        background: rgba(255, 255, 255, 0.03); 
        padding: 10px; 
        border-radius: 8px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
    }}
    
    .stMultiSelect {{ color: {COR_TEXTO}; }}
    div[data-testid="stDataFrame"] {{ background-color: {COR_CARD}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

def kpi_html(titulo, valor, sub, svg_icon):
    return f"""
    <div class="kpi-card">
        <div class="kpi-text-area">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        <div class="kpi-icon-box">{svg_icon}</div>
    </div>
    """

# ==============================================================================
# 2. SISTEMA DE LOGIN
# ==============================================================================
def check_auth():
    if "passwords" not in st.secrets:
        st.warning("⚠️ Nenhuma senha configurada em secrets.toml.")
        return True

    def password_entered():
        if hmac.compare_digest(st.session_state["password_input"], st.secrets["passwords"]["admin"]):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
             st.markdown(f"""<div style="background-color: {COR_CARD}; padding: 40px; border-radius: 20px; border-top: 5px solid {COR_PRIMARIA}; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">""", unsafe_allow_html=True)
             
             # Logo da tela de login
             st.image(LOGO_URL, width=180)
             
             st.markdown(f"""<h3 style="color: {COR_TEXTO}; margin-top: 20px; font-weight: 600;">Acesso Restrito</h3>""", unsafe_allow_html=True)
             st.markdown(f"""<p style="color: {COR_SUBTEXTO}; font-size: 14px;">Digite sua credencial para continuar.</p>""", unsafe_allow_html=True)
             
             st.text_input("Senha", type="password", on_change=password_entered, key="password_input", label_visibility="collapsed", placeholder="Digite a senha de acesso...")

             if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                 st.error("❌ Senha incorreta.")

        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_auth(): st.stop()

# ==============================================================================
# 3. ENGENHARIA DE DADOS
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    SHEET_ID = '19QVv-DBUIHoFx1mn5nL1NZUcHyPnzGLZfgCb9UH0ARo'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
    
    try:
        all_sheets = pd.read_excel(url, sheet_name=None, engine='openpyxl')
        df_list = []
        
        def limpar_valor(series):
            if series.dtype == 'O': 
                return pd.to_numeric(
                    series.astype(str).str.replace('R$', '', regex=False)
                          .str.replace('.', '', regex=False)
                          .str.replace(',', '.', regex=False),
                    errors='coerce'
                ).fillna(0)
            return series.fillna(0)

        for sheet_name, df in all_sheets.items():
            s_name_upper = sheet_name.upper()
            df.columns = df.columns.astype(str).str.strip().str.upper()
            
            tipo_lancamento = None
            if 'RECEB' in s_name_upper or 'RECEIT' in s_name_upper:
                tipo_lancamento = 'RECEITA'
            elif 'PAGA' in s_name_upper or 'DESP' in s_name_upper:
                tipo_lancamento = 'DESPESA'
            
            if tipo_lancamento:
                col_valor = next((c for c in df.columns if c == 'VALOR'), None) or \
                            next((c for c in df.columns if 'VALOR' in c), None)

                col_curso = next((c for c in df.columns if "CONTROLE_PADRONIZADO" in c), None)
                col_data = next((c for c in df.columns if 'DATA' in c), None)
                
                if col_valor and col_curso:
                    df_temp = pd.DataFrame()
                    df_temp['CURSO'] = df[col_curso].astype(str).str.strip().str.upper()
                    df_temp['VALOR'] = limpar_valor(df[col_valor]).abs()
                    
                    if col_data:
                        df_temp['DATA'] = pd.to_datetime(df[col_data], errors='coerce')
                        df_temp['ANO'] = df_temp['DATA'].dt.year
                    else:
                        df_temp['DATA'] = pd.NaT
                        df_temp['ANO'] = None
                        
                    df_temp['TIPO'] = tipo_lancamento
                    df_list.append(df_temp)
            
        return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

    except Exception as e:
        st.error(f"Erro Crítico no ETL: {e}")
        return pd.DataFrame()

df = load_data()

# ==============================================================================
# 4. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True, output_format="PNG")
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px; margin-top: -10px;">
        <p style="color: {COR_SUBTEXTO}; font-size: 12px; letter-spacing: 1px;">Intelligence Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Power BI Relatório"],
        icons=["rocket-takeoff", "graph-up"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": COR_PRIMARIA, "font-size": "16px"},
            "nav-link": {"color": COR_SUBTEXTO, "font-size": "14px", "text-align": "left", "margin": "5px"},
            "nav-link-selected": {"background-color": "rgba(235, 82, 131, 0.15)", "color": COR_PRIMARIA, "border-left": f"4px solid {COR_PRIMARIA}"},
        }
    )
    
    st.markdown("---")
    if st.button("🔒 Sair / Logout", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

if df.empty:
    st.info("Aguardando carregamento de dados...")
    st.stop()

# ==============================================================================
# 5. DASHBOARD
# ==============================================================================
if selected == "Dashboard":
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        {ICONS['rocket']}
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Visão Executiva</h1>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Filtros Avançados", expanded=True):
        c1, c2 = st.columns([1, 2])
        anos = sorted(df['ANO'].dropna().unique())
        sel_ano = c1.multiselect("Ano de Referência", anos, default=anos)
        df_f = df[df['ANO'].isin(sel_ano)] if sel_ano else df
        
        cursos = sorted(df_f['CURSO'].unique())
        ver_todos = c2.checkbox("Selecionar TODOS os cursos", value=True)
        
        if ver_todos:
            c2.markdown(f'<span style="color:{COR_SECUNDARIA}; font-weight:bold;">✅ Visualizando dados consolidados de {len(cursos)} cursos</span>', unsafe_allow_html=True)
            df_final = df_f
        else:
            sel_curso = c2.multiselect("Selecione Cursos Específicos", cursos)
            df_final = df_f[df_f['CURSO'].isin(sel_curso)] if sel_curso else df_f

    st.markdown("<br>", unsafe_allow_html=True)

    receita = df_final[df_final['TIPO'] == 'RECEITA']['VALOR'].sum()
    despesa = df_final[df_final['TIPO'] == 'DESPESA']['VALOR'].sum()
    lucro = receita - despesa
    margem = (lucro / receita * 100) if receita > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Receita Total", f"R$ {receita:,.2f}", "Entradas", ICONS['money']), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Despesas", f"R$ {despesa:,.2f}", "Saídas", ICONS['down']), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Lucro Líquido", f"R$ {lucro:,.2f}", "Resultado", ICONS['profit']), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Margem", f"{margem:.1f}%", "ROI", ICONS['chart']), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    df_chart = df_final.groupby(['CURSO', 'TIPO'])['VALOR'].sum().unstack(fill_value=0).reset_index()
    if 'RECEITA' not in df_chart.columns: df_chart['RECEITA'] = 0
    if 'DESPESA' not in df_chart.columns: df_chart['DESPESA'] = 0

    g1, g2 = st.columns([2, 1])
    with g1:
        st.markdown('<h3 style="color:white; font-size:18px;">Performance Financeira</h3>', unsafe_allow_html=True)
        if not df_chart.empty:
            df_chart['VOLUME'] = df_chart['RECEITA'] + df_chart['DESPESA']
            df_perf = df_chart.sort_values('VOLUME', ascending=False).head(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_perf['CURSO'], y=df_perf['RECEITA'], name='Receita', marker_color=COR_SECUNDARIA))
            fig.add_trace(go.Bar(x=df_perf['CURSO'], y=df_perf['DESPESA'], name='Despesa', marker_color=COR_PRIMARIA))
            fig.update_layout(
                barmode='group', height=400, 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COR_SUBTEXTO),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(orientation="h", y=1.1, x=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown('<h3 style="color:white; font-size:18px;">Top Ranking</h3>', unsafe_allow_html=True)
        if not df_chart.empty:
            df_rank = df_chart.sort_values('RECEITA', ascending=True).tail(10)
            fig_rank = px.bar(df_rank, y='CURSO', x='RECEITA', orientation='h', text_auto='.2s')
            fig_rank.update_traces(marker_color=COR_SECUNDARIA)
            fig_rank.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COR_SUBTEXTO), yaxis_title=None, xaxis_title=None,
                xaxis=dict(showgrid=False), yaxis=dict(type='category')
            )
            st.plotly_chart(fig_rank, use_container_width=True)

    with st.expander("Visualizar Dados em Tabela"):
        st.dataframe(
            df_final[['DATA', 'CURSO', 'TIPO', 'VALOR']].sort_values(['DATA', 'TIPO'], ascending=[False, True]),
            use_container_width=True, height=300
        )

# ==============================================================================
# 6. POWER BI
# ==============================================================================
elif selected == "Power BI Relatório":
    st.markdown(f"""
    <div style="background-color:{COR_CARD}; border-radius:12px; border:1px solid rgba(235, 82, 131, 0.3); padding:10px;">
        <iframe title="ANÁLISE RESULTADOS FINANCEIROS FRAME" width="100%" height="700" src="https://app.powerbi.com/reportEmbed?reportId=bc030009-e3a7-41d5-ba7d-1ba5081c9db8&autoAuth=true&ctid=1d90d210-ebe4-4b83-be2c-cdddc540416f&actionBarEnabled=true" frameborder="0" allowFullScreen="true"></iframe>
    </div>
    """, unsafe_allow_html=True)