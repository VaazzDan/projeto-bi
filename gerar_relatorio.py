import pandas as pd
from fpdf import FPDF

def gerar_pdf():
    # 1. Carregar dados gerados pelo app.py
    df = pd.read_excel("Resultado_Consultoria_Final.xlsx")
    
    # 2. Definir variáveis (Resolve o erro da sua Imagem f8228a)
    total_receita = df['Recebido'].sum()
    total_pago = df['Pago'].sum()
    total_margem = total_receita - total_pago # Definição da variável
    roi_medio = (total_margem / total_pago) if total_pago > 0 else 0
    
    # Identificação de turmas para o relatório
    resumo = df.groupby('Turma_Padronizada').agg({'Recebido':'sum', 'Pago':'sum'}).reset_index()
    resumo['Margem'] = resumo['Recebido'] - resumo['Pago']
    melhor_turma = resumo.loc[resumo['Margem'].idxmax()]
    pior_turma = resumo.loc[resumo['Margem'].idxmin()]

    # 3. Configuração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Relatório Financeiro Estratégico", ln=True, align='C')
    
    # Exemplo de uso das variáveis no diagnóstico
    pdf.set_font("Arial", size=11)
    diagnostico = f"A margem líquida total é de R$ {total_margem:,.2f}, com ROI de {roi_medio:.2f}x."
    pdf.multi_cell(0, 10, diagnostico)
    
    pdf.output("Relatorio_Consultoria_Final.pdf")
    print("✅ Relatório PDF gerado com sucesso.")