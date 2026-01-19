import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import hmac

# ==============================================================================
# 1. CONFIGURAÇÃO GERAL
# ==============================================================================
st.set_page_config(
    page_title="Ohana Soluções Financeiras",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

LOGO_URL = "https://i.ibb.co/xZGzw7F/ohana.png"

# --- CONSTANTES DE DATA ---
MESES_DICT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# --- CORES ---
COR_FUNDO = "#0e1117"
COR_SIDEBAR = "#161b24"
COR_CARD = "#1f2937"
COR_PRIMARIA = "#EB5283"
COR_SECUNDARIA = "#2497BF"
COR_TEXTO = "#FFFFFF"
COR_SUBTEXTO = "#B0B8C8"
COR_ALERT = "#ef4444"
COR_WARN = "#f59e0b"

# --- ÍCONES ---
ICONS = {
    "money": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
    "down": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>""",
    "profit": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
    "chart": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_TEXTO}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>""",
    "rocket": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.1 4-1 4-1"/><path d="M12 15v5s3.03-.55 4-2c1.1-1.62 1-4 1-4"/></svg>""",
    "bank": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>""",
    "tax": f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" x2="12" y1="18" y2="12"/><line x1="9" x2="15" y1="15" y2="15"/></svg>"""
}

# --- CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;600;700&display=swap');
    .stApp {{ background-color: {COR_FUNDO}; color: {COR_TEXTO}; }}
    h1, h2, h3, p, div, span {{ font-family: 'Noto Sans', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: {COR_SIDEBAR}; border-right: 1px solid rgba(235, 82, 131, 0.1); }}
    .stTextInput input {{ background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; border: 1px solid rgba(235, 82, 131, 0.3) !important; }}
    .stTextInput input:focus {{ border-color: {COR_PRIMARIA} !important; }}
    
    div.stButton > button {{
        background-color: {COR_CARD};
        color: {COR_TEXTO};
        border: 1px solid {COR_PRIMARIA};
        width: 100%;
        transition: all 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: {COR_PRIMARIA};
        color: white;
        border-color: {COR_PRIMARIA};
    }}
    
    .kpi-card {{ background-color: {COR_CARD}; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid {COR_PRIMARIA}; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; transition: transform 0.2s; }}
    .kpi-card:hover {{ transform: translateY(-3px); border-color: {COR_SECUNDARIA}; }}
    .kpi-title {{ color: {COR_SUBTEXTO}; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }}
    .kpi-value {{ color: {COR_TEXTO}; font-size: 24px; font-weight: 800; }}
    .kpi-sub {{ color: {COR_SECUNDARIA}; font-size: 11px; margin-top: 2px; }}
    .kpi-icon-box {{ background: rgba(255, 255, 255, 0.03); padding: 10px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }}
    .stMultiSelect {{ color: {COR_TEXTO}; }}
    div[data-testid="stDataFrame"] {{ background-color: {COR_CARD}; border-radius: 8px; }}
    div[data-testid="stAlert"] {{ padding: 0.5rem; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# --- FORMATADOR BRL ---
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
# 2. LOGIN
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
# 3. ETL (FILTRAGEM DE LIXO E MAPA DE DADOS)
# ==============================================================================
@st.cache_data(ttl=600)
def load_data():
    SHEET_ID = '19QVv-DBUIHoFx1mn5nL1NZUcHyPnzGLZfgCb9UH0ARo'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
    
    logs = []
    
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
            elif 'PAGA' in s_name_upper or 'DESP' in s_name_upper or 'SAIDA' in s_name_upper:
                tipo_lancamento = 'DESPESA'
            
            if tipo_lancamento:
                col_valor = next((c for c in df.columns if c == 'VALOR'), None) or \
                            next((c for c in df.columns if 'VALOR' in c), None)

                col_curso = next((c for c in df.columns if "CONTROLE" in c and "PADRONIZADO" in c), None)
                if not col_curso:
                    col_curso = next((c for c in df.columns if "CONTROLE" in c), None) or \
                                next((c for c in df.columns if "CURSO" in c), None)

                col_produto = next((c for c in df.columns if "PRODUTO" in c or "SERVIÇO" in c), None)
                
                col_entidade = next((c for c in df.columns if "CLIENTE" in c or "FORNECEDOR" in c or "FAVORECIDO" in c), None)
                if not col_entidade:
                    col_entidade = next((c for c in df.columns if "NOME" in c or "DESCRI" in c), None)

                col_data = next((c for c in df.columns if 'PAGAMENTO' in c and 'DATA' in c), None) or \
                           next((c for c in df.columns if 'DATA' in c), None)
                
                if col_valor and col_curso:
                    df_subset = df.copy()
                    
                    df_subset['TEMP_CURSO'] = (
                        df_subset[col_curso]
                        .fillna('')
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .str.replace(r'\.0$', '', regex=True)
                    )
                    
                    if col_produto:
                        df_subset['TEMP_PRODUTO'] = df_subset[col_produto].fillna('').astype(str).str.strip().str.upper()
                    else:
                        df_subset['TEMP_PRODUTO'] = 'NÃO INFORMADO'
                        
                    if col_entidade:
                        df_subset['TEMP_ENTIDADE'] = df_subset[col_entidade].fillna('').astype(str).str.strip().str.upper()
                    else:
                        df_subset['TEMP_ENTIDADE'] = 'NÃO INFORMADO'

                    # LISTA DE EXCLUSÃO (CRÍTICO)
                    valores_invalidos = [
                        '', 'NAN', 'NAT', 'NONE', 'NULL', '0', 'N/A', '-', 'nan',
                        'NÃO ENCONTRADO', 'NAO ENCONTRADO', 'NAO_ENCONTRADO'
                    ]
                    
                    mask_invalid = df_subset['TEMP_CURSO'].isin(valores_invalidos)
                    df_subset = df_subset[~mask_invalid]
                    
                    if df_subset.empty:
                        logs.append(f"⚠️ Aba '{sheet_name}' ignorada: Registros sem 'Nº Controle' válido.")
                        continue

                    df_temp = pd.DataFrame()
                    df_temp['CURSO'] = df_subset['TEMP_CURSO']
                    df_temp['PRODUTO'] = df_subset['TEMP_PRODUTO']
                    df_temp['ENTIDADE'] = df_subset['TEMP_ENTIDADE']
                    df_temp['VALOR'] = limpar_valor(df_subset[col_valor]).abs() 
                    
                    if col_data:
                        df_temp['DATA'] = pd.to_datetime(df_subset[col_data], errors='coerce')
                    else:
                        df_temp['DATA'] = pd.NaT
                        
                    df_temp['TIPO'] = tipo_lancamento
                    df_list.append(df_temp)
            
        df_final = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
        
        if not df_final.empty:
            mapa_produtos = (
                df_final[df_final['TIPO'] == 'RECEITA']
                .drop_duplicates('CURSO')
                .set_index('CURSO')['PRODUTO']
                .to_dict()
            )
            mask_update = (df_final['TIPO'] == 'DESPESA')
            df_final.loc[mask_update, 'PRODUTO'] = df_final.loc[mask_update, 'CURSO'].map(mapa_produtos).fillna('OUTROS / INDEFINIDO')

        return df_final, logs

    except Exception as e:
        return pd.DataFrame(), [f"Erro Crítico: {str(e)}"]

df, debug_logs = load_data()

# ==============================================================================
# 4. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True, output_format="PNG")
    st.markdown(f"""<div style="text-align: center; margin-bottom: 20px; margin-top: -10px;"><p style="color: {COR_SUBTEXTO}; font-size: 12px; letter-spacing: 1px;">Intelligence Dashboard</p></div>""", unsafe_allow_html=True)
    
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
    st.error("Nenhum dado financeiro válido foi encontrado.")
    with st.expander("🕵️ Ver Diagnóstico", expanded=True):
        for log in debug_logs: st.text(log)
    st.stop()

# ==============================================================================
# 5. DASHBOARD
# ==============================================================================
if selected == "Dashboard":
    st.markdown(f"""<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">{ICONS['rocket']}<h1 style="margin: 0; font-size: 28px; font-weight: 700;">Visão Executiva</h1></div>""", unsafe_allow_html=True)

    # --- INICIALIZAÇÃO DE ESTADO ---
    if 'show_taxas' not in st.session_state: st.session_state.show_taxas = False
    if 'show_das' not in st.session_state: st.session_state.show_das = False

    def toggle_taxas(): st.session_state.show_taxas = not st.session_state.show_taxas
    def toggle_das(): st.session_state.show_das = not st.session_state.show_das

    # --- FILTROS ---
    with st.expander("🔍 Filtros: Produto & Controle", expanded=True):
        c_f1, c_f2 = st.columns(2)
        
        produtos_unicos = sorted([p for p in df['PRODUTO'].unique() if p and str(p) != 'nan'])
        ver_todos_prod = c_f1.checkbox("Selecionar TODOS os Produtos", value=True)
        
        if ver_todos_prod:
            c_f1.info("✅ Todos os Produtos Selecionados")
            df_step1 = df
        else:
            sel_produto = c_f1.multiselect("Selecione Produtos", produtos_unicos)
            if not sel_produto:
                c_f1.warning("⚠️ Selecione pelo menos um produto")
                df_step1 = df[df['PRODUTO'].isin([])]
            else:
                df_step1 = df[df['PRODUTO'].isin(sel_produto)]
        
        controles_unicos = sorted(df_step1['CURSO'].unique())
        ver_todos_controle = c_f2.checkbox("Selecionar TODOS os Controles", value=True)
        
        if ver_todos_controle:
            c_f2.info("✅ Todos os Controles Selecionados")
            df_final = df_step1
        else:
            sel_controle = c_f2.multiselect("Selecione Nº Controle", controles_unicos)
            if not sel_controle:
                c_f2.warning("⚠️ Selecione pelo menos um controle")
                df_final = df_step1[df_step1['CURSO'].isin([])]
            else:
                df_final = df_step1[df_step1['CURSO'].isin(sel_controle)]

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CÁLCULOS KPI ---
    cursos_validos_receita = df[df['TIPO'] == 'RECEITA']['CURSO'].unique()
    
    receita = df_final[df_final['TIPO'] == 'RECEITA']['VALOR'].sum()
    
    df_despesas_validas = df_final[
        (df_final['TIPO'] == 'DESPESA') & 
        (df_final['CURSO'].isin(cursos_validos_receita))
    ]
    despesa = df_despesas_validas['VALOR'].sum()
    
    lucro = receita - despesa # Margem Bruta
    
    val_taxas_total = receita * 0.0233
    val_das_total = receita * 0.0989
    margem_contribuicao = lucro - val_taxas_total - val_das_total
    
    margem = (margem_contribuicao / receita * 100) if receita > 0 else 0

    # --- EXIBIÇÃO DE KPIS ---
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.markdown(kpi_html("Receita de Vendas", format_currency(receita), "Entradas (Vinc.)", ICONS['money']), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Despesas de Vendas", format_currency(despesa), "Saídas (Validadas)", ICONS['down']), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Margem Bruta", format_currency(lucro), "Resultado", ICONS['profit']), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Margem Contribuição", format_currency(margem_contribuicao), "Margem bruta - Taxas - DAS", ICONS['bank']), unsafe_allow_html=True)
    with k5: st.markdown(kpi_html("Margem %", f"{margem:.1f}%", "ROI Líquido", ICONS['chart']), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BOTÕES E KPIS DINÂMICOS ---
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    
    label_taxas = "🔽 Ocultar Taxas" if st.session_state.show_taxas else "▶ Taxas bancárias (média)"
    label_das = "🔽 Ocultar DAS" if st.session_state.show_das else "▶ DAS Real"
    
    btn_col1.button(label_taxas, on_click=toggle_taxas, use_container_width=True)
    btn_col2.button(label_das, on_click=toggle_das, use_container_width=True)
    
    if st.session_state.show_taxas or st.session_state.show_das:
        ext_kpi_cols = st.columns(4)
        idx = 0
        
        if st.session_state.show_taxas:
            with ext_kpi_cols[idx]:
                st.markdown(kpi_html("Taxas bancárias (média)", format_currency(val_taxas_total), "2,33% da Receita", ICONS['bank']), unsafe_allow_html=True)
            idx += 1
            
        if st.session_state.show_das:
            with ext_kpi_cols[idx]:
                st.markdown(kpi_html("DAS Real", format_currency(val_das_total), "9,89% da Receita", ICONS['tax']), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    df_g_receita = df_final[df_final['TIPO'] == 'RECEITA']
    df_g_despesa = df_despesas_validas
    df_grafico = pd.concat([df_g_receita, df_g_despesa])
    
    df_chart = df_grafico.groupby(['CURSO', 'TIPO'])['VALOR'].sum().unstack(fill_value=0).reset_index()
    if 'RECEITA' not in df_chart.columns: df_chart['RECEITA'] = 0
    if 'DESPESA' not in df_chart.columns: df_chart['DESPESA'] = 0

    g1, g2 = st.columns([2, 1])
    
    with g1:
        st.markdown('<h3 style="color:white; font-size:18px;">Performance Financeira (Nº Controle)</h3>', unsafe_allow_html=True)
        if not df_chart.empty:
            df_chart['VOLUME'] = df_chart['RECEITA'] + df_chart['DESPESA']
            df_perf = df_chart.sort_values('VOLUME', ascending=False).head(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_perf['CURSO'], y=df_perf['RECEITA'], name='Receita', marker_color=COR_SECUNDARIA,
                text=df_perf['RECEITA'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                textposition='auto'
            ))
            fig.add_trace(go.Bar(
                x=df_perf['CURSO'], y=df_perf['DESPESA'], name='Despesa', marker_color=COR_PRIMARIA,
                text=df_perf['DESPESA'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                textposition='auto'
            ))
            fig.update_layout(
                barmode='group', height=400, 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COR_SUBTEXTO),
                xaxis=dict(showgrid=False, type='category'), 
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                legend=dict(orientation="h", y=1.1, x=0), separators=",."
            )
            st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown('<h3 style="color:white; font-size:18px;">Top Ranking (Nº Controle)</h3>', unsafe_allow_html=True)
        if not df_chart.empty:
            df_rank = df_chart.sort_values('RECEITA', ascending=True).tail(10)
            df_rank['TEXTO_BRL'] = df_rank['RECEITA'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            fig_rank = px.bar(df_rank, y='CURSO', x='RECEITA', orientation='h', text='TEXTO_BRL')
            fig_rank.update_traces(marker_color=COR_SECUNDARIA)
            fig_rank.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COR_SUBTEXTO), yaxis_title="Nº Controle", xaxis_title=None,
                xaxis=dict(showgrid=False), yaxis=dict(type='category', title=None), separators=",."
            )
            st.plotly_chart(fig_rank, use_container_width=True)

    with st.expander("Visualizar Dados Detalhados"):
        st.dataframe(
            df_final[['DATA', 'CURSO', 'TIPO', 'VALOR', 'ENTIDADE', 'PRODUTO']]
            .sort_values(['DATA', 'TIPO'], ascending=[False, True])
            .rename(columns={
                'DATA': 'Data',
                'CURSO': 'Nº Controle',
                'TIPO': 'Tipo',
                'VALOR': 'Valor',
                'ENTIDADE': 'Cliente/Fornecedor',
                'PRODUTO': 'Conta/Serviço'
            })
            .style.format({'Valor': format_currency}),
            use_container_width=True, height=300
        )

# ==============================================================================
# 6. POWER BI
# ==============================================================================
elif selected == "Power BI Relatório":
    st.markdown(f"""
    <div style="background-color:{COR_CARD}; border-radius:12px; border:1px solid rgba(235, 82, 131, 0.3); padding:10px;">
        <iframe title="DASHBOARD RESULTADOS FRAME" width="100%" height="700" src="https://app.powerbi.com/reportEmbed?reportId=ff124fd1-8c3c-4a5f-a7dd-ed1f05b078c1&autoAuth=true&ctid=1d90d210-ebe4-4b83-be2c-cdddc540416f" frameborder="0" allowFullScreen="true"></iframe>
    </div>
    """, unsafe_allow_html=True)