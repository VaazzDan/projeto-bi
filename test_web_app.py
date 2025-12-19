import pytest
import pandas as pd
from web_app import limpar_valor, extrair_id, gerar_sugestao, normalizar_texto

# --- TESTES DE LIMPEZA FINANCEIRA ---
def test_limpar_valor_moeda():
    """Garante que o R$ e pontos de milhar sejam removidos corretamente."""
    assert limpar_valor("R$ 1.500,50") == 1500.50
    assert limpar_valor("1.200") == 1200.0
    assert limpar_valor(2500) == 2500.0

def test_limpar_valor_invalido():
    """Garante que textos inválidos não quebrem o sistema (retornando 0.0)."""
    assert limpar_valor("texto") == 0.0
    assert limpar_valor(None) == 0.0

# --- TESTES DE REGRA DE NEGÓCIO (REGRA DANILO) ---
def test_extrair_id_esquerda():
    """Valida se o ID numérico é capturado corretamente no início da string."""
    assert extrair_id("25016 PSICOLOGIA UNINGA") == "25016"
    assert extrair_id("100 teste") == "100"
    assert extrair_id("Sem ID aqui") is None

def test_gerar_sugestao_limpeza_direita():
    """Valida se sufixos numéricos e espaços extras são removidos do final."""
    assert gerar_sugestao("25016 PSICOLOGIA 2") == "25016 PSICOLOGIA"
    assert gerar_sugestao("PSICOLOGIA UNINGA 2024.1") == "PSICOLOGIA UNINGA"
    assert gerar_sugestao("TURMA TESTE   ") == "TURMA TESTE"

# --- TESTES DE NORMALIZAÇÃO ---
def test_normalizar_texto_acentos():
    """Valida a remoção de acentos e caracteres especiais."""
    assert normalizar_texto("AçãO e Café") == "acao e cafe"
    assert normalizar_texto("Nº Controle-1") == "n controle 1"

def test_normalizar_texto_vazio():
    """Valida comportamento com valores nulos."""
    assert normalizar_texto(None) == ""