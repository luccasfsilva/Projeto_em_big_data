# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
from plotly.subplots import make_subplots
import time

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
# ESTILOS CSS PERSONALIZADOS MODERNOS
# =========================
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .section-header {
        font-size: 1.5rem;
        color: #667eea;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
        font-weight: 600;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
    }
    .prediction-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SISTEMA DE CACHE AVANÇADO
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dados_avancado():
    """
    Carrega e processa dados com sistema de cache inteligente
    """
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    
    # Simular barra de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("📥 Baixando dados...")
        progress_bar.progress(20)
        
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        progress_bar.progress(40)
        
        status_text.text("🔧 Processando dados...")
        # Limpeza avançada
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce").fillna(0)
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        
        progress_bar.progress(60)
        
        # Engenharia de features avançada
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(0).astype(int)
        df["decada"] = (df["ano"] // 10) * 10
        
        # Métricas financeiras avançadas
        df["roi"] = np.where(
            df["budget_x"] > 0,
            (df["revenue"] - df["budget_x"]) / df["budget_x"] * 100,
            0
        )
        
        df["lucro"] = df["revenue"] - df["budget_x"]
        df["margem_lucro"] = np.where(
            df["revenue"] > 0,
            (df["lucro"] / df["revenue"]) * 100,
            0
        )
        
        progress_bar.progress(80)
        
        # Sistema de categorização inteligente
        conditions = [
            (df['revenue'] >= df['revenue'].quantile(0.9)),
            (df['revenue'] >= df['revenue'].quantile(0.7)),
            (df['revenue'] >= df['revenue'].quantile(0.5)),
            (df['revenue'] >= df['revenue'].quantile(0.3)),
            (df['revenue'] < df['revenue'].quantile(0.3))
        ]
        choices = ['Super Blockbuster', 'Blockbuster', 'High', 'Medium', 'Low']
        df['success_category'] = np.select(conditions, choices, default='Low')
        
        # Score normalizado para comparação
        if 'vote_count' in df.columns:
            df['popularity_norm'] = (df['vote_count'] - df['vote_count'].min()) / \
                                   (df['vote_count'].max() - df['vote_count'].min())
        
        # Feature: Estação do ano baseada no mês
        seasons_map = {12: 'Verão', 1: 'Verão', 2: 'Verão', 
                      3: 'Outono', 4: 'Outono', 5: 'Outono',
                      6: 'Inverno', 7: 'Inverno', 8: 'Inverno', 
                      9: 'Primavera', 10: 'Primavera', 11: 'Primavera'}
        df['estacao'] = df['mes'].map(seasons_map)
        
        progress_bar.progress(100)
        status_text.text("✅ Dados carregados com sucesso!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        
        return df
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Erro crítico ao carregar dados: {str(e)}")
        return None

# =========================
# SISTEMA DE TRADUÇÃO DINÂMICA AVANÇADO
# =========================
class SistemaTraducao:
    def __init__(self):
        self.cache_traducoes = {}
        self.dicionario_estatico = self._carregar_dicionario_estatico()
    
    def _carregar_dicionario_estatico(self):
        """Dicionário expandido com mais filmes"""
        return {
            # Filmes Populares
            "Avatar: The Way of Water": "Avatar: O Caminho da Água",
            "Avengers: Endgame": "Vingadores: Ultimato",
            "Avatar": "Avatar",
            "Titanic": "Titanic",
            "Star Wars: Episode VII - The Force Awakens": "Star Wars: Episódio VII - O Despertar da Força",
            "Avengers: Infinity War": "Vingadores: Guerra Infinita",
            "Spider-Man: No Way Home": "Homem-Aranha: Sem Volta para Casa",
            "Jurassic World": "Mundo Jurássico",
            "The Lion King": "O Rei Leão",
            "The Avengers": "Os Vingadores",
            "Furious 7": "Velozes e Furiosos 7",
            "Frozen II": "Frozen II",
            "Top Gun: Maverick": "Top Gun: Maverick",
            "Barbie": "Barbie",
            "The Super Mario Bros. Movie": "Super Mario Bros.: O Filme",
            "Avengers: Age of Ultron": "Vingadores: Era de Ultron",
            "Black Panther": "Pantera Negra",
            "Harry Potter and the Deathly Hallows: Part 2": "Harry Potter e as Relíquias da Morte: Parte 2",
            "Star Wars: Episode VIII - The Last Jedi": "Star Wars: Episódio VIII - Os Últimos Jedi",
            "Jurassic World: Fallen Kingdom": "Mundo Jurássico: Reino Ameaçado",
            "Frozen": "Frozen: Uma Aventura Congelante",
            "Beauty and the Beast": "A Bela e a Fera",
            "Incredibles 2": "Os Incríveis 2",
            "The Fate of the Furious": "O Destino de Velozes e Furiosos",
            "Iron Man 3": "Homem de Ferro 3",
            "Minions": "Minions",
            "Captain America: Civil War": "Capitão América: Guerra Civil",
            "Aquaman": "Aquaman",
            "The Lord of the Rings: The Return of the King": "O Senhor dos Anéis: O Retorno do Rei",
            "Spider-Man: Far From Home": "Homem-Aranha: Longe de Casa",
            # Filmes Recentes
            "Oppenheimer": "Oppenheimer",
            "Guardians of the Galaxy Vol. 3": "Guardiões da Galáxia Vol. 3",
            "Fast X": "Velozes e Furiosos 10",
            "The Little Mermaid": "A Pequena Sereia",
            "Elemental": "Elementos",
            "Ant-Man and the Wasp: Quantumania": "Homem-Formiga e a Vespa: Quantumania",
            "John Wick: Chapter 4": "John Wick 4: Baba Yaga",
            "The Flash": "The Flash",
            "Transformers: Rise of the Beasts": "Transformers: O Despertar das Feras",
            "Spider-Man: Across the Spider-Verse": "Homem-Aranha: Através do Aranhaverso",
            "Indiana Jones and the Dial of Destiny": "Indiana Jones e o Chamado do Destino",
            "Mission: Impossible - Dead Reckoning Part One": "Missão: Impossível - Acerto de Contas Parte Um",
            "The Marvels": "As Marvels",
            "Wonka": "Wonka",
            "Aquaman and the Lost Kingdom": "Aquaman e o Reino Perdido",
            "The Hunger Games: The Ballad of Songbirds & Snakes": "Jogos Vorazes: A Cantiga dos Pássaros e das Serpentes",
            # Filmes Brasileiros
            "Cidade de Deus": "Cidade de Deus",
            "Tropa de Elite": "Tropa de Elite",
            "Central do Brasil": "Central do Brasil",
            "O Auto da Compadecida": "O Auto da Compadecida",
            "Lisbela e o Prisioneiro": "Lisbela e o Prisioneiro",
        }
    
    @st.cache_data(show_spinner=False)
    def traduzir_dinamica(_self, texto):
        """Sistema de tradução dinâmica com fallback inteligente"""
        if not texto or pd.isna(texto):
            return texto
        
        # Verificar cache
        if texto in _self.cache_traducoes:
            return _self.cache_traducoes[texto]
        
        # Verificar dicionário estático
        if texto in _self.dicionario_estatico:
            traducao = _self.dicionario_estatico[texto]
            _self.cache_traducoes[texto] = traducao
            return traducao
        
        # Fallback: manter original (em produção, integrar com API de tradução)
        _self.cache_traducoes[texto] = texto
        return texto

# Inicializar sistema de tradução
sistema_traducao = SistemaTraducao()

# =========================
# CARREGAR DADOS
# =========================
df = carregar_dados_avancado()
if df is None:
    st.stop()

# Aplicar tradução aos nomes dos filmes
df["names"] = df["names"].apply(sistema_traducao.traduzir_dinamica)

# =========================
# SISTEMA DE ANÁLISE PREDITIVA SIMPLES
# =========================
class AnalisadorPreditivo:
    def __init__(self, df):
        self.df = df
    
    def prever_performance(self, orcamento, nota_esperada, genero=None, mes=None):
        """Sistema de previsão de performance baseado em dados históricos"""
        
        # Filtrar filmes similares
        similar_movies = self.df[
            (self.df['budget_x'].between(orcamento * 0.3, orcamento * 2)) &
            (self.df['score'].between(nota_esperada - 1, nota_esperada + 1))
        ]
        
        if similar_movies.empty:
            similar_movies = self.df  # Fallback para todos os filmes
        
        # Calcular métricas de referência
        receita_media = similar_movies['revenue'].mean()
        roi_medio = similar_movies['roi'].mean()
        sucesso_rate = len(similar_movies[similar_movies['revenue'] > similar_movies['budget_x']]) / len(similar_movies)
        
        # Ajustar baseado na nota esperada
        ajuste_nota = (nota_esperada - similar_movies['score'].mean()) * 0.15
        
        # Previsão ajustada
        receita_prevista = receita_media * (1 + ajuste_nota)
        roi_previsto = (receita_prevista - orcamento) / orcamento * 100
        
        # Categoria de risco
        if roi_previsto > 200:
            risco = "Muito Baixo"
            cor_risco = "🟢"
        elif roi_previsto > 50:
            risco = "Baixo"
            cor_risco = "🟡"
        elif roi_previsto > 0:
            risco = "Moderado"
            cor_risco = "🟠"
        else:
            risco = "Alto"
            cor_risco = "🔴"
        
        return {
            'receita_prevista': receita_prevista,
            'roi_previsto': roi_previsto,
            'probabilidade_sucesso': sucesso_rate * 100,
            'categoria_risco': risco,
            'cor_risco': cor_risco,
            'filmes_similares_analisados': len(similar_movies)
        }

# =========================
# BARRA LATERAL MODERNA
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎛️ Painel de Controle</h2>", unsafe_allow_html=True)
    
    # Filtro de anos com visual moderno
    st.markdown("### 📅 Período")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )
    
    st.markdown("---")
    
    # Filtros em abas
    tab_filtros1, tab_filtros2 = st.tabs(["📊 Métricas", "🎯 Performance"])
    
    with tab_filtros1:
        score_min, score_max = st.slider(
            "⭐ Nota IMDb:",
            0.0, 10.0, (0.0, 10.0), 0.1
        )
        
        orcamento_min, orcamento_max = st.slider(
            "💰 Orçamento (USD):",
            float(df['budget_x'].min()), 
            float(df['budget_x'].max()),
            (float(df['budget_x'].quantile(0.1)), float(df['budget_x'].quantile(0.9)))
        )
    
    with tab_filtros2:
        roi_min, roi_max = st.slider(
            "📈 ROI (%):",
            -100.0, 1000.0, (-100.0, 1000.0), 50.0
        )
        
        categorias = st.multiselect(
            "🏆 Categorias:",
            options=['Super Blockbuster', 'Blockbuster', 'High', 'Medium', 'Low'],
            default=['Super Blockbuster', 'Blockbuster', 'High']
        )
    
    st.markdown("---")
    
    # Configurações avançadas
    with st.expander("⚙️ Configurações Avançadas"):
        st.checkbox("Atualização automática", value=True)
        st.checkbox("Modo escuro", value=True)
        st.slider("Qualidade dos gráficos", 1, 3, 2)

# Aplicar filtros
df_filtrado = df[
    (df["ano"] >= ano_min) & (df["ano"] <= ano_max) &
    (df["score"] >= score_min) & (df["score"] <= score_max) &
    (df["budget_x"] >= orcamento_min) & (df["budget_x"] <= orcamento_max) &
    (df["roi"] >= roi_min) & (df["roi"] <= roi_max) &
    (df['success_category'].isin(categorias))
]

# =========================
# CABEÇALHO PRINCIPAL
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Inteligente de Análise Cinematográfica com IA</p>', unsafe_allow_html=True)

# =========================
# MÉTRICAS PRINCIPAIS DINÂMICAS
# =========================
if not df_filtrado.empty:
    # Cálculo de métricas
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean()
    total_filmes = df_filtrado.shape[0]
    roi_medio = df_filtrado["roi"].mean()
    blockbusters = df_filtrado[df_filtrado['success_category'].isin(['Super Blockbuster', 'Blockbuster'])].shape[0]
    
    # Análise de tendência
    crescimento_receita = ((df_filtrado[df_filtrado['ano'] == ano_max]['revenue'].mean() / 
                          df_filtrado[df_filtrado['ano'] == ano_min]['revenue'].mean()) - 1) * 100
else:
    receita_total = receita_media = nota_media = total_filmes = roi_medio = blockbusters = crescimento_receita = 0

# Grid de métricas responsivo
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}", 
              f"{crescimento_receita:+.1f}%" if not np.isnan(crescimento_receita) else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card-success">', unsafe_allow_html=True)
    st.metric("📈 ROI Médio", f"{roi_medio:.1f}%", 
              f"{blockbusters} blockbusters")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("⭐ Nota Média", f"{nota_media:.2f}", 
              f"{total_filmes} filmes")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎭 Eficiência", 
              f"{(receita_media/df_filtrado['budget_x'].mean()):.1f}x" if df_filtrado['budget_x'].mean() > 0 else "N/A",
              "Receita/Orçamento")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# SISTEMA DE ABAS AVANÇADO
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard", "📈 Analytics", "🎯 Simulador", 
    "🔍 Insights", "🏆 Benchmark", "📋 Dados", "🤖 IA"
])

