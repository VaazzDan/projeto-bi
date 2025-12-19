import pandas as pd

def rodar_testes():
    print("--- 🧪 INICIANDO TESTES DE INTEGRIDADE (CONCILIAÇÃO) ---")
    df_orig = pd.read_excel("dados_financeiros.xlsx")
    df_proc = pd.read_excel("Resultado_Consultoria_Final.xlsx")
    
    # O saldo final (Recebido - Pago) deve ser igual à soma da coluna Valor original
    saldo_original = round(df_orig['Valor'].sum(), 2)
    saldo_processado = round(df_proc['Recebido'].sum() - df_proc['Pago'].sum(), 2)
    
    if saldo_original == saldo_processado:
        print(f"✅ SUCESSO: O saldo de R$ {saldo_original:,.2f} foi conciliado perfeitamente.")
    else:
        print(f"❌ ERRO: Divergência de R$ {abs(saldo_original - saldo_processado):,.2f} detectada.")

if __name__ == "__main__":
    rodar_testes()