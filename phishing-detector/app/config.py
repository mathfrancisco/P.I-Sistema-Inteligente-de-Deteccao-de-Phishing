"""
Configurações da aplicação web de detecção de phishing.
Centraliza constantes, caminhos e parâmetros visuais.
"""

import os

# ============================================
# INFORMAÇÕES DA EMPRESA
# ============================================
EMPRESA_NOME = "Grings & Filhos LTDA"
EMPRESA_CNPJ = "03.102.452/0001-72"
PROJETO_AUTOR = "Matheus Francisco - RA 24001882"

# ============================================
# CAMINHOS DE ARQUIVOS
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO_PATH = os.path.join(BASE_DIR, 'modelo', 'detector_phishing.pkl')
LOGO_PATH = os.path.join(BASE_DIR, 'app', 'assets', 'logo.png')

# ============================================
# CONFIGURAÇÕES DO MODELO
# ============================================
THRESHOLD_RISCO_BAIXO = 0.3
THRESHOLD_RISCO_MEDIO = 0.7

# ============================================
# TEXTOS DA INTERFACE
# ============================================
TITULO_APP = "🛡️ Sistema de Detecção de Phishing"
SUBTITULO_APP = "Proteção Inteligente Contra Fraudes por Email"

INSTRUCOES = """
### 📋 Como usar:
1. **Cole o texto completo** do email suspeito na área abaixo
2. Clique em **"🔍 Analisar Email"**
3. Aguarde a análise (< 2 segundos)
4. Siga as **recomendações** apresentadas

⚠️ **Importante:** Este sistema é uma ferramenta auxiliar. Em caso de dúvida, 
sempre consulte o setor de TI antes de tomar qualquer ação.
"""

EXEMPLO_EMAIL_PHISHING = """URGENT SECURITY ALERT!

Your account has been temporarily suspended due to suspicious activity.

Click here immediately to verify your identity:
http://fake-verification-link.com/verify?id=12345

You have 24 hours to confirm your information or your account will be permanently closed.

Act now to avoid losing access to your account!

Best regards,
Security Team
"""

EXEMPLO_EMAIL_LEGITIMO = """Hi John,

I hope this email finds you well.

I wanted to follow up on our meeting last Tuesday regarding the Q4 project timeline. 
As discussed, I've attached the updated proposal with the revised budget estimates.

Could you please review it and let me know your thoughts by Friday? 
We can schedule another call next week if needed.

Looking forward to hearing from you.

Best regards,
Maria Silva
Project Manager
Grings & Filhos LTDA
"""

# ============================================
# RECOMENDAÇÕES POR NÍVEL DE RISCO
# ============================================
RECOMENDACOES = {
    'BAIXO': {
        'emoji': '✅',
        'titulo': 'Risco Baixo',
        'cor': 'green',
        'acoes': [
            "Email parece seguro, mas mantenha vigilância",
            "Verifique o remetente se solicitar ações importantes",
            "Em caso de dúvida, confirme por outro canal"
        ]
    },
    'MÉDIO': {
        'emoji': '⚠️',
        'titulo': 'Risco Médio',
        'cor': 'orange',
        'acoes': [
            "Cuidado! Alguns indicadores suspeitos detectados",
            "NÃO clique em links sem verificar o destino",
            "Confirme a autenticidade com o remetente por telefone",
            "Consulte o setor de TI antes de prosseguir"
        ]
    },
    'ALTO': {
        'emoji': '🚨',
        'titulo': 'Risco Alto - PHISHING DETECTADO',
        'cor': 'red',
        'acoes': [
            "⛔ NÃO clique em nenhum link ou anexo",
            "⛔ NÃO forneça informações pessoais ou financeiras",
            "⛔ NÃO responda ao email",
            "✅ Exclua o email imediatamente",
            "✅ Reporte ao setor de TI/Segurança",
            "✅ Informe colegas se receberem email similar"
        ]
    }
}

# ============================================
# INDICADORES DE PHISHING
# ============================================
INDICADORES_PHISHING = {
    'urgencia': {
        'nome': 'Senso de Urgência',
        'descricao': 'Uso de palavras como "urgente", "imediatamente", "agora"',
        'emoji': '⏰'
    },
    'urls': {
        'nome': 'Links Suspeitos',
        'descricao': 'Presença de URLs encurtadas ou domínios desconhecidos',
        'emoji': '🔗'
    },
    'financeiro': {
        'nome': 'Solicitação Financeira',
        'descricao': 'Menções a dinheiro, banco, pagamentos, prêmios',
        'emoji': '💰'
    },
    'maiusculas': {
        'nome': 'Excesso de Maiúsculas',
        'descricao': 'Uso excessivo de LETRAS MAIÚSCULAS',
        'emoji': '📢'
    },
    'especiais': {
        'nome': 'Caracteres Especiais',
        'descricao': 'Muitos caracteres especiais (!!! ??? $$$)',
        'emoji': '⚡'
    }
}

# ============================================
# CORES E ESTILOS
# ============================================
CORES = {
    'primaria': '#1f77b4',
    'secundaria': '#ff7f0e',
    'sucesso': '#2ecc71',
    'alerta': '#f39c12',
    'perigo': '#e74c3c',
    'fundo': '#f8f9fa',
    'texto': '#2c3e50'
}

# ============================================
# CSS CUSTOMIZADO
# ============================================
CUSTOM_CSS = """
<style>
    /* Estilo geral */
    .main {
        background-color: #f8f9fa;
    }

    /* Cabeçalho */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Cards de resultado */
    .resultado-seguro {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .resultado-phishing {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .resultado-medio {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Barra de confiança */
    .barra-confianca {
        background-color: #e9ecef;
        border-radius: 10px;
        height: 30px;
        overflow: hidden;
        margin: 1rem 0;
    }

    .barra-preenchimento {
        height: 100%;
        text-align: center;
        color: white;
        font-weight: bold;
        line-height: 30px;
        transition: width 0.5s ease;
    }

    /* Indicadores */
    .indicador {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 3px solid #667eea;
    }

    .indicador-titulo {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.3rem;
    }

    .indicador-descricao {
        color: #7f8c8d;
        font-size: 0.9rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #7f8c8d;
        font-size: 0.9rem;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }

    /* Botão customizado */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
        transition: transform 0.2s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Área de texto */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #dee2e6;
        font-family: 'Courier New', monospace;
    }

    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        font-weight: bold;
    }

    /* Métricas */
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }

    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
"""

# ============================================
# CONFIGURAÇÕES DE PÁGINA
# ============================================
PAGE_CONFIG = {
    'page_title': 'Detector de Phishing - Grings & Filhos',
    'page_icon': '🛡️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}