with tab1:
    st.markdown('<div class="section-header">📊 Visão Geral do Mercado</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de dispersão 3D interativo
        fig_3d = px.scatter_3d(
            df_filtrado.head(100),  # Limitar para performance
            x='budget_x',
            y='score', 
            z='revenue',
            color='success_category',
            size='roi',
            hover_name='names',
            title='🌐 Análise 3D: Orçamento vs Nota vs Receita',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_3d, use_container_width=True)
    
    with col2:
        # KPIs rápidos
        st.markdown("#### 📋 KPIs Rápidos")
        
        st.metric("🎯 Maior ROI", 
                 f"{df_filtrado['roi'].max():.0f}%" if not df_filtrado.empty else "N/A")
        st.metric("💸 Maior Receita", 
                 f"${df_filtrado['revenue'].max():,.0f}" if not df_filtrado.empty else "N/A")
        st.metric("⭐ Melhor Nota", 
                 f"{df_filtrado['score'].max():.1f}" if not df_filtrado.empty else "N/A")
        st.metric("📅 Período", 
                 f"{ano_min} - {ano_max}")

with tab2:
    st.markdown('<div class="section-header">📈 Analytics Avançado</div>', unsafe_allow_html=True)
    
    # Análise temporal múltipla
    if not df_filtrado.empty:
        evolucao_anual = df_filtrado.groupby('ano').agg({
            'revenue': ['mean', 'sum'],
            'score': 'mean',
            'roi': 'mean',
            'names': 'count'
        }).round(2)
        evolucao_anual.columns = ['Receita Média', 'Receita Total', 'Nota Média', 'ROI Médio', 'Nº Filmes']
        evolucao_anual = evolucao_anual.reset_index()
        
        fig_evolucao = make_subplots(
            rows=2, cols=2,
            subplot_titles=('📈 Receita Total Anual', '⭐ Nota Média', '📊 ROI Médio', '🎭 Número de Filmes'),
            vertical_spacing=0.1
        )
        
        fig_evolucao.add_trace(
            go.Scatter(x=evolucao_anual['ano'], y=evolucao_anual['Receita Total'], 
                      name='Receita Total', line=dict(color='#667eea')),
            row=1, col=1
        )
        
        fig_evolucao.add_trace(
            go.Scatter(x=evolucao_anual['ano'], y=evolucao_anual['Nota Média'],
                      name='Nota Média', line=dict(color='#f093fb')),
            row=1, col=2
        )
        
        fig_evolucao.add_trace(
            go.Scatter(x=evolucao_anual['ano'], y=evolucao_anual['ROI Médio'],
                      name='ROI Médio', line=dict(color='#4facfe')),
            row=2, col=1
        )
        
        fig_evolucao.add_trace(
            go.Bar(x=evolucao_anual['ano'], y=evolucao_anual['Nº Filmes'],
                  name='Nº Filmes', marker_color='#00f2fe'),
            row=2, col=2
        )
        
        fig_evolucao.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_evolucao, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">🎯 Simulador de Investimento</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 🎬 Configurar Projeto")
        
        with st.form("simulador_investimento"):
            orcamento = st.number_input("Orçamento (USD)", 
                                      min_value=1000000, 
                                      max_value=500000000,
                                      value=50000000,
                                      step=1000000)
            
            nota_esperada = st.slider("Nota IMDb Esperada", 1.0, 10.0, 7.0, 0.1)
            
            genero = st.selectbox("Gênero Principal", 
                                ["Ação", "Drama", "Comédia", "Ficção Científica", "Terror"])
            
            mes_lancamento = st.selectbox("Mês de Lançamento", 
                                        range(1, 13),
                                        format_func=lambda x: datetime(2020, x, 1).strftime('%B'))
            
            submitted = st.form_submit_button("🚀 Simular Performance")
    
    with col2:
        if submitted:
            st.markdown("#### 📊 Resultados da Simulação")
            
            # Inicializar analisador preditivo
            analisador = AnalisadorPreditivo(df_filtrado)
            resultado = analisador.prever_performance(orcamento, nota_esperada, genero, mes_lancamento)
            
            # Exibir resultados
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💰 Receita Prevista", f"${resultado['receita_prevista']:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_r2:
                st.markdown(f'<div class="metric-card-success">', unsafe_allow_html=True)
                st.metric("📈 ROI Previsto", f"{resultado['roi_previsto']:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_r3:
                st.markdown(f'<div class="metric-card-warning">', unsafe_allow_html=True)
                st.metric("🎯 Nível de Risco", f"{resultado['cor_risco']} {resultado['categoria_risco']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico de probabilidade
            fig_prob = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = resultado['probabilidade_sucesso'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Probabilidade de Sucesso"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90}}
            ))
            st.plotly_chart(fig_prob, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">🔍 Insights Inteligentes</div>', unsafe_allow_html=True)
    
    if not df_filtrado.empty:
        # Análise de correlação avançada
        numeric_cols = df_filtrado.select_dtypes(include=[np.number]).columns
        correlation_matrix = df_filtrado[numeric_cols].corr()
        
        fig_corr = px.imshow(
            correlation_matrix,
            title="🔥 Mapa de Correlações Avançado",
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Insights automáticos
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.markdown("#### 💡 Insights de Mercado")
            
            # Insight 1: Melhor investimento
            melhor_investimento = df_filtrado.loc[df_filtrado['roi'].idxmax()]
            st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"##### 🏆 Melhor Investimento")
            st.markdown(f"**{melhor_investimento['names']}**")
            st.markdown(f"ROI: **{melhor_investimento['roi']:.1f}%**")
            st.markdown(f"Nota: **{melhor_investimento['score']:.1f}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_i2:
            st.markdown("#### ⚠️ Alertas e Oportunidades")
            
            # Análise de sazonalidade
            if 'estacao' in df_filtrado.columns:
                performance_estacao = df_filtrado.groupby('estacao')['roi'].mean()
                melhor_estacao = performance_estacao.idxmax()
                
                st.markdown(f'<div class="prediction-box">', unsafe_allow_html=True)
                st.markdown(f"##### 📅 Melhor Época")
                st.markdown(f"**{melhor_estacao}** tem o maior ROI médio")
                st.markdown(f"ROI: **{performance_estacao[melhor_estacao]:.1f}%**")
                st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section-header">🏆 Benchmarking Competitivo</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 filmes por ROI
        st.markdown("#### 💰 Top 10 por ROI")
        top_roi = df_filtrado.nlargest(10, 'roi')[['names', 'roi', 'revenue', 'score']]
        if not top_roi.empty:
            top_roi_display = top_roi.copy()
            top_roi_display['ROI'] = top_roi_display['roi'].apply(lambda x: f"{x:.1f}%")
            top_roi_display['Receita'] = top_roi_display['revenue'].apply(lambda x: f"${x:,.0f}")
            top_roi_display['Nota'] = top_roi_display['score'].apply(lambda x: f"{x:.1f}")
            st.dataframe(
                top_roi_display[['names', 'ROI', 'Receita', 'Nota']].rename(
                    columns={'names': 'Filme'}),
                use_container_width=True
            )
    
    with col2:
        # Comparação por década
        st.markdown("#### 📊 Evolução Histórica")
        if 'decada' in df_filtrado.columns:
            decada_stats = df_filtrado.groupby('decada').agg({
                'revenue': 'mean',
                'budget_x': 'mean',
                'roi': 'mean'
            }).reset_index()
            
            fig_decada = px.line(
                decada_stats,
                x='decada',
                y=['revenue', 'budget_x'],
                title="Evolução da Receita e Orçamento por Década",
                markers=True
            )
            st.plotly_chart(fig_decada, use_container_width=True)

with tab6:
    st.markdown('<div class="section-header">📋 Base de Dados Completa</div>', unsafe_allow_html=True)
    
    # Sistema de busca e filtro
    col_search, col_filter = st.columns([2, 1])
    
    with col_search:
        busca = st.text_input("🔍 Buscar filmes:", placeholder="Digite o nome do filme...")
    
    with col_filter:
        colunas_visiveis = st.multiselect(
            "Colunas visíveis:",
            options=df_filtrado.columns.tolist(),
            default=['names', 'score', 'revenue', 'budget_x', 'roi', 'ano']
        )
    
    # Aplicar busca
    if busca:
        df_display = df_filtrado[df_filtrado['names'].str.contains(busca, case=False, na=False)]
    else:
        df_display = df_filtrado
    
    # Exibir dataframe com formatação
    if not df_display.empty:
        st.dataframe(
            df_display[colunas_visiveis].style.format({
                "revenue": "${:,.0f}",
                "budget_x": "${:,.0f}",
                "score": "{:.2f}",
                "roi": "{:.1f}%"
            }),
            use_container_width=True,
            height=600
        )
        
        # Estatísticas rápidas
        st.markdown(f"**📊 Mostrando {len(df_display)} de {len(df_filtrado)} filmes**")
    else:
        st.warning("Nenhum filme encontrado com os critérios de busca.")

with tab7:
    st.markdown('<div class="section-header">🤖 Assistente de IA</div>', unsafe_allow_html=True)
    
    st.info("""
    **🚀 Recursos de IA em Desenvolvimento:**
    
    - 🤖 **Analisador Preditivo**: Previsões de bilheteria baseadas em machine learning
    - 📝 **Gerador de Relatórios**: Análises automáticas personalizadas
    - 🎯 **Recomendações Inteligentes**: Sugestões baseadas em dados históricos
    - 🔮 **Análise de Tendências**: Identificação de padrões emergentes
    
    *Estes recursos estarão disponíveis em breve!*
    """)
    
    # Simulação de análise IA
    if st.button("🧠 Executar Análise IA (Demo)"):
        with st.spinner("Analisando dados com IA..."):
            time.sleep(2)
            
            st.success("✅ Análise concluída!")
            
            col_ia1, col_ia2 = st.columns(2)
            
            with col_ia1:
                st.markdown("#### 📈 Insights da IA")
                st.markdown("""
                - **Tendência Identificada**: Filmes de verão têm 25% mais ROI
                - **Oportunidade**: Mercado de comédia subexplorado
                - **Alerta**: Orçamentos acima de $150M têm risco aumentado
                """)
            
            with col_ia2:
                st.markdown("#### 🎯 Recomendações")
                st.markdown("""
                - 🎬 Investir em filmes de médio orçamento ($50-80M)
                - 📅 Priorizar lançamentos no verão
                - ⭐ Buscar notas acima de 7.0 no IMDb
                """)

# =========================
# RODAPÉ AVANÇADO
# =========================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("**📊 Estatísticas do Dataset**")
    st.markdown(f"""
    - Total de Filmes: {len(df):,}
    - Período: {df['ano'].min()} - {df['ano'].max()}
    - Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """)

with col_f2:
    st.markdown("**🔧 Tecnologias**")
    st.markdown("""
    - Streamlit • Plotly • Pandas
    - Análise Preditiva • Visualização 3D
    - Processamento em Tempo Real
    """)

with col_f2:
    st.markdown("**📞 Suporte**")
    st.markdown("""
    - 📧 suporte@cineanalytics.com
    - 🌐 www.cineanalytics.com
    - 📱 Versão 2.1.0
    """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6c757d;'>🎬 CineAnalytics Pro - Transformando dados em insights cinematográficos</div>", unsafe_allow_html=True)
