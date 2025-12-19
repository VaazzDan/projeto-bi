import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Financeiro Projuris", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Resultado_Consultoria_Final.xlsx")
    df['Turma_Padronizada'] = df['Turma_Padronizada'].fillna("NÃO INFORMADO").astype(str)
    return df

try:
    df = carregar_dados()
    st.title("📊 BI de Consultoria Financeira")

    st.sidebar.header("Filtros de Análise")
    opcoes_turmas = sorted(df['Turma_Padronizada'].unique())
    turmas_sel = st.sidebar.multiselect("Selecione as Turmas:", opcoes_turmas, default=opcoes_turmas)

    df_filtrado = df[df['Turma_Padronizada'].isin(turmas_sel)]

    # --- MÉTRICAS ---
    rec, pag = df_filtrado['Recebido'].sum(), df_filtrado['Pago'].sum()
    lucro = rec - pag
    roi = (lucro / pag * 100) if pag > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita", f"R$ {rec:,.2f}")
    c2.metric("Despesa", f"R$ {pag:,.2f}")
    c3.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
    c4.metric("ROI Geral", f"{roi:.1f}%")

    # --- GRÁFICOS ---
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(df_filtrado.groupby('Turma_Padronizada')['Recebido'].sum().reset_index(), 
                               x='Turma_Padronizada', y='Recebido', title="Faturamento por Turma"))

    with col2:
        # Resolve o erro "top_5 is not defined" (image_3bce05)
        resumo = df_filtrado.groupby('Turma_Padronizada').agg({'Recebido':'sum', 'Pago':'sum'}).reset_index()
        resumo['Lucro'] = resumo['Recebido'] - resumo['Pago']
        top_5 = resumo.nlargest(5, 'Lucro') # Define a variável top_5 aqui
        st.plotly_chart(px.bar(top_5, x='Turma_Padronizada', y='Lucro', title="Top 5 Turmas Lucrativas", color='Lucro'))

    st.subheader("Lançamentos Detalhados")
    st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Erro: {e}")