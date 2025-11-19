# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
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
    .section-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #34495e;
    }
    .chart-container {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 1.5rem;
        border-radius: 10px;
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
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSSV_URL, parse_dates=['date_x'])
        
        # Limpeza e transformação
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        
        # Extrair ano e mês
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(0).astype(int)
        
        # Calcular ROI
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
TRADUCOES_FILMES = {
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
    
    # Filmes de Ação e Aventura
    "Transformers: Dark of the Moon": "Transformers: O Lado Oculto da Lua",
    "Skyfall": "007 - Operação Skyfall",
    "Transformers: Age of Extinction": "Transformers: A Era da Extinção",
    "The Dark Knight Rises": "Batman: O Cavaleiro das Trevas Ressurge",
    "Toy Story 4": "Toy Story 4",
    "Toy Story 3": "Toy Story 3",
    "Pirates of the Caribbean: Dead Man's Chest": "Piratas do Caribe: O Baú da Morte",
    "Rogue One: A Star Wars Story": "Rogue One: Uma História Star Wars",
    "Pirates of the Caribbean: On Stranger Tides": "Piratas do Caribe: Navegando em Águas Misteriosas",
    "Despicable Me 3": "Meu Malvado Favorito 3",
    "Jumanji: Welcome to the Jungle": "Jumanji: Bem-vindo à Selva",
    "Justice League": "Liga da Justiça",
    "The Dark Knight": "Batman: O Cavaleiro das Trevas",
    
    # Filmes de Animação
    "Finding Dory": "Procurando Dory",
    "Zootopia": "Zootopia: Essa Cidade é o Bicho",
    "Despicable Me 2": "Meu Malvado Favorito 2",
    "The Grinch": "O Grinch",
    "Finding Nemo": "Procurando Nemo",
    "Shrek 2": "Shrek 2",
    "The Secret Life of Pets": "A Vida Secreta dos Bichos",
    "Inside Out": "Divertida Mente",
    "The Incredibles": "Os Incríveis",
    "Shrek the Third": "Shrek Terceiro",
    "Shrek": "Shrek",
    "Madagascar 3: Europe's Most Wanted": "Madagascar 3: Os Procurados",
    "Monsters, Inc.": "Monstros S.A.",
    "Up": "Up: Altas Aventuras",
    "Spider-Man: Into the Spider-Verse": "Homem-Aranha no Aranhaverso",
    
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
    
    # Filmes Diversos
    "The Lord of the Rings: The Two Towers": "O Senhor dos Anéis: As Duas Torres",
    "The Lord of the Rings: The Fellowship of the Ring": "O Senhor dos Anéis: A Sociedade do Anel",
    "The Matrix Reloaded": "Matrix Reloaded",
    "The Twilight Saga: Breaking Dawn - Part 2": "A Saga Crepúsculo: Amanhecer - Parte 2",
    "The Twilight Saga: New Moon": "A Saga Crepúsculo: Lua Nova",
    "The Twilight Saga: Eclipse": "A Saga Crepúsculo: Eclipse",
    "The Twilight Saga: Breaking Dawn - Part 1": "A Saga Crepúsculo: Amanhecer - Parte 1",
    "The Hobbit: An Unexpected Journey": "O Hobbit: Uma Jornada Inesperada",
    "The Hobbit: The Desolation of Smaug": "O Hobbit: A Desolação de Smaug",
    "The Hobbit: The Battle of the Five Armies": "O Hobbit: A Batalha dos Cinco Exércitos",
    "The Da Vinci Code": "O Código Da Vinci",
    "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe": "As Crônicas de Nárnia: O Leão, a Feiticeira e o Guarda-Roupa",
    "The Passion of the Christ": "A Paixão de Cristo",
    "The Exorcist": "O Exorcista",
    "The Sound of Music": "A Noviça Rebelde",
    "The Sting": "Um Golpe de Mestre",
    "Butch Cassidy and the Sundance Kid": "Butch Cassidy e o Menino da Lua",
    
    # Filmes em Português (manter como estão)
    "Cidade de Deus": "Cidade de Deus",
    "Tropa de Elite": "Tropa de Elite",
    "Central do Brasil": "Central do Brasil",
    "O Auto da Compadecida": "O Auto da Compadecida",
    "Lisbela e o Prisioneiro": "Lisbela e o Prisioneiro",
}

def traduzir_nome_filme(nome_original):
    if pd.isna(nome_original):
        return nome_original
    return TRADUCOES_FILMES.get(nome_original, nome_original)

