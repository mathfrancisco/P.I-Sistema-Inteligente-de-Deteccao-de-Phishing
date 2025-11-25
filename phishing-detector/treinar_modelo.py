"""
Script principal para treinar o modelo de detecção de phishing.
Execute este script após preparar o dataset em dados/emails.csv
"""

import os
import sys
import argparse
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import carregar_dataset, criar_dataset_exemplo
from src.modelo import DetectorPhishing
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Função principal de treinamento.
    """
    parser = argparse.ArgumentParser(description='Treinar modelo de detecção de phishing')
    parser.add_argument('--dataset', type=str, default='dados/emails.csv',
                        help='Caminho do dataset CSV')
    parser.add_argument('--output', type=str, default='modelo/detector_phishing.pkl',
                        help='Caminho para salvar o modelo treinado')
    parser.add_argument('--criar-exemplo', action='store_true',
                        help='Criar dataset de exemplo se não existir')
    parser.add_argument('--idioma', type=str, default='english',
                        choices=['english', 'portuguese'],
                        help='Idioma para pré-processamento')
    parser.add_argument('--max-features', type=int, default=1500,
                        help='Número máximo de features TF-IDF')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Proporção de dados para teste (0.0 a 1.0)')

    # NOVO: Argumentos para colunas do CSV
    parser.add_argument('--coluna-texto', type=str, default='Email Text',
                        help='Nome da coluna contendo o texto dos emails')
    parser.add_argument('--coluna-label', type=str, default='Email Type',
                        help='Nome da coluna contendo as labels')

    args = parser.parse_args()

    print("=" * 70)
    print("🛡️  SISTEMA DE DETECÇÃO DE PHISHING - TREINAMENTO")
    print("   Grings & Filhos LTDA")
    print("=" * 70)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Verificar se dataset existe, senão criar exemplo
    if not os.path.exists(args.dataset):
        if args.criar_exemplo:
            logger.info("📊 Dataset não encontrado. Criando dataset de exemplo...")
            criar_dataset_exemplo(args.dataset, n_exemplos=200)
        else:
            logger.error(f"❌ Dataset não encontrado: {args.dataset}")
            logger.info("💡 Dica: Use --criar-exemplo para gerar dataset de teste")
            sys.exit(1)

    # Carregar dataset
    try:
        textos, labels = carregar_dataset(
            args.dataset,
            coluna_texto=args.coluna_texto,
            coluna_label=args.coluna_label
        )
        logger.info(f"✅ Dataset carregado com sucesso!")
        logger.info(f"   Total de exemplos: {len(textos)}")
        logger.info(f"   Legítimos: {(labels == 0).sum()}")
        logger.info(f"   Phishing: {(labels == 1).sum()}\n")
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dataset: {e}")
        sys.exit(1)

    # Criar e treinar detector
    try:
        logger.info("🚀 Inicializando detector de phishing...")
        detector = DetectorPhishing(
            idioma=args.idioma,
            max_features=args.max_features
        )

        logger.info("🎓 Iniciando treinamento...\n")
        metricas = detector.treinar(
            textos.tolist(),
            labels.values,
            test_size=args.test_size,
            validacao_cruzada=True
        )

        # Exibir palavras importantes
        print("\n" + "=" * 70)
        print("🔑 PALAVRAS MAIS IMPORTANTES")
        print("=" * 70)

        palavras_importantes = detector.obter_palavras_importantes(top_n=10)

        print("\n⚠️  Indicam PHISHING:")
        for palavra, peso in palavras_importantes['phishing']:
            print(f"   • {palavra:20s} (peso: {peso:+.4f})")

        print("\n✅ Indicam LEGÍTIMO:")
        for palavra, peso in palavras_importantes['legitimo'][:10]:
            print(f"   • {palavra:20s} (peso: {peso:+.4f})")

        print("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"❌ Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Salvar modelo
    try:
        logger.info(f"💾 Salvando modelo em: {args.output}")

        # Criar diretório se não existir
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

        detector.salvar(args.output)

        # Verificar tamanho do arquivo
        tamanho_mb = os.path.getsize(args.output) / (1024 * 1024)
        logger.info(f"✅ Modelo salvo com sucesso! Tamanho: {tamanho_mb:.2f} MB")

    except Exception as e:
        logger.error(f"❌ Erro ao salvar modelo: {e}")
        sys.exit(1)

    # Testar modelo com exemplos
    print("\n" + "=" * 70)
    print("🧪 TESTANDO MODELO COM EXEMPLOS")
    print("=" * 70 + "\n")

    exemplos_teste = [
        ("URGENT! Click here to verify your account NOW!", "Phishing esperado"),
        ("Hi team, meeting is scheduled for Tuesday.", "Legítimo esperado"),
        ("You won $1,000,000! Send bank details.", "Phishing esperado"),
        ("Please review the attached quarterly report.", "Legítimo esperado")
    ]

    for texto, esperado in exemplos_teste:
        resultado = detector.analisar_email(texto)
        print(f"📧 Email: {texto[:50]}...")
        print(f"   Classificação: {resultado['classificacao']} ({esperado})")
        print(f"   Confiança: {resultado['confianca'] * 100:.1f}%")
        print(f"   Risco: {resultado['nivel_risco']}\n")

    print("=" * 70)
    print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"\n💡 Próximo passo: Execute 'streamlit run app/app.py' para usar o detector\n")


if __name__ == "__main__":
    main()
