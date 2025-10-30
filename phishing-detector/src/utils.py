"""
Funções auxiliares para o sistema de detecção de phishing.
Inclui operações de I/O, logging e utilitários gerais.
"""

import os
import pickle
import pandas as pd
import logging
from typing import Tuple, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def carregar_dataset(caminho: str, coluna_texto: str = 'text',
                     coluna_label: str = 'label') -> Tuple[pd.Series, pd.Series]:
    """
    Carrega dataset de emails a partir de arquivo CSV.

    Args:
        caminho: Caminho para o arquivo CSV
        coluna_texto: Nome da coluna contendo o texto dos emails
        coluna_label: Nome da coluna contendo as labels (0=legítimo, 1=phishing)

    Returns:
        Tupla (textos, labels) como pandas Series

    Raises:
        FileNotFoundError: Se o arquivo não existir
        KeyError: Se as colunas especificadas não existirem
    """
    logger.info(f"Carregando dataset de: {caminho}")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    try:
        df = pd.read_csv(caminho, encoding='utf-8')
        logger.info(f"✅ Dataset carregado: {len(df)} exemplos")

        # Debug: mostrar colunas disponíveis
        logger.info(f"📋 Colunas encontradas: {df.columns.tolist()}")

        # Verificar colunas necessárias
        if coluna_texto not in df.columns:
            raise KeyError(f"Coluna '{coluna_texto}' não encontrada. Colunas disponíveis: {df.columns.tolist()}")
        if coluna_label not in df.columns:
            raise KeyError(f"Coluna '{coluna_label}' não encontrada. Colunas disponíveis: {df.columns.tolist()}")

        # Remover valores nulos
        df = df.dropna(subset=[coluna_texto, coluna_label])
        logger.info(f"📊 Após remoção de nulos: {len(df)} exemplos")

        # Converter labels de texto para numérico (0 e 1)
        labels_originais = df[coluna_label].unique()
        logger.info(f"🏷️  Labels originais encontradas: {labels_originais}")

        # Mapear labels para 0 (legítimo) e 1 (phishing)
        # Detectar automaticamente qual é phishing baseado em palavras-chave
        label_mapping = {}

        for label in labels_originais:
            label_lower = str(label).lower()
            # Se contém "phish", "spam", "malicious", "unsafe" -> 1 (phishing)
            if any(word in label_lower for word in ['phish', 'spam', 'malicious', 'unsafe', 'scam']):
                label_mapping[label] = 1
            # Se contém "safe", "ham", "legitimate", "normal" -> 0 (legítimo)
            elif any(word in label_lower for word in ['safe', 'ham', 'legitimate', 'normal', 'legit']):
                label_mapping[label] = 0
            else:
                # Se não conseguir detectar, assumir pela ordem alfabética
                # (geralmente "Phishing Email" vem depois de "Safe Email")
                label_mapping[label] = 1 if label == max(labels_originais) else 0

        logger.info(f"🔄 Mapeamento de labels: {label_mapping}")

        df['label_numeric'] = df[coluna_label].map(label_mapping)

        # Verificar se há valores não mapeados
        if df['label_numeric'].isna().any():
            logger.warning("⚠️  Algumas labels não foram mapeadas corretamente!")
            logger.warning(f"Labels problemáticas: {df[df['label_numeric'].isna()][coluna_label].unique()}")
            # Remover linhas com labels não mapeadas
            df = df.dropna(subset=['label_numeric'])

        # Exibir distribuição de classes
        distribuicao = df['label_numeric'].value_counts()
        logger.info(f"📈 Distribuição - Legítimos (0): {distribuicao.get(0, 0)} | Phishing (1): {distribuicao.get(1, 0)}")

        return df[coluna_texto], df['label_numeric'].astype(int)

    except Exception as e:
        logger.error(f"❌ Erro ao carregar dataset: {str(e)}")
        raise


def salvar_modelo(modelo: Any, caminho: str, metadata: dict = None) -> None:
    """
    Salva modelo treinado em arquivo pickle.

    Args:
        modelo: Objeto do modelo (sklearn pipeline ou modelo individual)
        caminho: Caminho onde salvar o arquivo .pkl
        metadata: Dicionário com informações adicionais (acurácia, data, etc.)
    """
    logger.info(f"Salvando modelo em: {caminho}")

    # Criar diretório se não existir
    diretorio = os.path.dirname(caminho)
    if diretorio and not os.path.exists(diretorio):
        os.makedirs(diretorio)
        logger.info(f"📁 Diretório criado: {diretorio}")

    # Adicionar timestamp ao metadata
    if metadata is None:
        metadata = {}
    metadata['data_salvamento'] = datetime.now().isoformat()

    # Salvar modelo e metadata juntos
    dados_salvamento = {
        'modelo': modelo,
        'metadata': metadata
    }

    try:
        with open(caminho, 'wb') as f:
            pickle.dump(dados_salvamento, f)

        tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)
        logger.info(f"✅ Modelo salvo com sucesso! Tamanho: {tamanho_mb:.2f} MB")

        if metadata:
            logger.info(f"📋 Metadata: {metadata}")

    except Exception as e:
        logger.error(f"❌ Erro ao salvar modelo: {str(e)}")
        raise