# =========================
# FUNÇÕES DE ANÁLISE DO COLAB (CORRIGIDAS)
# =========================
def criar_grafico_top_filmes(df, top_n=10):
    """Top filmes por receita - Gráfico 1 do Colab"""
    top_filmes = df.nlargest(top_n, 'revenue')[['names', 'revenue', 'score']].copy()
    top_filmes['names'] = top_filmes['names'].apply(traduzir_nome_filme)
    
    fig = px.bar(
        top_filmes,
        x='revenue',
        y='names',
        orientation='h',
        title=f'🏆 Top {top_n} Filmes por Receita',
        labels={'revenue': 'Receita (USD)', 'names': 'Filme'},
        color='revenue',
        color_continuous_scale='viridis',
        hover_data=['score']
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    return fig

def criar_grafico_dispercao_nota_receita(df):
    """Relação entre nota e receita - Gráfico 2 do Colab (CORRIGIDO)"""
    fig = px.scatter(
        df,
        x='score',
        y='revenue',
        title='🎯 Relação entre Nota e Receita',
        labels={'score': 'Nota IMDb', 'revenue': 'Receita (USD)'},
        hover_data=['names'],
        # Removido trendline='lowess' que causava o erro
        color_discrete_sequence=['#FF6B6B']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def criar_grafico_evolucao_receita_anual(df):
    """Evolução da receita anual - Gráfico 3 do Colab"""
    receita_anual = df.groupby('ano')['revenue'].sum().reset_index()
    
    fig = px.line(
        receita_anual,
        x='ano',
        y='revenue',
        title='📈 Evolução da Receita Anual da Indústria Cinematográfica',
        labels={'ano': 'Ano', 'revenue': 'Receita Total (USD)'},
        markers=True
    )
    fig.update_traces(line=dict(color='#4ECDC4', width=3))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def criar_grafico_distribuicao_idiomas(df):
    """Distribuição de idiomas - Gráfico 4 do Colab"""
    idiomas = df['orig_lang'].value_counts().head(10).reset_index()
    idiomas.columns = ['Idioma', 'Quantidade']
    
    fig = px.pie(
        idiomas,
        values='Quantidade',
        names='Idioma',
        title='🌎 Distribuição dos Idiomas Originais (Top 10)',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def criar_grafico_filmes_por_ano(df):
    """Quantidade de filmes por ano - Gráfico 5 do Colab"""
    filmes_ano = df.groupby('ano').size().reset_index(name='quantidade')
    
    fig = px.bar(
        filmes_ano,
        x='ano',
        y='quantidade',
        title='🎬 Quantidade de Filmes por Ano',
        labels={'ano': 'Ano', 'quantidade': 'Número de Filmes'},
        color='quantidade',
        color_continuous_scale='blues'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    return fig

def criar_grafico_media_notas_ano(df):
    """Média de notas por ano - Gráfico 6 do Colab"""
    media_notas = df.groupby('ano')['score'].mean().reset_index()
    
    fig = px.line(
        media_notas,
        x='ano',
        y='score',
        title='⭐ Evolução da Média de Notas por Ano',
        labels={'ano': 'Ano', 'score': 'Nota Média'},
        markers=True
    )
    fig.update_traces(line=dict(color='#FFA726', width=3))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def criar_grafico_correlacao(df):
    """Mapa de calor de correlações - Gráfico 7 do Colab"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title='🔥 Mapa de Calor de Correlações',
            color_continuous_scale='RdBu_r',
            aspect='auto',
            text_auto=True
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        return fig
    return None

def criar_grafico_decadas(df):
    """Análise por décadas - Gráfico 8 do Colab"""
    df_copy = df.copy()
    df_copy['decada'] = (df_copy['ano'] // 10) * 10
    decada_stats = df_copy.groupby('decada').agg({
        'revenue': 'mean',
        'score': 'mean',
        'names': 'count'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=decada_stats['decada'],
        y=decada_stats['names'],
        name='Número de Filmes',
        marker_color='#4ECDC4'
    ))
    fig.add_trace(go.Scatter(
        x=decada_stats['decada'],
        y=decada_stats['revenue'] / max(decada_stats['revenue'].max(), 1) * decada_stats['names'].max(),
        name='Receita Média (escala ajustada)',
        line=dict(color='#FF6B6B', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='📊 Análise por Décadas: Quantidade de Filmes e Receita Média',
        xaxis_title='Década',
        yaxis_title='Número de Filmes',
        yaxis2=dict(
            title='Receita Média (escala ajustada)',
            overlaying='y',
            side='right',
            range=[0, decada_stats['names'].max()]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def criar_grafico_sazonalidade(df):
    """Análise de sazonalidade - Gráfico 9 do Colab"""
    if 'mes' in df.columns:
        sazonalidade = df.groupby('mes').agg({
            'revenue': 'mean',
            'score': 'mean',
            'names': 'count'
        }).reset_index()
        
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=meses,
            y=sazonalidade['revenue'],
            name='Receita Média',
            line=dict(color='#4ECDC4', width=3)
        ))
        fig.add_trace(go.Bar(
            x=meses,
            y=sazonalidade['names'],
            name='Número de Filmes',
            marker_color='rgba(255, 107, 107, 0.6)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='📅 Sazonalidade: Lançamentos e Receita por Mês',
            xaxis_title='Mês',
            yaxis_title='Receita Média (USD)',
            yaxis2=dict(
                title='Número de Filmes',
                overlaying='y',
                side='right'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        return fig
    return None

def criar_grafico_orcamento_vs_receita(df):
    """Relação orçamento vs receita - Gráfico adicional do Colab (CORRIGIDO)"""
    df_filtrado = df[df['budget_x'] > 0]
    if len(df_filtrado) > 0:
        fig = px.scatter(
            df_filtrado,
            x='budget_x',
            y='revenue',
            title='💰 Relação entre Orçamento e Receita',
            labels={'budget_x': 'Orçamento (USD)', 'revenue': 'Receita (USD)'},
            # Removido trendline que causava erro
            hover_data=['names', 'score'],
            color_discrete_sequence=['#FFA726']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        return fig
    return None

def criar_grafico_distribuicao_notas(df):
    """Distribuição de notas - Gráfico adicional do Colab"""
    fig = px.histogram(
        df,
        x='score',
        nbins=30,
        title='📊 Distribuição das Notas dos Filmes',
        labels={'score': 'Nota IMDb', 'count': 'Número de Filmes'},
        color_discrete_sequence=['#4ECDC4']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    return fig

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4ECDC4;'>🎛️ Painel de Controle</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtro de anos
    st.markdown("#### 📅 Filtro por Ano")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )
    
    st.markdown("---")
    
    # Filtro de notas
    st.markdown("#### ⭐ Filtro por Nota")
    score_min, score_max = st.slider(
        "Selecione a faixa de notas:",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1
    )
    
    st.markdown("---")
    
    # Filtro de receita
    st.markdown("#### 💰 Filtro por Receita")
    receita_max = df["revenue"].max()
    receita_min, receita_max = st.slider(
        "Selecione a faixa de receita:",
        min_value=0.0,
        max_value=float(receita_max),
        value=(0.0, float(receita_max)),
        step=1_000_000.0,
        format="$%.0f"
    )

# Aplicar filtro principal
df_filtrado = df[
    (df["ano"] >= ano_min) &
    (df["ano"] <= ano_max) &
    (df["score"] >= score_min) &
    (df["score"] <= score_max) &
    (df["revenue"] >= receita_min) &
    (df["revenue"] <= receita_max)
]

# Aplicar tradução aos nomes dos filmes
df_filtrado = df_filtrado.copy()
df_filtrado["names"] = df_filtrado["names"].apply(traduzir_nome_filme)

# =========================
# CABEÇALHO
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Completo com Todas as Análises do Colab</p>', unsafe_allow_html=True)

# =========================
# SISTEMA DE ABAS COM TODOS OS GRÁFICOS DO COLAB
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏆 Top Filmes", 
    "📈 Tendências Temporais", 
    "🎯 Relações e Correlações",
    "🌎 Distribuições",
    "📊 Análise Financeira",
    "📅 Sazonalidade",
    "🔍 Dados Completos"
])

with tab1:
    st.markdown('<div class="section-header">🏆 Análise dos Filmes Mais Populares</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Filmes por Receita")
        top_n = st.slider("Número de filmes:", 5, 20, 10, key="top_n")
        fig_top = criar_grafico_top_filmes(df_filtrado, top_n)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribuição de Notas")
        fig_dist_notas = criar_grafico_distribuicao_notas(df_filtrado)
        st.plotly_chart(fig_dist_notas, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">📈 Análise Temporal e Evolução</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Evolução da Receita Anual")
        fig_evolucao_receita = criar_grafico_evolucao_receita_anual(df_filtrado)
        st.plotly_chart(fig_evolucao_receita, use_container_width=True)
        
        st.markdown("#### Quantidade de Filmes por Ano")
        fig_filmes_ano = criar_grafico_filmes_por_ano(df_filtrado)
        st.plotly_chart(fig_filmes_ano, use_container_width=True)
    
    with col2:
        st.markdown("#### Evolução das Notas Médias")
        fig_media_notas = criar_grafico_media_notas_ano(df_filtrado)
        st.plotly_chart(fig_media_notas, use_container_width=True)
        
        st.markdown("#### Análise por Décadas")
        fig_decadas = criar_grafico_decadas(df_filtrado)
        st.plotly_chart(fig_decadas, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">🎯 Relações entre Variáveis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Nota vs Receita")
        fig_dispersao = criar_grafico_dispercao_nota_receita(df_filtrado)
        if fig_dispersao:
            st.plotly_chart(fig_dispersao, use_container_width=True)
        else:
            st.info("Não há dados suficientes para este gráfico")
    
    with col2:
        st.markdown("#### Orçamento vs Receita")
        fig_orcamento_receita = criar_grafico_orcamento_vs_receita(df_filtrado)
        if fig_orcamento_receita:
            st.plotly_chart(fig_orcamento_receita, use_container_width=True)
        else:
            st.info("Não há dados de orçamento suficientes")
    
    st.markdown("#### Mapa de Correlações")
    fig_correlacao = criar_grafico_correlacao(df_filtrado)
    if fig_correlacao:
        st.plotly_chart(fig_correlacao, use_container_width=True)
    else:
        st.info("Não há dados numéricos suficientes para correlação")

with tab4:
    st.markdown('<div class="section-header">🌎 Distribuições e Categorias</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribuição de Idiomas")
        fig_idiomas = criar_grafico_distribuicao_idiomas(df_filtrado)
        st.plotly_chart(fig_idiomas, use_container_width=True)
    
    with col2:
        st.markdown("#### Categorias de Sucesso")
        success_dist = df_filtrado['success_category'].value_counts()
        if len(success_dist) > 0:
            fig_success = px.pie(
                values=success_dist.values,
                names=success_dist.index,
                title="Distribuição por Categoria de Sucesso",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_success.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_success, use_container_width=True)
        else:
            st.info("Não há dados para categorias de sucesso")

with tab5:
    st.markdown('<div class="section-header">📊 Análise Financeira Detalhada</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Métricas financeiras
        if not df_filtrado.empty:
            receita_total = df_filtrado["revenue"].sum()
            receita_media = df_filtrado["revenue"].mean()
            roi_medio = df_filtrado["roi"].mean()
            orcamento_medio = df_filtrado[df_filtrado["budget_x"] > 0]["budget_x"].mean()
            
            st.metric("💰 Receita Total", f"${receita_total:,.0f}")
            st.metric("📊 Receita Média", f"${receita_media:,.0f}")
            st.metric("📈 ROI Médio", f"{roi_medio:.1f}%")
            st.metric("💸 Orçamento Médio", f"${orcamento_medio:,.0f}" if not pd.isna(orcamento_medio) else "N/A")
        else:
            st.info("Não há dados financeiros disponíveis")
    
    with col2:
        st.markdown("#### Top Filmes por ROI")
        df_roi = df_filtrado[df_filtrado['roi'] > 0].nlargest(10, 'roi')
        if not df_roi.empty:
            fig_roi = px.bar(
                df_roi,
                x='roi',
                y='names',
                orientation='h',
                title='📈 Top Filmes por ROI',
                labels={'roi': 'ROI (%)', 'names': 'Filme'},
                color='roi',
                color_continuous_scale='viridis'
            )
            fig_roi.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            st.plotly_chart(fig_roi, use_container_width=True)
        else:
            st.info("Não há dados de ROI disponíveis")

with tab6:
    st.markdown('<div class="section-header">📅 Análise de Sazonalidade</div>', unsafe_allow_html=True)
    
    fig_sazonalidade = criar_grafico_sazonalidade(df_filtrado)
    if fig_sazonalidade:
        st.plotly_chart(fig_sazonalidade, use_container_width=True)
    else:
        st.info("Dados de sazonalidade não disponíveis")
    
    # Análise adicional de meses
    if 'mes' in df_filtrado.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            meses_ordenados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec']
            receita_mensal = df_filtrado.groupby('mes')['revenue'].mean().reset_index()
            
            if len(receita_mensal) > 0:
                fig_mensal = px.bar(
                    receita_mensal,
                    x=receita_mensal['mes'].apply(lambda x: meses_ordenados[x-1]),
                    y='revenue',
                    title='💰 Receita Média por Mês',
                    labels={'x': 'Mês', 'revenue': 'Receita Média'},
                    color='revenue',
                    color_continuous_scale='blues'
                )
                fig_mensal.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_mensal, use_container_width=True)
        
        with col2:
            filmes_mensal = df_filtrado.groupby('mes').size().reset_index(name='count')
            
            if len(filmes_mensal) > 0:
                fig_count_mensal = px.bar(
                    filmes_mensal,
                    x=filmes_mensal['mes'].apply(lambda x: meses_ordenados[x-1]),
                    y='count',
                    title='🎬 Número de Filmes por Mês',
                    labels={'x': 'Mês', 'count': 'Número de Filmes'},
                    color='count',
                    color_continuous_scale='greens'
                )
                fig_count_mensal.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_count_mensal, use_container_width=True)

with tab7:
    st.markdown('<div class="section-header">🔍 Base de Dados Completa</div>', unsafe_allow_html=True)
    
    # Sistema de busca
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar filme:", placeholder="Digite o nome do filme...")
    with col2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "Ano de Lançamento", "Nome do Filme"],
            index=0
        )
    with col3:
        resultados_por_pagina = st.selectbox("Itens por página:", [10, 25, 50, 100], index=0)

    # Preparar dados para exibição
    df_display = df_filtrado.copy().rename(columns={
        "names": "Nome do Filme",
        "orig_lang": "Idioma Original",
        "revenue": "Receita",
        "score": "Pontuação",
        "ano": "Ano de Lançamento",
        "date_x": "Data de Lançamento",
        "country": "País de Origem",
        "genre": "Gênero",
        "budget_x": "Orçamento",
        "roi": "ROI"
    })

    # Formatações
    if "Data de Lançamento" in df_display.columns:
        df_display["Data de Lançamento"] = pd.to_datetime(
            df_display["Data de Lançamento"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    df_display["Receita"] = df_display["Receita"].apply(
        lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A"
    )

    df_display["Pontuação"] = df_display["Pontuação"].apply(
        lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A"
    )

    df_display["ROI"] = df_display["ROI"].apply(
        lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A"
    )

    df_display["Orçamento"] = df_display["Orçamento"].apply(
        lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A"
    )

    # Filtro de busca
    if search_term:
        df_display = df_display[
            df_display["Nome do Filme"].str.contains(search_term, case=False, na=False) |
            df_display["Gênero"].str.contains(search_term, case=False, na=False)
        ]

    # Ordenação
    sort_map = {
        "Receita": "Receita",
        "Pontuação": "Pontuação", 
        "Ano de Lançamento": "Ano de Lançamento",
        "Nome do Filme": "Nome do Filme"
    }
    
    if sort_by in sort_map:
        ascending = sort_by == "Nome do Filme"
        # Converter para numérico se necessário para ordenação
        if sort_by == "Receita":
            df_display["Receita_Num"] = df_display["Receita"].replace('[\$,]', '', regex=True).replace('N/A', '0').astype(float)
            df_display = df_display.sort_values(by="Receita_Num", ascending=ascending)
        elif sort_by == "Pontuação":
            df_display["Pontuação_Num"] = df_display["Pontuação"].replace('N/A', '0').astype(float)
            df_display = df_display.sort_values(by="Pontuação_Num", ascending=ascending)
        else:
            df_display = df_display.sort_values(by=sort_map[sort_by], ascending=ascending)

    # Colunas a exibir
    colunas_para_mostrar = [
        "Nome do Filme", "Gênero", "Idioma Original", "País de Origem",
        "Pontuação", "Receita", "Orçamento", "ROI", "Ano de Lançamento"
    ]

    # Sistema de paginação
    total_resultados = len(df_display)
    if total_resultados > 0:
        total_paginas = (total_resultados + resultados_por_pagina - 1) // resultados_por_pagina
        pagina_atual = st.number_input("Página:", min_value=1, max_value=max(total_paginas, 1), value=1)
        
        inicio = (pagina_atual - 1) * resultados_por_pagina
        fim = inicio + resultados_por_pagina
        
        df_paginado = df_display.iloc[inicio:fim]
        
        st.caption(f"Mostrando {inicio + 1}-{min(fim, total_resultados)} de {total_resultados} resultados")
        
        st.dataframe(
            df_paginado[colunas_para_mostrar],
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        if st.button("📥 Exportar Dados para CSV"):
            csv = df_display[colunas_para_mostrar].to_csv(index=False)
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name="filmes_completo.csv",
                mime="text/csv"
            )
    else:
        st.warning("🎭 Nenhum filme encontrado com os filtros aplicados.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>"
    f"📊 Dashboard CineAnalytics Pro • Todos os Gráficos do Colab • "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} • "
    f"🎬 {len(df_filtrado):,} filmes analisados"
    f"</div>",
    unsafe_allow_html=True
)
