"""
Sistema Inteligente de Detecção de Phishing
Grings & Filhos LTDA

Pacote principal contendo módulos de ML para detecção de phishing.
"""

__version__ = "1.0.0"
__author__ = "Matheus Francisco"
__email__ = "contato@gringsfilhos.com.br"

# Importações principais para facilitar uso
from .preprocessamento import PreprocessadorTexto
from .features import ExtratorFeatures
from .modelo import DetectorPhishing
from .utils import carregar_dataset, salvar_modelo, carregar_modelo

__all__ = [
    'PreprocessadorTexto',
    'ExtratorFeatures',
    'DetectorPhishing',
    'carregar_dataset',
    'salvar_modelo',
    'carregar_modelo'
]