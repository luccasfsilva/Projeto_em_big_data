# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
from googletrans import Translator # Import da biblioteca de tradução
warnings.filterwarnings('ignore')

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="CineAnalytics Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILOS CSS PERSONALIZADOS
# =========================
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA726);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #8f8f8f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FFA726;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .metric-card-danger {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF6B6B;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .section-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #34495e;
    }
    .insight-box {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #FFA726;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .prediction-box {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4ECDC4;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CARREGAR E PREPROCESSAR DADOS
# =========================
@st.cache_data
def carregar_dados():
    # URL do CSV do GitHub (utilizada no projeto original)
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        
        # Limpeza e transformação mais robusta
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        
        # Extrair ano e mês
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(0).astype(int)
        
        # Calcular ROI (Return on Investment)
        df["roi"] = np.where(
            df["budget_x"] > 0,
            (df["revenue"] - df["budget_x"]) / df["budget_x"] * 100,
            0
        )
        
        # Categorizar sucesso
        conditions = [
            df['revenue'] >= df['revenue'].quantile(0.8),
            df['revenue'] >= df['revenue'].quantile(0.6),
            df['revenue'] >= df['revenue'].quantile(0.4),
            df['revenue'] < df['revenue'].quantile(0.4)
        ]
        choices = ['Blockbuster', 'High', 'Medium', 'Low']
        df['success_category'] = np.select(conditions, choices, default='Low')
        
        # Popularidade normalizada
        if 'vote_count' in df.columns:
            df['popularity_norm'] = (df['vote_count'] - df['vote_count'].min()) / (df['vote_count'].max() - df['vote_count'].min())
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar o CSV.\nDetalhe: {e}")
        st.stop()

df = carregar_dados()
if df is None:
    st.stop()

# =========================
# DICIONÁRIO DE TRADUÇÃO DOS FILMES
# =========================
# (O dicionário de TRADUCOES_FILMES não foi incluído aqui por ser muito extenso, 
# mas deve ser mantido exatamente como estava na sua versão original.)
TRADUCOES_FILMES = {
    # Filmes Populares
    "Avatar: The Way of Water": "Avatar: O Caminho da Água",
    "Avengers: Endgame": "Vingadores: Ultimato",
    # ... (Mantenha o restante do seu dicionário)
}

def traduzir_nome_filme(nome_original):
    """Traduz o nome do filme para português"""
    if pd.isna(nome_original):
        return nome_original
    return TRADUCOES_FILMES.get(nome_original, nome_original)

# =========================
# FUNÇÕES DE ANÁLISE AVANÇADA (SEM scikit-learn)
# =========================
def calcular_tendencia_simples(df, coluna):
    """Calcula tendência simples usando método estatístico básico"""
    anual = df.groupby('ano')[coluna].mean().reset_index()
    if len(anual) > 1:
        # Método simples: compara primeiro e último ano
        primeiro_valor = anual[coluna].iloc[0]
        ultimo_valor = anual[coluna].iloc[-1]
        periodo = anual['ano'].iloc[-1] - anual['ano'].iloc[0]
        
        if periodo > 0 and primeiro_valor != 0:
            crescimento_percentual = ((ultimo_valor - primeiro_valor) / primeiro_valor) * 100
            return crescimento_percentual / periodo  # Crescimento médio anual percentual
    return 0

def calcular_correlacao_personalizada(df, col1, col2):
    """Calcula correlação simples entre duas colunas"""
    valid_data = df[[col1, col2]].dropna()
    if len(valid_data) > 1:
        return valid_data[col1].corr(valid_data[col2])
    return 0

# =========================
# BARRA LATERAL AVANÇADA
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4ECDC4;'>🎛️ Painel de Controle Avançado</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtro de anos
    st.markdown("#### 📅 Filtro por Ano")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis)),
        help="Filtre os filmes por ano de lançamento"
    )
    
    st.markdown("---")
    
    # Filtros múltiplos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Filtro por Nota")
        score_min, score_max = st.slider(
            "Nota IMDb:",
            min_value=0.0,
            max_value=10.0,
            value=(0.0, 10.0),
            step=0.1,
            help="Filtre os filmes pela nota no IMDb"
        )
    
    with col2:
        st.markdown("#### 💰 Filtro por ROI")
        roi_min, roi_max = st.slider(
            "ROI (%):",
            min_value=-100.0,
            max_value=1000.0,
            value=(-100.0, 1000.0),
            step=50.0,
            help="Retorno sobre Investimento"
        )
    
    st.markdown("---")
    
    # Filtro por categoria de sucesso
    st.markdown("#### 🏆 Categoria de Sucesso")
    categorias = st.multiselect(
        "Selecione as categorias:",
        options=['Blockbuster', 'High', 'Medium', 'Low'],
        default=['Blockbuster', 'High', 'Medium', 'Low'],
        help="Filtre pela categoria de sucesso financeiro"
    )
    
    st.markdown("---")
    
    # Análise rápida
    with st.expander("🔍 Análise Rápida"):
        if st.button("Calcular Insights Automáticos"):
            # A lógica para o estado deve ser implementada aqui, se necessário.
            st.session_state.calcular_insights = True

