"""
Script para avaliar um modelo treinado e gerar visualizações.
Útil para análise detalhada de performance e geração de relatórios.
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.modelo import DetectorPhishing
from src.utils import carregar_dataset
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import roc_curve, auc, classification_report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plotar_curva_roc(y_true, y_proba, salvar=None):
    """
    Plota curva ROC (Receiver Operating Characteristic).

    Args:
        y_true: Labels verdadeiros
        y_proba: Probabilidades preditas
        salvar: Caminho para salvar imagem (opcional)
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2,
             label=f'Curva ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
             label='Classificador Aleatório')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taxa de Falsos Positivos', fontsize=12)
    plt.ylabel('Taxa de Verdadeiros Positivos', fontsize=12)
    plt.title('Curva ROC - Detector de Phishing', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    if salvar:
        plt.savefig(salvar, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Curva ROC salva em: {salvar}")

    plt.show()


def plotar_distribuicao_confianca(y_true, y_proba, salvar=None):
    """
    Plota distribuição de confiança das predições.

    Args:
        y_true: Labels verdadeiros
        y_proba: Probabilidades preditas
        salvar: Caminho para salvar imagem
    """
    plt.figure(figsize=(12, 6))

    # Separar por classe
    proba_legitimo = y_proba[y_true == 0]
    proba_phishing = y_proba[y_true == 1]

    plt.hist(proba_legitimo, bins=30, alpha=0.6, label='Legítimo (real)', color='green')
    plt.hist(proba_phishing, bins=30, alpha=0.6, label='Phishing (real)', color='red')

    plt.axvline(x=0.5, color='black', linestyle='--', linewidth=2,
                label='Threshold (0.5)')

    plt.xlabel('Probabilidade de ser Phishing', fontsize=12)
    plt.ylabel('Frequência', fontsize=12)
    plt.title('Distribuição de Confiança das Predições', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    if salvar:
        plt.savefig(salvar, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Distribuição salva em: {salvar}")

    plt.show()


def analisar_erros(detector, textos, y_true, y_pred, y_proba, n_exemplos=5):
    """
    Analisa e exibe exemplos de erros do modelo.

    Args:
        detector: Instância do DetectorPhishing
        textos: Lista de textos
        y_true: Labels verdadeiros
        y_pred: Labels preditos
        y_proba: Probabilidades preditas
        n_exemplos: Número de exemplos a exibir
    """
    print("\n" + "=" * 70)
    print("❌ ANÁLISE DE ERROS")
    print("=" * 70 + "\n")

    # Falsos Positivos (previu phishing, mas era legítimo)
    fp_indices = np.where((y_pred == 1) & (y_true == 0))[0]
    print(f"🔴 Falsos Positivos: {len(fp_indices)} casos")
    print("   (Classificou como phishing, mas era legítimo)\n")

    for i, idx in enumerate(fp_indices[:n_exemplos]):
        print(f"   Exemplo {i + 1}:")
        print(f"   Texto: {textos[idx][:80]}...")
        print(f"   Confiança: {y_proba[idx] * 100:.1f}%\n")

    # Falsos Negativos (previu legítimo, mas era phishing)
    fn_indices = np.where((y_pred == 0) & (y_true == 1))[0]
    print(f"🔴 Falsos Negativos: {len(fn_indices)} casos")
    print("   (Classificou como legítimo, mas era phishing)\n")

    for i, idx in enumerate(fn_indices[:n_exemplos]):
        print(f"   Exemplo {i + 1}:")
        print(f"   Texto: {textos[idx][:80]}...")
        print(f"   Confiança: {y_proba[idx] * 100:.1f}%\n")

    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Avaliar modelo de detecção de phishing')
    parser.add_argument('--modelo', type=str, default='modelo/detector_phishing.pkl',
                        help='Caminho do modelo treinado')
    parser.add_argument('--dataset', type=str, default='dados/emails.csv',
                        help='Caminho do dataset para teste')
    parser.add_argument('--output-dir', type=str, default='resultados',
                        help='Diretório para salvar visualizações')

    args = parser.parse_args()

    print("=" * 70)
    print("📊 AVALIAÇÃO DO MODELO DE DETECÇÃO DE PHISHING")
    print("=" * 70 + "\n")

    # Criar diretório de saída
    os.makedirs(args.output_dir, exist_ok=True)

    # Carregar modelo
    try:
        logger.info(f"Carregando modelo de: {args.modelo}")
        detector = DetectorPhishing.carregar(args.modelo)
        logger.info("✅ Modelo carregado!\n")
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {e}")
        sys.exit(1)

    # Carregar dataset de teste
    try:
        logger.info(f"Carregando dataset de: {args.dataset}")
        textos, labels = carregar_dataset(args.dataset)
        logger.info(f"✅ Dataset carregado: {len(textos)} exemplos\n")
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dataset: {e}")
        sys.exit(1)

    # Fazer predições
    logger.info("🔮 Fazendo predições...")
    y_pred, y_proba = detector.predizer(textos.tolist())
    logger.info("✅ Predições concluídas!\n")

    # Relatório de classificação
    print("=" * 70)
    print("📋 RELATÓRIO DE CLASSIFICAÇÃO")
    print("=" * 70)
    print(classification_report(labels, y_pred,
                                target_names=['Legítimo', 'Phishing'],
                                digits=4))
    print("=" * 70 + "\n")

    # Plotar matriz de confusão
    logger.info("📊 Gerando matriz de confusão...")
    detector.metricas['matriz_confusao'] = np.array([[
        ((y_pred == 0) & (labels == 0)).sum(),
        ((y_pred == 1) & (labels == 0)).sum()
    ], [
        ((y_pred == 0) & (labels == 1)).sum(),
        ((y_pred == 1) & (labels == 1)).sum()
    ]])

    detector.plotar_matriz_confusao(
        salvar=os.path.join(args.output_dir, 'matriz_confusao.png')
    )

    # Plotar curva ROC
    logger.info("📈 Gerando curva ROC...")
    plotar_curva_roc(labels, y_proba,
                     salvar=os.path.join(args.output_dir, 'curva_roc.png'))

    # Plotar distribuição de confiança
    logger.info("📊 Gerando distribuição de confiança...")
    plotar_distribuicao_confianca(labels, y_proba,
                                  salvar=os.path.join(args.output_dir, 'distribuicao_confianca.png'))

    # Analisar erros
    analisar_erros(detector, textos.tolist(), labels.values, y_pred, y_proba)

    # Palavras importantes
    print("=" * 70)
    print("🔑 TOP 15 PALAVRAS MAIS IMPORTANTES")
    print("=" * 70 + "\n")

    palavras = detector.obter_palavras_importantes(top_n=15)

    print("⚠️  Indicam PHISHING:")
    for palavra, peso in palavras['phishing']:
        print(f"   {palavra:20s} {'█' * int(peso * 10):20s} {peso:+.4f}")

    print("\n✅ Indicam LEGÍTIMO:")
    for palavra, peso in palavras['legitimo']:
        print(f"   {palavra:20s} {'█' * int(abs(peso) * 10):20s} {peso:+.4f}")

    print("\n" + "=" * 70)
    print(f"✅ Avaliação concluída! Resultados salvos em: {args.output_dir}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()