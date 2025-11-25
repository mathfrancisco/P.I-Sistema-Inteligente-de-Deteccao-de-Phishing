"""
Módulo de pré-processamento de texto para detecção de phishing.
Realiza limpeza, normalização e preparação de emails para análise.
"""

import re
import string
import logging
from typing import List
import nltk
from nltk.corpus import stopwords
from .cache import CachePreprocessamento
from multiprocessing import Pool, cpu_count

logger = logging.getLogger(__name__)

# Baixar recursos do NLTK se necessário
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Baixando recursos do NLTK...")
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)


class PreprocessadorTexto:
    """
    Classe responsável por todas as operações de pré-processamento de texto.
    """

    def __init__(self, idioma: str = 'english', remover_stopwords: bool = True):
        """
        Inicializa o preprocessador.

        Args:
            idioma: Idioma para remoção de stopwords ('english' ou 'portuguese')
            remover_stopwords: Se deve remover stopwords
        """
        self.idioma = idioma
        self.remover_stopwords = remover_stopwords
        self.cache = CachePreprocessamento()

        # Carregar stopwords
        if remover_stopwords:
            try:
                self.stopwords = set(stopwords.words(idioma))
                logger.info(f"✅ Stopwords carregados ({idioma}): {len(self.stopwords)} palavras")
            except:
                logger.warning(f"⚠️  Não foi possível carregar stopwords para '{idioma}'")
                self.stopwords = set()
        else:
            self.stopwords = set()

        # Palavras de urgência comuns em phishing (não remover)
        self.palavras_urgencia = {
            'urgent', 'immediately', 'now', 'act', 'verify', 'confirm',
            'suspended', 'expires', 'limited', 'expire', 'hurry', 'quick'
        }

        # Atualizar stopwords para não remover palavras importantes
        self.stopwords = self.stopwords - self.palavras_urgencia

    def limpar_url(self, texto: str) -> str:
        """
        Remove URLs do texto, mas mantém marcador para feature engineering.

        Args:
            texto: Texto original

        Returns:
            Texto com URLs substituídas por marcador
        """
        # Padrão para detectar URLs
        padrao_url = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        # Contar URLs antes de remover
        urls_encontradas = re.findall(padrao_url, texto)

        # Substituir por marcador
        texto_limpo = re.sub(padrao_url, ' URL_TOKEN ', texto)

        if urls_encontradas:
            logger.debug(f"🔗 URLs encontradas: {len(urls_encontradas)}")

        return texto_limpo

    def limpar_caracteres_especiais(self, texto: str) -> str:
        """
        Remove caracteres especiais, mantendo apenas letras, números e espaços.

        Args:
            texto: Texto com caracteres especiais

        Returns:
            Texto limpo
        """
        # Preservar URL_TOKEN se existir
        has_url_token = 'URL_TOKEN' in texto

        # Remover pontuação
        texto = texto.translate(str.maketrans('', '', string.punctuation))

        # Remover caracteres não-ASCII
        texto = texto.encode('ascii', 'ignore').decode('ascii')

        # Restaurar URL_TOKEN
        if has_url_token:
            texto = texto.replace('URLTOKEN', 'URL_TOKEN')

        return texto

    def normalizar_espacos(self, texto: str) -> str:
        """
        Normaliza espaços em branco múltiplos para um único espaço.

        Args:
            texto: Texto com espaços irregulares

        Returns:
            Texto com espaços normalizados
        """
        # Remover tabs, newlines, múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()

    def remover_stopwords_texto(self, texto: str) -> str:
        """
        Remove stopwords do texto.

        Args:
            texto: Texto com stopwords

        Returns:
            Texto sem stopwords
        """
        if not self.remover_stopwords:
            return texto

        palavras = texto.split()
        palavras_filtradas = [
            palavra for palavra in palavras
            if palavra.lower() not in self.stopwords
        ]

        return ' '.join(palavras_filtradas)

    def processar(self, texto: str) -> str:
    """Pipeline com cache."""
    if not texto or not isinstance(texto, str):
        return ""
    
    # ⚡ Verificar cache primeiro
    resultado_cache = self.cache.obter(texto)
    if resultado_cache is not None:
        return resultado_cache
    
    # Processar normalmente
    texto_processado = self._processar_sem_cache(texto)
    
    # Salvar no cache
    self.cache.adicionar(texto, texto_processado)
    
    return texto_processado

    def _processar_sem_cache(self, texto: str) -> str:
    """Lógica original de processamento."""
    # Mover toda a lógica atual de processar() para cá
    texto = texto.lower()
    texto = self.limpar_url(texto)
    texto = self.limpar_caracteres_especiais(texto)
    texto = self.normalizar_espacos(texto)
    texto = self.remover_stopwords_texto(texto)
    return texto

    def processar_lote(self, textos: List[str], usar_paralelo: bool = True) -> List[str]:
    """Processa múltiplos textos em paralelo."""
    logger.info(f"Processando lote de {len(textos)} textos...")
    
    if not usar_paralelo or len(textos) < 100:
        # Para lotes pequenos, processar sequencialmente
        return [self.processar(texto) for texto in textos]
    
    # ⚡ Processamento paralelo para lotes grandes
    num_workers = max(1, cpu_count() - 1)  # Deixar 1 core livre
    logger.info(f"🚀 Usando {num_workers} processos paralelos")
    
    with Pool(num_workers) as pool:
        textos_processados = pool.map(self.processar, textos)
    
    logger.info("✅ Lote processado com sucesso!")
    return textos_processados


# Função de conveniência para uso rápido
def preprocessar_texto(texto: str, idioma: str = 'english',
                       remover_stopwords: bool = True) -> str:
    """
    Função auxiliar para pré-processar um único texto rapidamente.

    Args:
        texto: Texto bruto
        idioma: Idioma para stopwords
        remover_stopwords: Se deve remover stopwords

    Returns:
        Texto processado
    """
    preprocessador = PreprocessadorTexto(idioma=idioma,
                                         remover_stopwords=remover_stopwords)
    return preprocessador.processar(texto)


if __name__ == "__main__":
    # Teste do módulo
    print("🧪 Testando módulo de pré-processamento...\n")

    texto_teste = """
    URGENT! Your account will be SUSPENDED immediately!
    Click here: http://fakephishing.com/verify?id=12345
    Confirm your details NOW or lose access forever!!!
    """

    print("Texto original:")
    print("-" * 50)
    print(texto_teste)
    print("-" * 50)

    preprocessador = PreprocessadorTexto(idioma='english')
    texto_limpo = preprocessador.processar(texto_teste)

    print("\nTexto processado:")
    print("-" * 50)
    print(texto_limpo)
    print("-" * 50)
    print("\n✅ Teste concluído!")
