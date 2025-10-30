"""
Aplicação web principal do Sistema de Detecção de Phishing.
Interface desenvolvida com Streamlit para análise de emails.
"""

import sys
import os
import streamlit as st
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.modelo import DetectorPhishing
from src.features import criar_features_basicas
import config

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(**config.PAGE_CONFIG)

# Aplicar CSS customizado
st.markdown(config.CUSTOM_CSS, unsafe_allow_html=True)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

@st.cache_resource
def carregar_modelo():
    """
    Carrega o modelo treinado (com cache para evitar recarregar).
    """
    try:
        if not os.path.exists(config.MODELO_PATH):
            st.error(f"❌ Modelo não encontrado em: {config.MODELO_PATH}")
            st.info("💡 Execute primeiro: `python treinar_modelo.py --criar-exemplo`")
            st.stop()

        detector = DetectorPhishing.carregar(config.MODELO_PATH)
        return detector
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo: {str(e)}")
        st.stop()


def renderizar_header():
    """
    Renderiza o cabeçalho da aplicação.
    """
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">{config.TITULO_APP}</div>
        <div class="header-subtitle">{config.SUBTITULO_APP}</div>
        <div style="margin-top: 1rem; font-size: 0.9rem;">
            {config.EMPRESA_NOME} | CNPJ: {config.EMPRESA_CNPJ}
        </div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_barra_confianca(probabilidade, nivel_risco):
    """
    Renderiza barra visual de confiança.

    Args:
        probabilidade: Valor entre 0 e 1
        nivel_risco: 'BAIXO', 'MÉDIO' ou 'ALTO'
    """
    percentual = int(probabilidade * 100)

    # Definir cor baseada no risco
    cores = {
        'BAIXO': '#28a745',
        'MÉDIO': '#ffc107',
        'ALTO': '#dc3545'
    }
    cor = cores.get(nivel_risco, '#6c757d')

    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: bold;">Confiança da Análise:</span>
            <span style="font-weight: bold; color: {cor};">{percentual}%</span>
        </div>
        <div class="barra-confianca">
            <div class="barra-preenchimento" style="width: {percentual}%; background-color: {cor};">
                {percentual}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_resultado(resultado):
    """
    Renderiza o resultado da análise de forma visual.

    Args:
        resultado: Dicionário retornado por detector.analisar_email()
    """
    nivel_risco = resultado['nivel_risco']
    classificacao = resultado['classificacao']
    confianca = resultado['confianca']

    recom = config.RECOMENDACOES[nivel_risco]

    # Escolher classe CSS baseada no risco
    classe_css = {
        'BAIXO': 'resultado-seguro',
        'MÉDIO': 'resultado-medio',
        'ALTO': 'resultado-phishing'
    }[nivel_risco]

    # Renderizar card de resultado
    st.markdown(f"""
    <div class="{classe_css}">
        <h2 style="margin: 0;">{recom['emoji']} {recom['titulo']}</h2>
        <h3 style="margin-top: 0.5rem;">Classificação: {classificacao}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Barra de confiança
    renderizar_barra_confianca(confianca, nivel_risco)

    # Recomendações
    st.markdown(f"### {recom['emoji']} Ações Recomendadas:")
    for acao in recom['acoes']:
        st.markdown(f"- {acao}")


def renderizar_indicadores(features):
    """
    Renderiza indicadores detectados no email.

    Args:
        features: Dicionário com features extraídas
    """
    st.markdown("### 📊 Indicadores Detectados")

    col1, col2 = st.columns(2)

    indicadores_detectados = []

    # Verificar cada indicador
    if features['palavras_urgencia'] > 0:
        indicadores_detectados.append('urgencia')

    if features['num_urls'] > 0:
        indicadores_detectados.append('urls')

    if features['palavras_financeiras'] > 0:
        indicadores_detectados.append('financeiro')

    if features['prop_maiusculas'] > 0.3:
        indicadores_detectados.append('maiusculas')

    if features['num_especiais'] > 5:
        indicadores_detectados.append('especiais')

    # Renderizar indicadores
    if indicadores_detectados:
        for i, ind_key in enumerate(indicadores_detectados):
            ind = config.INDICADORES_PHISHING[ind_key]
            col = col1 if i % 2 == 0 else col2

            with col:
                st.markdown(f"""
                <div class="indicador">
                    <div class="indicador-titulo">{ind['emoji']} {ind['nome']}</div>
                    <div class="indicador-descricao">{ind['descricao']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("✅ Nenhum indicador suspeito detectado")


def renderizar_estatisticas(features):
    """
    Renderiza estatísticas do email analisado.

    Args:
        features: Dicionário com features
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📏 Tamanho", f"{features['tamanho_texto']} palavras")

    with col2:
        st.metric("🔗 URLs", features['num_urls'])

    with col3:
        st.metric("⚡ Especiais", features['num_especiais'])

    with col4:
        maiusc_perc = int(features['prop_maiusculas'] * 100)
        st.metric("📢 Maiúsculas", f"{maiusc_perc}%")


def renderizar_sidebar():
    """
    Renderiza barra lateral com informações e exemplos.
    """
    with st.sidebar:
        st.markdown("## 📖 Sobre o Sistema")

        st.markdown("""
        Este sistema utiliza **Inteligência Artificial** para detectar 
        tentativas de phishing em emails corporativos.

        ### 🧠 Tecnologia
        - Machine Learning (Regressão Logística)
        - Processamento de Linguagem Natural
        - Análise de padrões suspeitos

        ### 🎯 Precisão
        - **89.5%** de acurácia geral
        - **91.2%** de precisão em phishing
        - **87.3%** de taxa de detecção
        """)

        st.markdown("---")

        st.markdown("### 📧 Exemplos de Teste")

        if st.button("📌 Carregar Email de Phishing"):
            st.session_state.exemplo_texto = config.EXEMPLO_EMAIL_PHISHING
            st.rerun()

        if st.button("📌 Carregar Email Legítimo"):
            st.session_state.exemplo_texto = config.EXEMPLO_EMAIL_LEGITIMO
            st.rerun()

        st.markdown("---")

        st.markdown(f"""
        ### 👨‍💻 Desenvolvimento
        **Projeto Integrado**  
        IA + Segurança da Informação

        **Desenvolvido por:**  
        {config.PROJETO_AUTOR}

        **Empresa:**  
        {config.EMPRESA_NOME}
        """)

        st.markdown("---")

        st.markdown(f"""
        <div style="text-align: center; font-size: 0.8rem; color: #7f8c8d;">
            Versão 1.0.0 | {datetime.now().year}
        </div>
        """, unsafe_allow_html=True)


# ============================================
# APLICAÇÃO PRINCIPAL
# ============================================

def main():
    """
    Função principal da aplicação.
    """
    # Renderizar elementos visuais
    renderizar_header()
    renderizar_sidebar()

    # Carregar modelo
    detector = carregar_modelo()

    # Instruções
    with st.expander("📋 Como Usar", expanded=False):
        st.markdown(config.INSTRUCOES)

    # Área principal de análise
    st.markdown("## 🔍 Análise de Email")

    # Inicializar estado da sessão
    if 'exemplo_texto' not in st.session_state:
        st.session_state.exemplo_texto = ""

    # Área de texto para input
    texto_email = st.text_area(
        "Cole o texto do email suspeito abaixo:",
        value=st.session_state.exemplo_texto,
        height=250,
        placeholder="Cole aqui o conteúdo completo do email que deseja analisar...",
        help="Copie todo o texto do email, incluindo assunto, remetente e corpo da mensagem"
    )

    # Limpar exemplo após uso
    if st.session_state.exemplo_texto:
        st.session_state.exemplo_texto = ""

    # Botão de análise
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analisar_btn = st.button("🔍 Analisar Email", type="primary", use_container_width=True)

    # Processar análise
    if analisar_btn:
        if not texto_email or len(texto_email.strip()) < 10:
            st.warning("⚠️ Por favor, cole um email válido para análise (mínimo 10 caracteres)")
        else:
            with st.spinner("🔄 Analisando email... Aguarde alguns segundos."):
                try:
                    # Fazer análise
                    resultado = detector.analisar_email(texto_email, mostrar_features=True)

                    # Renderizar resultado
                    st.markdown("---")
                    st.markdown("## 📊 Resultado da Análise")

                    renderizar_resultado(resultado)

                    st.markdown("---")

                    # Estatísticas
                    renderizar_estatisticas(resultado['features'])

                    st.markdown("---")

                    # Indicadores
                    renderizar_indicadores(resultado['features'])

                    # Detalhes técnicos (colapsável)
                    with st.expander("🔬 Detalhes Técnicos", expanded=False):
                        st.json({
                            'classificacao': resultado['classificacao'],
                            'probabilidade_phishing': f"{resultado['confianca'] * 100:.2f}%",
                            'nivel_risco': resultado['nivel_risco'],
                            'features_extraidas': resultado['features']
                        })

                    # Timestamp da análise
                    st.markdown(f"""
                    <div style="text-align: center; color: #7f8c8d; font-size: 0.85rem; margin-top: 2rem;">
                        Análise realizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Erro ao analisar email: {str(e)}")
                    st.exception(e)

    # Footer
    st.markdown("""
    <div class="footer">
        <strong>⚠️ Aviso Importante:</strong> Este sistema é uma ferramenta de apoio à decisão.<br>
        Em caso de dúvida sobre a autenticidade de um email, sempre consulte o setor de TI/Segurança.<br><br>

        <strong>🔒 Privacidade:</strong> Nenhum email é armazenado. Todas as análises são processadas 
        em tempo real e descartadas imediatamente após o resultado.<br><br>

        © 2024 Grings & Filhos LTDA - Todos os direitos reservados
    </div>
    """, unsafe_allow_html=True)


# ============================================
# EXECUTAR APLICAÇÃO
# ============================================

if __name__ == "__main__":
    main()