# Aplicar filtro principal
df_filtrado = df[
    (df["ano"] >= ano_min) &
    (df["ano"] <= ano_max) &
    (df["score"] >= score_min) &
    (df["score"] <= score_max) &
    (df["roi"] >= roi_min) &
    (df["roi"] <= roi_max) &
    (df['success_category'].isin(categorias))
]

# Aplicar tradução aos nomes dos filmes
df_filtrado = df_filtrado.copy()
df_filtrado["names"] = df_filtrado["names"].apply(traduzir_nome_filme)

# =========================
# CABEÇALHO E MÉTRICAS PRINCIPAIS
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Avançado de Análise Cinematográfica</p>', unsafe_allow_html=True)

# Métricas principais expandidas
if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
    roi_medio = df_filtrado["roi"].mean()
    orcamento_medio = df_filtrado["budget_x"].mean()
    
    # Análises avançadas
    tendencia_receita = calcular_tendencia_simples(df_filtrado, 'revenue')
    tendencia_nota = calcular_tendencia_simples(df_filtrado, 'score')
    blockbusters = df_filtrado[df_filtrado['success_category'] == 'Blockbuster'].shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = roi_medio = orcamento_medio = 0
    tendencia_receita = tendencia_nota = blockbusters = 0

# Primeira linha de métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}", 
              f"{tendencia_receita:+.1f}%/ano" if tendencia_receita != 0 else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Receita Média", f"${receita_media:,.0f}", 
              help="Receita média por filme")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⭐ Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—",
              f"{tendencia_nota:+.2f}/ano" if tendencia_nota != 0 else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎭 Total de Filmes", f"{total_filmes:,}", 
              help="Número total de filmes que correspondem aos filtros")
    st.markdown('</div>', unsafe_allow_html=True)

# Segunda linha de métricas avançadas
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("📈 ROI Médio", f"{roi_medio:.1f}%", 
              help="Retorno sobre Investimento médio")
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💸 Orçamento Médio", f"${orcamento_medio:,.0f}" if orcamento_medio > 0 else "N/A",
              help="Orçamento médio dos filmes")
    st.markdown('</div>', unsafe_allow_html=True)

with col7:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("🏆 Blockbusters", f"{blockbusters:,}",
              help="Filmes na categoria Blockbuster")
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    st.markdown('<div class="metric-card-danger">', unsafe_allow_html=True)
    eficiencia = receita_total / max(orcamento_medio * total_filmes, 1)
    st.metric("⚡ Eficiência", f"{eficiencia:.2f}x",
              help="Relação Receita/Orçamento")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# SISTEMA DE ABAS AVANÇADO
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard Principal", 
    "🎭 Análise de Performance", 
    "📈 Tendências & Análises",
    "🔍 Insights Avançados",
    "🏆 Benchmarking",
    "📋 Base de Dados"
])

# ... (O código para as abas Tab1 a Tab6 deve seguir aqui, exatamente como na versão corrigida anterior)
# ... (O código foi omitido para brevidade, mas você deve usar a versão completa da etapa anterior)

if not df_filtrado.empty:
    with tab1:
        # Conteúdo da Tab1 (Dashboard Principal)
        # ...
    with tab2:
        # Conteúdo da Tab2 (Análise de Performance)
        # ...
    with tab3:
        # Conteúdo da Tab3 (Tendências & Análises)
        # ...
    with tab4:
        # Conteúdo da Tab4 (Insights Avançados)
        # ...
    with tab5:
        # Conteúdo da Tab5 (Benchmarking)
        # ...
    with tab6:
        # Conteúdo da Tab6 (Base de Dados)
        st.markdown('<div class="section-header">📋 Base de Dados Completa</div>', unsafe_allow_html=True)
        st.dataframe(df_filtrado.style.format({
            "revenue": "${:,.0f}",
            "budget_x": "${:,.0f}",
            "score": "{:.2f}",
            "roi": "{:.1f}%"
        }), use_container_width=True)
else:
    st.warning("O DataFrame está vazio. Por favor, ajuste os filtros.")
