"""
Módulo principal do modelo de Machine Learning para detecção de phishing.
Implementa treinamento, avaliação e predição usando Regressão Logística.
"""

import numpy as np
import logging
from typing import Tuple, Dict, List
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

from .preprocessamento import PreprocessadorTexto
from .features import ExtratorFeatures

logger = logging.getLogger(__name__)


class DetectorPhishing:
    """
    Classe principal que encapsula todo o pipeline de detecção de phishing.
    Integra pré-processamento, extração de features e modelo de ML.
    """

    def __init__(self, idioma: str = 'english', max_features: int = 3000):
        """
        Inicializa o detector de phishing.

        Args:
            idioma: Idioma para pré-processamento ('english' ou 'portuguese')
            max_features: Número máximo de features TF-IDF
        """
        self.idioma = idioma
        self.max_features = max_features

        # Componentes do pipeline
        self.preprocessador = PreprocessadorTexto(idioma=idioma)
        self.extrator = ExtratorFeatures(max_features=max_features)

        # Scaler para normalizar features (NOVO - resolve convergência)
        self.scaler = StandardScaler()

        # Modelo de ML - OTIMIZADO para melhor convergência
        self.modelo = LogisticRegression(
            C=1.0,  # Regularização
            max_iter=2000,  # AUMENTADO de 1000 para 2000
            solver='saga',  # MUDADO de lbfgs para saga (mais rápido para datasets grandes)
            random_state=42,  # Reprodutibilidade
            class_weight='balanced',  # Balancear classes automaticamente
            n_jobs=-1,  # Usar todos os cores do CPU
            verbose=0  # Silenciar avisos durante treinamento
        )

        # Flags de estado
        self.esta_treinado = False
        self.metricas = {}

        logger.info("✅ Detector de Phishing inicializado")

    def preparar_dados(self, textos: List[str], labels: np.ndarray = None,
                       test_size: float = 0.2) -> Tuple:
        """
        Prepara dados para treinamento ou predição.

        Args:
            textos: Lista de emails (texto bruto)
            labels: Array com labels (0=legítimo, 1=phishing)
            test_size: Proporção de dados para teste

        Returns:
            Se labels fornecidos: (X_train, X_test, y_train, y_test)
            Se sem labels: X (features completas)
        """
        logger.info(f"Preparando {len(textos)} emails...")

        # Manter textos originais para features de maiúsculas
        textos_originais = textos.copy()

        # Pré-processar
        textos_processados = self.preprocessador.processar_lote(textos)

        # Se for treinamento, treinar o TF-IDF
        if labels is not None and not self.esta_treinado:
            self.extrator.treinar_tfidf(textos_processados)

        # Extrair features
        X = self.extrator.extrair_features_completas(
            textos_processados,
            textos_originais
        )

        # NOVO: Normalizar features para melhor convergência
        if labels is not None and not self.esta_treinado:
            # Treinar scaler apenas no conjunto de treino
            X = self.scaler.fit_transform(X)
        elif self.esta_treinado:
            # Usar scaler já treinado
            X = self.scaler.transform(X)

        # Se tem labels, dividir em treino/teste
        if labels is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X, labels, test_size=test_size, random_state=42, stratify=labels
            )
            logger.info(f"📊 Treino: {len(X_train)} | Teste: {len(X_test)}")
            return X_train, X_test, y_train, y_test
        else:
            return X

    def treinar(self, textos: List[str], labels: np.ndarray,
                test_size: float = 0.2, validacao_cruzada: bool = True) -> Dict:
        """
        Treina o modelo de detecção de phishing.

        Args:
            textos: Lista de emails
            labels: Array com labels (0=legítimo, 1=phishing)
            test_size: Proporção de dados para teste
            validacao_cruzada: Se deve fazer validação cruzada

        Returns:
            Dicionário com métricas de performance
        """
        logger.info("🚀 Iniciando treinamento do modelo...")

        # Preparar dados
        X_train, X_test, y_train, y_test = self.preparar_dados(
            textos, labels, test_size
        )

        # Treinar modelo
        logger.info("Treinando Regressão Logística (otimizada)...")
        logger.info("⏳ Isso pode levar alguns minutos com datasets grandes...")

        self.modelo.fit(X_train, y_train)
        self.esta_treinado = True
        logger.info("✅ Modelo treinado com sucesso!")

        # Fazer predições
        y_pred_train = self.modelo.predict(X_train)
        y_pred_test = self.modelo.predict(X_test)
        y_pred_proba_test = self.modelo.predict_proba(X_test)[:, 1]

        # Calcular métricas
        metricas = {
            'acuracia_treino': accuracy_score(y_train, y_pred_train),
            'acuracia_teste': accuracy_score(y_test, y_pred_test),
            'precisao': precision_score(y_test, y_pred_test),
            'recall': recall_score(y_test, y_pred_test),
            'f1_score': f1_score(y_test, y_pred_test),
            'auc_roc': roc_auc_score(y_test, y_pred_proba_test),
            'matriz_confusao': confusion_matrix(y_test, y_pred_test)
        }

        # Validação cruzada (opcional)
        if validacao_cruzada:
            logger.info("Executando validação cruzada (5-fold)...")
            cv_scores = cross_val_score(
                self.modelo, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1
            )
            metricas['cv_mean'] = cv_scores.mean()
            metricas['cv_std'] = cv_scores.std()
            logger.info(f"📊 CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        self.metricas = metricas

        # Exibir resultados
        self._exibir_metricas(metricas)

        return metricas

    def _exibir_metricas(self, metricas: Dict) -> None:
        """
        Exibe métricas de forma visual no console.

        Args:
            metricas: Dicionário com métricas calculadas
        """
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DO TREINAMENTO")
        print("=" * 60)
        print(f"Acurácia (Treino):  {metricas['acuracia_treino'] * 100:6.2f}%")
        print(
            f"Acurácia (Teste):   {metricas['acuracia_teste'] * 100:6.2f}% {'█' * int(metricas['acuracia_teste'] * 10)}")
        print(f"Precisão:           {metricas['precisao'] * 100:6.2f}% {'█' * int(metricas['precisao'] * 10)}")
        print(f"Recall:             {metricas['recall'] * 100:6.2f}% {'█' * int(metricas['recall'] * 10)}")
        print(f"F1-Score:           {metricas['f1_score'] * 100:6.2f}% {'█' * int(metricas['f1_score'] * 10)}")
        print(f"AUC-ROC:            {metricas['auc_roc']:6.4f}")

        if 'cv_mean' in metricas:
            print(f"CV Score:           {metricas['cv_mean'] * 100:6.2f}% (+/- {metricas['cv_std'] * 100:.2f}%)")

        print("\n📈 Matriz de Confusão:")
        print(metricas['matriz_confusao'])
        print("=" * 60 + "\n")

    def predizer(self, textos: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Faz predições para novos emails.

        Args:
            textos: Lista de emails para classificar

        Returns:
            Tupla (predições, probabilidades)
            predições: Array com 0 (legítimo) ou 1 (phishing)
            probabilidades: Array com probabilidade de ser phishing (0.0 a 1.0)
        """
        if not self.esta_treinado:
            raise ValueError("❌ Modelo não foi treinado ainda! Use .treinar() primeiro.")

        # Preparar dados
        X = self.preparar_dados(textos)

        # Fazer predições
        predicoes = self.modelo.predict(X)
        probabilidades = self.modelo.predict_proba(X)[:, 1]

        return predicoes, probabilidades

    def analisar_email(self, texto: str, mostrar_features: bool = False) -> Dict:
        """
        Analisa um único email e retorna resultado detalhado.

        Args:
            texto: Texto do email
            mostrar_features: Se deve incluir features extraídas

        Returns:
            Dicionário com resultado da análise
        """
        if not self.esta_treinado:
            raise ValueError("❌ Modelo não foi treinado ainda!")

        # Predizer
        predicao, probabilidade = self.predizer([texto])

        resultado = {
            'e_phishing': bool(predicao[0]),
            'confianca': float(probabilidade[0]),
            'classificacao': 'PHISHING' if predicao[0] else 'LEGÍTIMO',
            'nivel_risco': self._calcular_nivel_risco(probabilidade[0])
        }

        # Adicionar features se solicitado
        if mostrar_features:
            from .features import criar_features_basicas
            resultado['features'] = criar_features_basicas(texto)

        return resultado

    def _calcular_nivel_risco(self, probabilidade: float) -> str:
        """
        Calcula nível de risco baseado na probabilidade.

        Args:
            probabilidade: Probabilidade de ser phishing (0.0 a 1.0)

        Returns:
            String com nível de risco
        """
        if probabilidade < 0.3:
            return "BAIXO"
        elif probabilidade < 0.7:
            return "MÉDIO"
        else:
            return "ALTO"

    def plotar_matriz_confusao(self, salvar: str = None) -> None:
        """
        Plota matriz de confusão.

        Args:
            salvar: Caminho para salvar a imagem (opcional)
        """
        if not self.metricas or 'matriz_confusao' not in self.metricas:
            logger.warning("⚠️  Nenhuma métrica disponível. Treine o modelo primeiro.")
            return

        cm = self.metricas['matriz_confusao']

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Legítimo', 'Phishing'],
                    yticklabels=['Legítimo', 'Phishing'])
        plt.title('Matriz de Confusão - Detector de Phishing', fontsize=14, fontweight='bold')
        plt.ylabel('Verdadeiro')
        plt.xlabel('Predito')
        plt.tight_layout()

        if salvar:
            plt.savefig(salvar, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Matriz de confusão salva em: {salvar}")

        plt.show()

    def obter_palavras_importantes(self, top_n: int = 20) -> Dict:
        """
        Retorna as palavras mais importantes para classificação.

        Args:
            top_n: Número de palavras a retornar

        Returns:
            Dicionário com palavras que indicam phishing e legítimo
        """
        if not self.esta_treinado:
            raise ValueError("❌ Modelo não foi treinado ainda!")

        # Obter coeficientes do modelo
        coef = self.modelo.coef_[0]

        # Obter vocabulário TF-IDF
        vocab = self.extrator.vectorizer.vocabulary_
        vocab_invertido = {v: k for k, v in vocab.items()}

        # Pegar apenas features TF-IDF (excluir features manuais no final)
        num_features_tfidf = len(vocab)
        coef_tfidf = coef[:num_features_tfidf]

        # Palavras que indicam PHISHING (coeficientes positivos altos)
        indices_phishing = np.argsort(coef_tfidf)[-top_n:][::-1]
        palavras_phishing = [(vocab_invertido[i], coef_tfidf[i]) for i in indices_phishing]

        # Palavras que indicam LEGÍTIMO (coeficientes negativos altos)
        indices_legitimo = np.argsort(coef_tfidf)[:top_n]
        palavras_legitimo = [(vocab_invertido[i], coef_tfidf[i]) for i in indices_legitimo]

        return {
            'phishing': palavras_phishing,
            'legitimo': palavras_legitimo
        }

    def salvar(self, caminho: str) -> None:
        """
        Salva o modelo completo (incluindo preprocessador e extrator).

        Args:
            caminho: Caminho do arquivo .pkl
        """
        from .utils import salvar_modelo

        if not self.esta_treinado:
            logger.warning("⚠️  Modelo não foi treinado. Salvando mesmo assim...")

        metadata = {
            'idioma': self.idioma,
            'max_features': self.max_features,
            'metricas': self.metricas
        }

        # Salvar objeto completo (self contém tudo)
        salvar_modelo(self, caminho, metadata)

    @classmethod
    def carregar(cls, caminho: str) -> 'DetectorPhishing':
        """
        Carrega modelo previamente salvo.

        Args:
            caminho: Caminho do arquivo .pkl

        Returns:
            Instância de DetectorPhishing carregada
        """
        from .utils import carregar_modelo

        detector, metadata = carregar_modelo(caminho)

        logger.info("✅ Modelo carregado com sucesso!")
        if metadata:
            logger.info(f"📋 Metadata: {metadata}")

        return detector


def exemplo_uso():
    """
    Demonstração de uso básico do detector.
    """
    print("🧪 Exemplo de uso do Detector de Phishing\n")

    # Dados de exemplo
    emails = [
        "URGENT! Your account will be suspended. Click here NOW!",
        "Hi John, the meeting is scheduled for Tuesday at 10am.",
        "You won $1,000,000! Send bank details to claim prize.",
        "Please review the attached quarterly report before Friday.",
        "Verify your identity immediately or lose access forever!"
    ]

    labels = np.array([1, 0, 1, 0, 1])  # 1=phishing, 0=legítimo

    # Criar e treinar detector
    detector = DetectorPhishing()
    detector.treinar(emails, labels, validacao_cruzada=False)

    # Testar com novo email
    novo_email = "Click here to verify your payment information urgently!"
    resultado = detector.analisar_email(novo_email, mostrar_features=True)

    print("\n🔍 Análise de novo email:")
    print(f"Classificação: {resultado['classificacao']}")
    print(f"Confiança: {resultado['confianca'] * 100:.1f}%")
    print(f"Nível de Risco: {resultado['nivel_risco']}")
    print(f"Features: {resultado['features']}")


if __name__ == "__main__":
    exemplo_uso()