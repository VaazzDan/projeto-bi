import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import hmac
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="Ohana Soluções Empresariais",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# --- 2. IMPORTAÇÃO DE FONTES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;600;700&display=swap');
    </style>
""", unsafe_allow_html=True)

# --- 3. CORES (IDENTIDADE VISUAL) ---
COR_FUNDO = "#0e1117"
COR_SIDEBAR = "#161b24"
COR_CARD = "#1f2937"
COR_PRIMARIA = "#EB5283"    # Magenta/Rosa
COR_SECUNDARIA = "#2497BF"  # Azul Ciano
COR_TEXTO = "#FFFFFF"
COR_SUBTEXTO = "#B0B8C8"
URL_LOGO_LOGIN = "https://i.ibb.co/hJV9NNmX/backgroud-png.png"

# --- 4. ÍCONES SVG ---
ICONS = {
    "money": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>""",
    "down": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>""",
    "profit": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>""",
    "chart": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>""",
    "rocket": f"""<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.1 4-1 4-1"/><path d="M12 15v5s3.03-.55 4-2c1.1-1.62 1-4 1-4"/></svg>""",
    "check": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "alert": f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{COR_PRIMARIA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>""",
    "filter": f"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{COR_SUBTEXTO}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>"""
}

# --- 5. CSS REFINADO ---
def local_css():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {COR_FUNDO}; color: {COR_TEXTO}; }}
        h1, h2, h3, h4, h5, h6, p, span, div, label, input, button {{ font-family: 'Noto Sans', sans-serif; }}
        [data-testid="stSidebarCollapsedControl"] button, [data-testid="stSidebarCollapsedControl"] span, [data-testid="stSidebarNav"] i {{ font-family: sans-serif !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ color: {COR_PRIMARIA} !important; }}
        section[data-testid="stSidebar"] {{ background-color: {COR_SIDEBAR}; border-right: 1px solid rgba(235, 82, 131, 0.2); }}
        section[data-testid="stSidebar"] .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}
        section[data-testid="stSidebar"] > div::-webkit-scrollbar {{ display: none; }}
        h1, h2, h3 {{ color: {COR_PRIMARIA} !important; font-weight: 700 !important; }}
        .kpi-card {{
            background-color: {COR_CARD}; padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);
            border-left: 6px solid {COR_PRIMARIA}; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; transition: all 0.3s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-5px); border-color: {COR_SECUNDARIA}; }}
        .kpi-text-area {{ display: flex; flex-direction: column; }}
        .kpi-title {{ color: {COR_SUBTEXTO}; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
        .kpi-value {{ color: {COR_TEXTO}; font-size: 28px; font-weight: 800; line-height: 1; }}
        .kpi-sub {{ color: {COR_SECUNDARIA}; font-size: 11px; margin-top: 5px; font-weight: 600; }}
        .kpi-icon-box {{ background: rgba(36, 151, 191, 0.1); padding: 12px; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(36, 151, 191, 0.2); }}
        div[data-testid="stDataFrame"] {{ background-color: {COR_CARD}; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }}
        .stTextInput input {{ background-color: {COR_SIDEBAR} !important; color: white !important; border: 1px solid {COR_PRIMARIA} !important; }}
        #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{background-color: transparent !important;}}
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 6. FUNÇÃO AUXILIAR GLOBAL (Cards) ---
def kpi_html(titulo, valor, sub, svg_icon):
    return f"""
    <div class="kpi-card">
        <div class="kpi-text-area">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        <div class="kpi-icon-box">
            {svg_icon}
        </div>
    </div>
    """

# --- 7. TELA DE LOGIN ---
def check_auth():
    if "passwords" not in st.secrets: return True 
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["passwords"]["admin"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False): return True

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
            st.markdown(f"""<div style="background-color: {COR_CARD}; padding: 40px; border-radius: 20px; border-top: 5px solid {COR_PRIMARIA}; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">""", unsafe_allow_html=True)
            try: st.image(URL_LOGO_LOGIN, width=320) 
            except: st.markdown(f"<h1 style='color: {COR_PRIMARIA};'>OHANA</h1>", unsafe_allow_html=True)
            st.markdown(f"""<p style="color: {COR_SUBTEXTO}; letter-spacing: 3px; font-size:12px; font-weight:700; margin-top: 20px;"></p>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_input("Senha", type="password", on_change=password_entered, key="password", label_visibility="collapsed", placeholder="Digite a senha...")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]: st.error("Acesso Negado.")
    return False

if not check_auth(): st.stop()

# --- 8. DADOS (ETL CONECTADO AO GOOGLE SHEETS) ---
# Link do Mapeamento
URL_MAPEAMENTO = "https://docs.google.com/spreadsheets/d/1eP7EPmbaZg1brLwe0DeCD3EFzIyzn6z7yXOGzfvd-H8/edit?usp=sharing"
# Link da Planilha Financeira (Novo Link Fornecido)
URL_FINANCEIRO = "https://docs.google.com/spreadsheets/d/1xhdYFEyl0t5H-928RdGX7je9xiwfEGDaaHIBALAzY60/edit?usp=sharing"
LINK_POWER_BI = "https://app.powerbi.com/reportEmbed?reportId=31c41b07-b8ce-4fc1-9396-0a6cc516c92d&autoAuth=true&ctid=1d90d210-ebe4-4b83-be2c-cdddc540416f"

# Conexão GSheets Universal
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_data():
    # 1. Carrega Mapeamento
    try:
        df_map = conn.read(spreadsheet=URL_MAPEAMENTO)
    except:
        df_map = pd.DataFrame()
    
    # 2. Carrega Financeiro (Agora via Link do Google Sheets)
    try:
        df_fin = conn.read(spreadsheet=URL_FINANCEIRO)
    except Exception as e:
        st.error(f"Erro ao ler Planilha Financeira: {e}")
        df_fin = pd.DataFrame()
        
    return df_map, df_fin

def process_data(df_map, df_fin):
    # Dicionário definido corretamente aqui como mapa_id
    mapa_id = {}
    
    # Processa Mapeamento
    if not df_map.empty:
        df_map.columns = [str(c).strip().capitalize() for c in df_map.columns]
        for _, row in df_map.dropna(subset=['Para']).iterrows():
            match = re.search(r'^\d+', str(row.get('De', '')))
            if match: mapa_id[match.group(0)] = str(row['Para']).upper()

    # Processa Financeiro
    if not df_fin.empty:
        df_fin.columns = [str(c).strip() for c in df_fin.columns]
        
        # Limpeza de Valor (Tratamento robusto para números e strings)
        def clean_val(v):
            try:
                if pd.isna(v) or str(v).strip() == '': return 0.0
                if isinstance(v, (int, float)): return float(v)
                s = str(v).replace('R$', '').replace(' ', '')
                if ',' in s and '.' not in s: s = s.replace(',', '.')
                elif '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
                return float(s)
            except: return 0.0
            
        col_valor_original = 'Valor' if 'Valor' in df_fin.columns else df_fin.columns[0]
        df_fin['Valor_Clean'] = df_fin[col_valor_original].apply(clean_val)

        # Classificação Recebido/Pago
        def classificar(row):
            rec, desp = 0.0, 0.0
            col_tipo = next((c for c in df_fin.columns if c.upper() == 'TIPO'), None)
            tipo = str(row[col_tipo]).lower() if col_tipo else ''
            
            val = row.get('Valor_Clean', 0.0)
            
            if 'recebido' in tipo:
                rec = val
            elif 'pago' in tipo:
                desp = abs(val)
            elif val > 0: rec = val 
            else: desp = abs(val)
            
            return pd.Series([rec, desp])
            
        df_fin[['Receita_Real', 'Despesa_Real']] = df_fin.apply(classificar, axis=1)
        
        # Padronização de Turma
        def get_turma(val):
            match = re.search(r'^\d+', str(val).strip())
            if match:
                turma_id = match.group(0)
                # Usa mapa_id (a variável local correta)
                return mapa_id.get(turma_id, re.sub(r'\s+\d+[\d\s.]*$', '', str(val).strip()).upper())
            return "NÃO INFORMADO"
            
        col_controle = next((c for c in df_fin.columns if 'CONTROLE' in c.upper()), df_fin.columns[0])
        df_fin['Turma_Padronizada'] = df_fin[col_controle].apply(get_turma)
        
    # CORREÇÃO: Retorna mapa_id (variável local), não mapa_dict (que não existe aqui)
    return df_fin, df_map, mapa_id 

raw_map, raw_fin = load_data()
df_dados, df_map, mapa_dict = process_data(raw_map, raw_fin)

# --- 9. MENU E PÁGINAS ---
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 0; color: {COR_PRIMARIA}; letter-spacing: 2px;'>MENU</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Power BI", "Mapeamento", "Auditoria"],
        icons=["rocket-takeoff", "graph-up", "table", "shield-check"], 
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": COR_PRIMARIA, "font-size": "18px"},
            "nav-link": {"color": COR_SUBTEXTO, "font-size": "14px", "margin": "5px"},
            "nav-link-selected": {"background-color": "rgba(235, 82, 131, 0.1)", "color": COR_PRIMARIA, "border": f"1px solid {COR_PRIMARIA}"},
        }
    )
    st.markdown("---")
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if selected == "Dashboard":
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        {ICONS['rocket']}
        <h1 style="margin: 0; font-size: 32px;">Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

    if df_dados.empty:
        st.info("Carregando dados...")
    else:
        # --- CABEÇALHO DO FILTRO (SVG + Texto) ---
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; color: {COR_SUBTEXTO};">
            {ICONS['filter']}
            <span style="font-weight: 600; font-size: 14px; text-transform: uppercase;">Filtros Avançados</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Expandir Opções", expanded=True):
            c1, c2 = st.columns([1, 4])
            mode = c1.radio("Modo", ["Todas", "Seleção"], horizontal=True)
            turmas_disponiveis = []
            if 'Turma_Padronizada' in df_dados.columns:
                turmas_disponiveis = sorted(df_dados['Turma_Padronizada'].astype(str).unique())
            
            if mode == "Seleção":
                padrao = turmas_disponiveis[:3] if len(turmas_disponiveis) >= 3 else turmas_disponiveis
                sel = c2.multiselect("Selecione:", turmas_disponiveis, default=padrao, label_visibility="collapsed")
                if sel: df_f = df_dados[df_dados['Turma_Padronizada'].astype(str).isin(sel)]
                else:
                    st.warning("Selecione pelo menos uma turma.")
                    df_f = df_dados.head(0)
            else:
                c2.info(f"Visualizando dados consolidados de {len(turmas_disponiveis)} turmas.")
                df_f = df_dados

        if not df_f.empty:
            rec = df_f['Receita_Real'].sum()
            pag = df_f['Despesa_Real'].sum()
            lucro = rec - pag
            margem = (lucro / rec * 100) if rec > 0 else 0
            
            k1, k2, k3, k4 = st.columns(4)
            with k1: st.markdown(kpi_html("Receita", f"R$ {rec:,.2f}", "Entradas", ICONS['money']), unsafe_allow_html=True)
            with k2: st.markdown(kpi_html("Despesas", f"R$ {pag:,.2f}", "Saídas", ICONS['down']), unsafe_allow_html=True)
            with k3: st.markdown(kpi_html("Lucro Líquido", f"R$ {lucro:,.2f}", "Resultado", ICONS['profit']), unsafe_allow_html=True)
            with k4: st.markdown(kpi_html("Margem", f"{margem:.1f}%", "ROI", ICONS['chart']), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            g1, g2 = st.columns([2, 1])
            with g1:
                st.markdown(f"""<div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">{ICONS['chart']} <h3>Performance</h3></div>""", unsafe_allow_html=True)
                df_c = df_f.groupby('Turma_Padronizada')[['Receita_Real', 'Despesa_Real']].sum().reset_index().sort_values('Receita_Real').tail(10)
                fig = go.Figure()
                fig.add_trace(go.Bar(y=df_c['Turma_Padronizada'], x=df_c['Receita_Real'], name='Receita', orientation='h', marker_color=COR_SECUNDARIA))
                fig.add_trace(go.Bar(y=df_c['Turma_Padronizada'], x=df_c['Despesa_Real'], name='Despesa', orientation='h', marker_color=COR_PRIMARIA))
                fig.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=COR_SUBTEXTO), margin=dict(t=10,l=0,r=0,b=0), legend=dict(orientation="h", y=1.1, x=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
                st.plotly_chart(fig, use_container_width=True)

            with g2:
                st.markdown(f"""<div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">{ICONS['profit']} <h3>Ranking</h3></div>""", unsafe_allow_html=True)
                top = df_f.groupby('Turma_Padronizada')[['Receita_Real', 'Despesa_Real']].sum().reset_index()
                top['Lucro'] = top['Receita_Real'] - top['Despesa_Real']
                st.dataframe(top.nlargest(10, 'Lucro')[['Turma_Padronizada', 'Lucro']], use_container_width=True, hide_index=True, height=450, column_config={"Turma_Padronizada": st.column_config.TextColumn("Turma"), "Lucro": st.column_config.ProgressColumn("Lucro", format="R$ %.0f", min_value=0, max_value=float(top['Lucro'].max()) if not top.empty else 100)})

elif selected == "Power BI":
    st.markdown(f"""<h3>Relatório Power BI</h3>""", unsafe_allow_html=True)
    st.markdown(f"""<div style="background-color:{COR_CARD}; height:85vh; border-radius:12px; border:1px solid {COR_PRIMARIA}; overflow:hidden;"><iframe title="BI" width="100%" height="100%" src="{LINK_POWER_BI}" frameborder="0" allowFullScreen="true"></iframe></div>""", unsafe_allow_html=True)

elif selected == "Mapeamento":
    st.markdown(f"""<h3>Editor de Mapeamentos</h3>""", unsafe_allow_html=True)
    if not df_map.empty:
        edt = st.data_editor(df_map, num_rows="dynamic", use_container_width=True, height=600)
        if st.button("💾 Salvar"):
            try:
                conn.update(spreadsheet=URL_MAPEAMENTO, data=edt)
                st.success("Salvo!")
            except: st.error("Erro ao salvar")

elif selected == "Auditoria":
    st.markdown(f"""<h3>Auditoria</h3>""", unsafe_allow_html=True)
    if not df_dados.empty and 'Turma_Padronizada' in df_dados.columns:
        if mapa_dict:
            err = df_dados[~df_dados['Turma_Padronizada'].isin(mapa_dict.values())]
        else:
            err = pd.DataFrame() 
            
        c1, c2 = st.columns(2)
        total = len(df_dados)
        qualidade = (1 - len(err)/total)*100 if total > 0 else 100
        with c1: st.markdown(kpi_html("Pendentes", f"{len(err)}", "Itens não mapeados", ICONS['alert']), unsafe_allow_html=True)
        with c2: st.markdown(kpi_html("Qualidade", f"{qualidade:.1f}%", "Dados Confiáveis", ICONS['check']), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if not err.empty: st.dataframe(err.iloc[:, :5], use_container_width=True)
        elif total > 0: st.success("100% dos dados estão mapeados ou mapa vazio.")
