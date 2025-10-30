"""
Módulo de extração de features para detecção de phishing.
Transforma texto em características numéricas para o modelo de ML.
"""

import re
import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)


class ExtratorFeatures:
    """
    Classe responsável por extrair features de emails para classificação.
    Combina TF-IDF com features manuais específicas de phishing.
    """

    def __init__(self, max_features: int = 3000, ngram_range: tuple = (1, 2)):
        """
        Inicializa o extrator de features.

        Args:
            max_features: Número máximo de features TF-IDF
            ngram_range: Tupla (min, max) para n-gramas (ex: (1,2) = unigramas e bigramas)
        """
        self.max_features = max_features
        self.ngram_range = ngram_range

        # Vetorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=2,  # Palavra deve aparecer em pelo menos 2 documentos
            max_df=0.8,  # Palavra não pode aparecer em mais de 80% dos documentos
            sublinear_tf=True  # Usar escala log para TF
        )

        # Palavras-chave de urgência comuns em phishing
        self.palavras_urgencia = [
            'urgent', 'immediately', 'now', 'expire', 'suspended',
            'verify', 'confirm', 'click', 'act', 'limited', 'hurry'
        ]

        # Palavras relacionadas a dinheiro/finanças
        self.palavras_financeiras = [
            'money', 'bank', 'account', 'credit', 'card', 'payment',
            'invoice', 'transfer', 'wire', 'dollar', 'prize', 'winner'
        ]

        logger.info(f"✅ Extrator de features inicializado (max_features={max_features})")

    def contar_urls(self, texto: str) -> int:
        """
        Conta número de URLs no texto.

        Args:
            texto: Texto do email

        Returns:
            Número de URLs encontradas
        """
        padrao_url = r'http[s]?://|URL_TOKEN|www\.'
        urls = re.findall(padrao_url, texto.lower())
        return len(urls)

    def proporcao_maiusculas(self, texto: str) -> float:
        """
        Calcula proporção de letras maiúsculas (indicador de spam/phishing).

        Args:
            texto: Texto original (antes do lowercase)

        Returns:
            Proporção de maiúsculas (0.0 a 1.0)
        """
        if not texto:
            return 0.0

        letras = [c for c in texto if c.isalpha()]
        if not letras:
            return 0.0

        maiusculas = sum(1 for c in letras if c.isupper())
        return maiusculas / len(letras)

    def contar_caracteres_especiais(self, texto: str) -> int:
        """
        Conta caracteres especiais (!?$% etc).

        Args:
            texto: Texto do email

        Returns:
            Número de caracteres especiais
        """
        especiais = r'[!?$%&*@#]'
        return len(re.findall(especiais, texto))

    def detectar_palavras_urgencia(self, texto: str) -> int:
        """
        Conta palavras que indicam urgência.

        Args:
            texto: Texto preprocessado (lowercase)

        Returns:
            Número de palavras de urgência encontradas
        """
        texto_lower = texto.lower()
        return sum(1 for palavra in self.palavras_urgencia if palavra in texto_lower)

    def detectar_palavras_financeiras(self, texto: str) -> int:
        """
        Conta palavras relacionadas a finanças.

        Args:
            texto: Texto preprocessado

        Returns:
            Número de palavras financeiras encontradas
        """
        texto_lower = texto.lower()
        return sum(1 for palavra in self.palavras_financeiras if palavra in texto_lower)

    def tamanho_texto(self, texto: str) -> int:
        """
        Retorna número de palavras no texto.

        Args:
            texto: Texto do email

        Returns:
            Número de palavras
        """
        return len(texto.split())

    def extrair_features_manuais(self, textos: List[str],
                                 textos_originais: List[str] = None) -> pd.DataFrame:
        """
        Extrai features manuais (não TF-IDF) de uma lista de textos.

        Args:
            textos: Lista de textos preprocessados
            textos_originais: Lista de textos originais (para proporção de maiúsculas)

        Returns:
            DataFrame com features manuais
        """
        if textos_originais is None:
            textos_originais = textos

        features = []

        for texto, original in zip(textos, textos_originais):
            features.append({
                'num_urls': self.contar_urls(texto),
                'prop_maiusculas': self.proporcao_maiusculas(original),
                'num_especiais': self.contar_caracteres_especiais(original),
                'palavras_urgencia': self.detectar_palavras_urgencia(texto),
                'palavras_financeiras': self.detectar_palavras_financeiras(texto),
                'tamanho_texto': self.tamanho_texto(texto)
            })

        return pd.DataFrame(features)

    def treinar_tfidf(self, textos: List[str]) -> None:
        """
        Treina o vetorizador TF-IDF com os textos fornecidos.

        Args:
            textos: Lista de textos preprocessados para treino
        """
        logger.info(f"Treinando TF-IDF com {len(textos)} textos...")
        self.vectorizer.fit(textos)

        vocab_size = len(self.vectorizer.vocabulary_)
        logger.info(f"✅ TF-IDF treinado! Vocabulário: {vocab_size} termos")

    def transformar_tfidf(self, textos: List[str]) -> np.ndarray:
        """
        Transforma textos em features TF-IDF.

        Args:
            textos: Lista de textos preprocessados

        Returns:
            Matriz TF-IDF (sparse matrix convertida para array)
        """
        return self.vectorizer.transform(textos).toarray()

    def extrair_features_completas(self, textos: List[str],
                                   textos_originais: List[str] = None) -> np.ndarray:
        """
        Extrai TODAS as features (TF-IDF + manuais) de uma vez.

        Args:
            textos: Lista de textos preprocessados
            textos_originais: Lista de textos originais

        Returns:
            Array numpy com todas as features concatenadas
        """
        logger.info(f"Extraindo features de {len(textos)} textos...")

        # Features TF-IDF
        features_tfidf = self.transformar_tfidf(textos)
        logger.debug(f"TF-IDF shape: {features_tfidf.shape}")

        # Features manuais
        features_manuais = self.extrair_features_manuais(textos, textos_originais)
        logger.debug(f"Features manuais shape: {features_manuais.shape}")

        # Concatenar horizontalmente
        features_completas = np.hstack([features_tfidf, features_manuais.values])

        logger.info(f"✅ Features extraídas! Shape final: {features_completas.shape}")
        return features_completas

    def obter_features_mais_importantes(self, top_n: int = 20) -> List[tuple]:
        """
        Retorna as N palavras mais importantes do vocabulário TF-IDF.

        Args:
            top_n: Número de termos a retornar

        Returns:
            Lista de tuplas (termo, índice)
        """
        if not hasattr(self.vectorizer, 'vocabulary_'):
            raise ValueError("TF-IDF não foi treinado ainda!")

        vocab = self.vectorizer.vocabulary_
        # Ordenar por índice (termos mais frequentes têm índices menores)
        termos_ordenados = sorted(vocab.items(), key=lambda x: x[1])

        return termos_ordenados[:top_n]


