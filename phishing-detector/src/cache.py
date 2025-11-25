"""
Sistema de cache para acelerar preprocessamento de emails.
Evita reprocessar emails idênticos múltiplas vezes.
"""

import hashlib
import pickle
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CachePreprocessamento:
    """
    Cache inteligente para textos preprocessados.
    Armazena resultados em memória e disco.
    """
    
    def __init__(self, caminho_cache: str = 'cache/preprocessamento.pkl'):
        """
        Inicializa o sistema de cache.
        
        Args:
            caminho_cache: Onde salvar cache em disco
        """
        self.caminho_cache = caminho_cache
        self.cache_memoria: Dict[str, str] = {}
        
        # Carregar cache existente do disco
        self._carregar_cache()
    
    def _gerar_hash(self, texto: str) -> str:
        """Gera hash MD5 do texto para usar como chave."""
        return hashlib.md5(texto.encode('utf-8')).hexdigest()
    
    def _carregar_cache(self) -> None:
        """Carrega cache do disco se existir."""
        if os.path.exists(self.caminho_cache):
            try:
                with open(self.caminho_cache, 'rb') as f:
                    self.cache_memoria = pickle.load(f)
                logger.info(f"✅ Cache carregado: {len(self.cache_memoria)} entradas")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar cache: {e}")
                self.cache_memoria = {}
    
    def salvar_cache(self) -> None:
        """Salva cache em disco."""
        os.makedirs(os.path.dirname(self.caminho_cache), exist_ok=True)
        try:
            with open(self.caminho_cache, 'wb') as f:
                pickle.dump(self.cache_memoria, f)
            logger.info(f"💾 Cache salvo: {len(self.cache_memoria)} entradas")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache: {e}")
    
    def obter(self, texto: str) -> Optional[str]:
        """
        Busca texto preprocessado no cache.
        
        Returns:
            Texto preprocessado ou None se não encontrado
        """
        hash_texto = self._gerar_hash(texto)
        return self.cache_memoria.get(hash_texto)
    
    def adicionar(self, texto_original: str, texto_processado: str) -> None:
        """Adiciona entrada ao cache."""
        hash_texto = self._gerar_hash(texto_original)
        self.cache_memoria[hash_texto] = texto_processado
    
    def limpar(self) -> None:
        """Limpa todo o cache."""
        self.cache_memoria.clear()
        if os.path.exists(self.caminho_cache):
            os.remove(self.caminho_cache)
        logger.info("🗑️ Cache limpo")
    
    def estatisticas(self) -> Dict:
        """Retorna estatísticas do cache."""
        return {
            'total_entradas': len(self.cache_memoria),
            'tamanho_mb': len(pickle.dumps(self.cache_memoria)) / (1024 * 1024)
        }
