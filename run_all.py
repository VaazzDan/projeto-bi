import multiprocessing
import app, test_integridade, gerar_relatorio

def main():
    multiprocessing.freeze_support() # Essencial para evitar loops no Windows
    print("=== INICIANDO PIPELINE FINANCEIRO ===")
    try:
        app.executar_limpeza()
        test_integridade.rodar_testes_integridade()
        # gerar_relatorio.gerar_pdf() # Ative após corrigir o arquivo de relatório
        print("\n✨ Processamento Concluído!")
    except Exception as e:
        print(f"❌ Erro no Pipeline: {e}")
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()