def criar_features_basicas(texto: str) -> Dict[str, any]:
    """
    Função de conveniência para extrair features básicas de um único texto.
    Útil para análise rápida ou debugging.

    Args:
        texto: Texto do email

    Returns:
        Dicionário com features
    """
    extrator = ExtratorFeatures()

    features = {
        'num_urls': extrator.contar_urls(texto),
        'prop_maiusculas': extrator.proporcao_maiusculas(texto),
        'num_especiais': extrator.contar_caracteres_especiais(texto),
        'palavras_urgencia': extrator.detectar_palavras_urgencia(texto),
        'palavras_financeiras': extrator.detectar_palavras_financeiras(texto),
        'tamanho_texto': extrator.tamanho_texto(texto)
    }

    return features


if __name__ == "__main__":
    # Teste do módulo
    print("🧪 Testando extração de features...\n")

    texto_phishing = "URGENT! Click here http://fake.com to verify account NOW!"
    texto_normal = "Hi, the meeting is scheduled for Tuesday at 10am. See you there."

    print("📧 Texto 1 (Phishing):")
    print(texto_phishing)
    features1 = criar_features_basicas(texto_phishing)
    print(f"Features: {features1}\n")

    print("📧 Texto 2 (Normal):")
    print(texto_normal)
    features2 = criar_features_basicas(texto_normal)
    print(f"Features: {features2}\n")

    print("✅ Teste concluído!")