def carregar_modelo(caminho: str) -> Tuple[Any, dict]:
    """
    Carrega modelo treinado de arquivo pickle.

    Args:
        caminho: Caminho do arquivo .pkl

    Returns:
        Tupla (modelo, metadata)

    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    logger.info(f"Carregando modelo de: {caminho}")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Modelo não encontrado: {caminho}")

    try:
        with open(caminho, 'rb') as f:
            dados = pickle.load(f)

        # Compatibilidade com modelos salvos sem metadata
        if isinstance(dados, dict) and 'modelo' in dados:
            modelo = dados['modelo']
            metadata = dados.get('metadata', {})
        else:
            modelo = dados
            metadata = {}

        logger.info("✅ Modelo carregado com sucesso!")
        if metadata:
            logger.info(f"📋 Metadata: {metadata}")

        return modelo, metadata

    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {str(e)}")
        raise


def criar_dataset_exemplo(caminho_saida: str = 'dados/exemplo.csv', n_exemplos: int = 100) -> None:
    """
    Cria dataset de exemplo para testes (usado quando não há dataset real).

    Args:
        caminho_saida: Caminho onde salvar o CSV
        n_exemplos: Número de exemplos a gerar
    """
    logger.info(f"Gerando dataset de exemplo com {n_exemplos} exemplos...")

    # Exemplos de phishing
    phishing = [
        "URGENT! Your account will be closed. Click here immediately to verify your information.",
        "Congratulations! You won $1,000,000. Send your bank details now to claim prize.",
        "Security Alert: Suspicious activity detected. Update your password at this link NOW.",
        "Your package is waiting. Pay delivery fee to receive: bit.ly/fakelnk",
        "Dear Customer, your invoice is attached. Please wire payment to new bank account urgently.",
        "Limited time offer! Click now to get 90% discount on luxury watches!",
        "Your Netflix subscription has expired. Update payment here to continue service.",
        "IRS Tax Refund: You are eligible for $2,500 refund. Confirm details immediately.",
        "WARNING: Your computer is infected with virus. Download antivirus now!",
        "Verify your identity to unlock your Facebook account. Click here within 24 hours."
    ]

    # Exemplos legítimos
    legitimo = [
        "Hi John, the meeting is scheduled for next Tuesday at 10am. Please confirm.",
        "Thank you for your purchase. Your order #12345 will arrive on Monday.",
        "Quarterly financial report is attached. Please review before board meeting.",
        "Team lunch this Friday at the Italian restaurant. Looking forward to seeing everyone.",
        "Your subscription renews on May 15th. No action needed if you wish to continue.",
        "Welcome to our newsletter! Here are this week's industry insights.",
        "Reminder: Annual compliance training must be completed by end of month.",
        "Invoice #2024-001 for consulting services is attached for your records.",
        "Performance review scheduled for next week. Please prepare self-assessment.",
        "Project update: Phase 1 completed successfully. Moving to Phase 2 next month."
    ]

    # Replicar para atingir n_exemplos
    textos = []
    labels = []

    for i in range(n_exemplos):
        if i % 2 == 0:
            textos.append(phishing[i % len(phishing)])
            labels.append(1)  # phishing
        else:
            textos.append(legitimo[i % len(legitimo)])
            labels.append(0)  # legítimo

    # Criar DataFrame e salvar
    df = pd.DataFrame({
        'text': textos,
        'label': labels
    })

    # Criar diretório se não existir
    diretorio = os.path.dirname(caminho_saida)
    if diretorio and not os.path.exists(diretorio):
        os.makedirs(diretorio)

    df.to_csv(caminho_saida, index=False, encoding='utf-8')
    logger.info(f"✅ Dataset de exemplo criado: {caminho_saida}")
    logger.info(f"📊 Total: {len(df)} exemplos (50% phishing, 50% legítimo)")


def exibir_estatisticas(y_true, y_pred) -> None:
    """
    Exibe estatísticas de performance de forma visual no console.

    Args:
        y_true: Labels verdadeiros
        y_pred: Labels preditos
    """
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print("\n" + "=" * 50)
    print("📊 MÉTRICAS DE PERFORMANCE")
    print("=" * 50)
    print(f"Acurácia:  {acc * 100:6.2f}% {'█' * int(acc * 10)}")
    print(f"Precisão:  {prec * 100:6.2f}% {'█' * int(prec * 10)}")
    print(f"Recall:    {rec * 100:6.2f}% {'█' * int(rec * 10)}")
    print(f"F1-Score:  {f1 * 100:6.2f}% {'█' * int(f1 * 10)}")
    print("=" * 50 + "\n")