"""
Interface Streamlit para o Sistema de Detecção de Phishing
Grings & Filhos LTDA
"""

import os
import sys
import streamlit as st
from datetime import datetime
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# ⚡ CORREÇÃO: Adicionar o diretório raiz ao path
# Obtém o diretório do app (app/) e volta para a raiz (phishing-detector/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Agora pode importar normalmente
from src.modelo import DetectorPhishing
from src.utils import carregar_modelo

# Configuração da página
st.set_page_config(
    page_title="Detector de Phishing - Grings & Filhos",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .phishing-box {
        background-color: #ffe6e6;
        border-left: 5px solid #ff4444;
    }
    .safe-box {
        background-color: #e6f7e6;
        border-left: 5px solid #44ff44;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def carregar_modelo_cache():
    """Carrega o modelo uma única vez e mantém em cache."""
    caminho_modelo = os.path.join(BASE_DIR, 'modelo', 'detector_phishing.pkl')

    if not os.path.exists(caminho_modelo):
        st.error(f"❌ Modelo não encontrado em: {caminho_modelo}")
        st.info("💡 Execute 'python treinar_modelo.py' primeiro para treinar o modelo")
        st.stop()

    try:
        detector, metadata = carregar_modelo(caminho_modelo)
        return detector  # Retornar apenas o detector, não a tupla
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {e}")
        st.stop()

def exibir_resultado(resultado):
    """Exibe o resultado da análise de forma visual."""

    classificacao = resultado['classificacao']
    confianca = resultado['confianca']
    nivel_risco = resultado['nivel_risco']

    # Escolher estilo baseado na classificação
    if classificacao == "PHISHING":
        box_class = "phishing-box"
        emoji = "⚠️"
        cor = "#ff4444"
    else:
        box_class = "safe-box"
        emoji = "✅"
        cor = "#44ff44"

    # Box principal com resultado
    st.markdown(f"""
    <div class="result-box {box_class}">
        <h2 style="margin:0;">{emoji} {classificacao}</h2>
        <p style="font-size:1.2rem; margin:0.5rem 0;">
            <strong>Nível de Risco:</strong> {nivel_risco}
        </p>
        <p style="font-size:1.1rem; margin:0;">
            <strong>Confiança:</strong> {confianca * 100:.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Métricas adicionais
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Classificação",
            value=classificacao,
            delta="Atenção!" if classificacao == "PHISHING" else "Seguro"
        )

    with col2:
        st.metric(
            label="Confiança",
            value=f"{confianca * 100:.1f}%"
        )

    with col3:
        st.metric(
            label="Risco",
            value=nivel_risco
        )

    # Indicadores visuais de phishing
    if 'indicadores_phishing' in resultado and resultado['indicadores_phishing']:
        st.warning("🚨 **Indicadores de Phishing Detectados:**")
        for indicador in resultado['indicadores_phishing']:
            st.markdown(f"- {indicador}")


def salvar_analise(texto, resultado):
    """Salva uma análise no histórico."""
    try:
        from datetime import datetime
        import json

        # Criar registro da análise
        analise = {
            'timestamp': datetime.now().isoformat(),
            'texto': texto[:100] + '...' if len(texto) > 100 else texto,
            'classificacao': resultado['classificacao'],
            'confianca': resultado['confianca'],
            'nivel_risco': resultado['nivel_risco']
        }

        # Obter histórico atual
        try:
            historico_json = st.session_state.get('historico', '[]')
            historico = json.loads(historico_json) if isinstance(historico_json, str) else historico_json
        except:
            historico = []

        # Adicionar nova análise no início
        historico.insert(0, analise)

        # Manter apenas últimas 50 análises
        historico = historico[:50]

        # Salvar no session state
        st.session_state['historico'] = json.dumps(historico)

        return True
    except Exception as e:
        st.error(f"Erro ao salvar análise: {e}")
        return False


def obter_historico():
    """Obtém o histórico de análises."""
    try:
        import json
        historico_json = st.session_state.get('historico', '[]')
        return json.loads(historico_json) if isinstance(historico_json, str) else historico_json
    except:
        return []


def main():
    """Função principal da aplicação."""

    # Inicializar session state
    if 'historico' not in st.session_state:
        st.session_state['historico'] = '[]'

    # Cabeçalho
    st.markdown('<h1 class="main-header">🛡️ Sistema de Detecção de Phishing</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Grings & Filhos LTDA - Protegendo sua comunicação</p>', unsafe_allow_html=True)

    # Carregar modelo
    with st.spinner("🔄 Carregando modelo de IA..."):
        detector = carregar_modelo_cache()

    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Sobre o Sistema")
        st.info("""
        Este sistema utiliza **Machine Learning** para detectar emails de phishing.
        
        **Características:**
        - 🎯 Acurácia: ~94%
        - ⚡ Análise em tempo real
        - 🔍 Detecção de padrões suspeitos
        """)

        st.header("📊 Estatísticas do Modelo")
        if hasattr(detector, 'metricas') and detector.metricas:
            metricas = detector.metricas
            st.metric("Acurácia", f"{metricas.get('acuracia_teste', 0) * 100:.2f}%")
            st.metric("Precisão", f"{metricas.get('precisao', 0) * 100:.2f}%")
            st.metric("Recall", f"{metricas.get('recall', 0) * 100:.2f}%")

        st.header("🛠️ Como Usar")
        st.markdown("""
        1. Cole o texto do email suspeito
        2. Clique em **Analisar Email**
        3. Veja o resultado da análise
        """)

        # Histórico de análises
        st.header("📋 Histórico Recente")
        historico = obter_historico()

        if historico:
            # Mostrar estatísticas do histórico
            total = len(historico)
            phishing_count = sum(1 for h in historico if h['classificacao'] == 'PHISHING')
            legitimo_count = total - phishing_count

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", total)
            with col2:
                st.metric("Phishing", phishing_count)

            st.markdown("---")

            # Mostrar últimas 5 análises
            st.markdown("**Últimas análises:**")
            for i, analise in enumerate(historico[:5]):
                emoji = "🚨" if analise['classificacao'] == 'PHISHING' else "✅"
                confianca = analise['confianca'] * 100

                with st.expander(f"{emoji} {analise['texto'][:40]}...", expanded=False):
                    st.markdown(f"**Classificação:** {analise['classificacao']}")
                    st.markdown(f"**Confiança:** {confianca:.1f}%")
                    st.markdown(f"**Risco:** {analise['nivel_risco']}")
                    st.markdown(f"**Data:** {analise['timestamp'][:19]}")

            # Botão para limpar histórico
            if st.button("🗑️ Limpar Histórico", use_container_width=True):
                st.session_state['historico'] = '[]'
                st.rerun()
        else:
            st.info("Nenhuma análise realizada ainda.")

    # Área principal
    st.header("📧 Análise de Email")

    # Tabs para diferentes modos de entrada
    tab1, tab2 = st.tabs(["✍️ Inserir Texto", "📋 Exemplos"])

    with tab1:
        # Área de texto para input
        texto_email = st.text_area(
            "Cole o conteúdo do email aqui:",
            height=200,
            placeholder="Exemplo: URGENT! Your account will be suspended. Click here to verify..."
        )

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            analisar = st.button("🔍 Analisar Email", type="primary", use_container_width=True)

        with col2:
            limpar = st.button("🗑️ Limpar", use_container_width=True)

        if limpar:
            st.rerun()

        if analisar:
            if not texto_email.strip():
                st.warning("⚠️ Por favor, insira o texto do email para análise.")
            else:
                with st.spinner("🔄 Analisando email..."):
                    try:
                        resultado = detector.analisar_email(texto_email)
                        exibir_resultado(resultado)

                        # Salvar no histórico
                        salvar_analise(texto_email, resultado)

                        # Mostrar explicação
                        with st.expander("🔍 Ver Detalhes da Análise"):
                            st.json(resultado)

                    except Exception as e:
                        st.error(f"❌ Erro ao analisar email: {e}")

    with tab2:
        st.subheader("Exemplos de Emails para Teste")

        exemplos = [
            {
                "nome": "🚨 Phishing - Conta Suspensa",
                "texto": "URGENT! Your account will be SUSPENDED immediately! Click here to verify: http://fakephishing.com/verify"
            },
            {
                "nome": "🚨 Phishing - Prêmio Falso",
                "texto": "Congratulations! You have won $1,000,000! Send your bank details to claim your prize NOW!"
            },
            {
                "nome": "✅ Legítimo - Reunião",
                "texto": "Hi team, just a reminder that our weekly meeting is scheduled for Tuesday at 2 PM. Please review the attached agenda."
            },
            {
                "nome": "✅ Legítimo - Relatório",
                "texto": "Dear colleagues, please find attached the quarterly financial report. Let me know if you have any questions."
            }
        ]

        for exemplo in exemplos:
            with st.expander(exemplo["nome"]):
                st.text_area(
                    "Texto do email:",
                    value=exemplo["texto"],
                    height=100,
                    key=f"exemplo_{exemplo['nome']}",
                    disabled=True
                )

                if st.button(f"Analisar este exemplo", key=f"btn_{exemplo['nome']}"):
                    with st.spinner("🔄 Analisando..."):
                        resultado = detector.analisar_email(exemplo["texto"])
                        exibir_resultado(resultado)

                        # Salvar no histórico
                        salvar_analise(exemplo["texto"], resultado)

    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🛡️ <strong>Grings & Filhos LTDA</strong> - Sistema de Detecção de Phishing v1.0</p>
        <p><em>Última atualização: {}</em></p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()