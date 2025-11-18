# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from plotly.subplots import make_subplots

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
# DICIONÁRIOS DE TRADUÇÃO
# =========================
TRADUCOES_FILMES = {
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
    "Cidade de Deus": "Cidade de Deus",
    "Tropa de Elite": "Tropa de Elite",
    "Central do Brasil": "Central do Brasil",
    "O Auto da Compadecida": "O Auto da Compadecida",
    "Lisbela e o Prisioneiro": "Lisbela e o Prisioneiro",
}

TRADUCOES_GENEROS = {
    "Action": "Ação", "Adventure": "Aventura", "Animation": "Animação", 
    "Comedy": "Comédia", "Crime": "Crime", "Documentary": "Documentário",
    "Drama": "Drama", "Family": "Família", "Fantasy": "Fantasia",
    "History": "História", "Horror": "Terror", "Music": "Música",
    "Mystery": "Mistério", "Romance": "Romance", "Science Fiction": "Ficção Científica",
    "TV Movie": "Filme de TV", "Thriller": "Suspense", "War": "Guerra",
    "Western": "Faroeste"
}

MESES_PORTUGUES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# =========================
# SISTEMA DE TRADUÇÃO
# =========================
class SistemaTraducao:
    def __init__(self):
        self.cache_traducoes = {}
    
    def traduzir_filme(self, nome_original):
        if pd.isna(nome_original):
            return nome_original
        if nome_original in self.cache_traducoes:
            return self.cache_traducoes[nome_original]
        traducao = TRADUCOES_FILMES.get(nome_original, nome_original)
        self.cache_traducoes[nome_original] = traducao
        return traducao
    
    def traduzir_genero(self, genero_original):
        if pd.isna(genero_original):
            return "Gênero não disponível"
        if ',' in genero_original:
            generos = [g.strip() for g in genero_original.split(',')]
            generos_traduzidos = [TRADUCOES_GENEROS.get(g, g) for g in generos]
            return ', '.join(generos_traduzidos)
        return TRADUCOES_GENEROS.get(genero_original, genero_original)
    
    def formatar_data_completa(self, data):
        if pd.isna(data):
            return "Data não disponível"
        try:
            if isinstance(data, str):
                data = pd.to_datetime(data)
            dia = data.day
            mes = MESES_PORTUGUES[data.month]
            ano = data.year
            return f"{dia} de {mes} de {ano}"
        except:
            return "Data inválida"

# =========================
# CARREGAR E PROCESSAR DADOS (ADAPTAÇÃO DO COLAB)
# =========================
@st.cache_data
def carregar_dados_colab():
    """
    Adaptação do código do Google Colab para o Streamlit
    """
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    
    try:
        # Carregar dados
        df = pd.read_csv(CSV_URL)
        
        # Verificar estrutura dos dados
        st.info(f"📊 Dataset carregado: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        # Inicializar tradutor
        tradutor = SistemaTraducao()
        
        # PROCESSAMENTO ESPECÍFICO DO COLAB
        # 1. Limpeza de dados financeiros
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce").fillna(0)
        
        # 2. Processar datas (adaptado do Colab)
        date_columns = ['date_x', 'date_published', 'release_date']
        date_column = None
        for col in date_columns:
            if col in df.columns:
                date_column = col
                break
        
        if date_column:
            df["date_x"] = pd.to_datetime(df[date_column], errors='coerce')
        else:
            # Criar datas baseadas no índice (fallback)
            start_date = datetime(2000, 1, 1)
            df["date_x"] = [start_date + timedelta(days=x*30) for x in range(len(df))]
        
        # Extrair componentes de data
        df["ano"] = df["date_x"].dt.year.fillna(2000).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(1).astype(int)
        df["dia"] = df["date_x"].dt.day.fillna(1).astype(int)
        df["decada"] = (df["ano"] // 10) * 10
        
        # 3. Calcular métricas financeiras (do Colab)
        df["lucro"] = df["revenue"] - df["budget_x"]
        df["roi"] = np.where(
            df["budget_x"] > 0,
            (df["lucro"] / df["budget_x"]) * 100,
            0
        )
        df["orcamento_ratio"] = np.where(
            df["revenue"] > 0,
            df["budget_x"] / df["revenue"],
            0
        )
        
        # 4. Categorização baseada no Colab
        # Categorizar por receita
        conditions = [
            (df['revenue'] >= df['revenue'].quantile(0.9)),
            (df['revenue'] >= df['revenue'].quantile(0.7)),
            (df['revenue'] >= df['revenue'].quantile(0.5)),
            (df['revenue'] >= df['revenue'].quantile(0.3)),
            (df['revenue'] < df['revenue'].quantile(0.3))
        ]
        choices = ['Super Blockbuster', 'Blockbuster', 'Alto', 'Médio', 'Baixo']
        df['categoria_receita'] = np.select(conditions, choices, default='Baixo')
        
        # Categorizar por ROI
        roi_conditions = [
            (df['roi'] >= 500),
            (df['roi'] >= 100),
            (df['roi'] >= 0),
            (df['roi'] < 0)
        ]
        roi_choices = ['Excelente', 'Bom', 'Regular', 'Ruim']
        df['categoria_roi'] = np.select(roi_conditions, roi_choices, default='Regular')
        
        # 5. Aplicar traduções
        df["nome_pt"] = df["names"].apply(tradutor.traduzir_filme)
        
        # Traduzir gêneros
        genre_columns = ['genre', 'genres', 'category']
        genre_column = None
        for col in genre_columns:
            if col in df.columns:
                genre_column = col
                break
        
        if genre_column:
            df["genero_pt"] = df[genre_column].apply(tradutor.traduzir_genero)
        else:
            df["genero_pt"] = "Gênero não disponível"
        
        # Data formatada
        df["data_completa_pt"] = df["date_x"].apply(tradutor.formatar_data_completa)
        
        # 6. Engenharia de features do Colab
        # Duração categorizada
        if 'duration' in df.columns:
            df['duracao_categoria'] = pd.cut(
                df['duration'],
                bins=[0, 90, 120, 180, 1000],
                labels=['Curto (<90min)', 'Médio (90-120min)', 'Longo (120-180min)', 'Muito Longo (>180min)']
            )
        
        # Popularidade normalizada
        if 'vote_count' in df.columns:
            df['popularidade_norm'] = (df['vote_count'] - df['vote_count'].min()) / (df['vote_count'].max() - df['vote_count'].min())
        
        st.success("✅ Dados processados com sucesso usando adaptação do Colab!")
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        return None

# =========================
# ANÁLISES ESPECÍFICAS DO COLAB
# =========================
def analise_exploratoria_colab(df):
    """Análises específicas baseadas no notebook do Colab"""
    
    st.markdown('<div class="section-header">🔍 Análise Exploratória (Adaptada do Colab)</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Distribuição de notas
        fig_notas = px.histogram(
            df, 
            x='score',
            nbins=50,
            title='Distribuição das Notas IMDb',
            color_discrete_sequence=['#4ECDC4']
        )
        fig_notas.update_layout(showlegend=False)
        st.plotly_chart(fig_notas, use_container_width=True)
    
    with col2:
        # Distribuição de receitas
        fig_receitas = px.histogram(
            df,
            x=np.log1p(df['revenue']),
            nbins=50,
            title='Distribuição de Receitas (Log)',
            color_discrete_sequence=['#FF6B6B']
        )
        fig_receitas.update_layout(showlegend=False, xaxis_title='Log(Receita)')
        st.plotly_chart(fig_receitas, use_container_width=True)
    
    with col3:
        # Distribuição de ROI
        fig_roi = px.box(
            df[df['roi'].between(-100, 1000)],
            y='roi',
            title='Distribuição de ROI',
            color_discrete_sequence=['#FFA726']
        )
        st.plotly_chart(fig_roi, use_container_width=True)

def analise_correlacao_colab(df):
    """Análise de correlação baseada no Colab"""
    
    st.markdown('<div class="section-header">📊 Análise de Correlações</div>', unsafe_allow_html=True)
    
    # Selecionar colunas numéricas para correlação
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlation_data = df[numeric_cols].corr()
    
    # Heatmap de correlação
    fig_corr = px.imshow(
        correlation_data,
        title="Mapa de Correlação entre Variáveis Numéricas",
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Correlações específicas destacadas
    st.markdown("#### 🔗 Correlações Principais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'budget_x' in numeric_cols and 'revenue' in numeric_cols:
            corr = df['budget_x'].corr(df['revenue'])
            st.metric("Orçamento vs Receita", f"{corr:.3f}")
    
    with col2:
        if 'score' in numeric_cols and 'revenue' in numeric_cols:
            corr = df['score'].corr(df['revenue'])
            st.metric("Nota vs Receita", f"{corr:.3f}")
    
    with col3:
        if 'budget_x' in numeric_cols and 'score' in numeric_cols:
            corr = df['budget_x'].corr(df['score'])
            st.metric("Orçamento vs Nota", f"{corr:.3f}")
    
    with col4:
        if 'vote_count' in numeric_cols and 'revenue' in numeric_cols:
            corr = df['vote_count'].corr(df['revenue'])
            st.metric("Votos vs Receita", f"{corr:.3f}")

def analise_temporal_colab(df):
    """Análise temporal baseada no Colab"""
    
    st.markdown('<div class="section-header">📈 Análise Temporal</div>', unsafe_allow_html=True)
    
    # Agrupar por ano
    yearly_stats = df.groupby('ano').agg({
        'revenue': ['mean', 'sum', 'count'],
        'score': 'mean',
        'roi': 'mean',
        'budget_x': 'mean'
    }).round(2)
    
    yearly_stats.columns = ['Receita Média', 'Receita Total', 'Nº Filmes', 'Nota Média', 'ROI Médio', 'Orçamento Médio']
    yearly_stats = yearly_stats.reset_index()
    
    # Gráfico de evolução temporal
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Evolução da Receita Média', 'Evolução da Nota Média', 
                       'Evolução do ROI Médio', 'Número de Filmes por Ano'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=yearly_stats['ano'], y=yearly_stats['Receita Média'], 
                  name='Receita Média', line=dict(color='#4ECDC4')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=yearly_stats['ano'], y=yearly_stats['Nota Média'],
                  name='Nota Média', line=dict(color='#FF6B6B')),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=yearly_stats['ano'], y=yearly_stats['ROI Médio'],
                  name='ROI Médio', line=dict(color='#FFA726')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=yearly_stats['ano'], y=yearly_stats['Nº Filmes'],
              name='Nº Filmes', marker_color='#45B7D1'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def analise_generos_colab(df):
    """Análise de gêneros baseada no Colab"""
    
    st.markdown('<div class="section-header">🎭 Análise por Gênero</div>', unsafe_allow_html=True)
    
    # Expandir gêneros múltiplos
    df_genres = df.copy()
    df_genres['genero_individual'] = df_genres['genero_pt'].str.split(', ')
    df_genres = df_genres.explode('genero_individual')
    
    # Estatísticas por gênero
    genre_stats = df_genres.groupby('genero_individual').agg({
        'nome_pt': 'count',
        'revenue': 'mean',
        'score': 'mean',
        'roi': 'mean',
        'budget_x': 'mean'
    }).round(2).sort_values('revenue', ascending=False)
    
    genre_stats = genre_stats.rename(columns={
        'nome_pt': 'Nº Filmes',
        'revenue': 'Receita Média',
        'score': 'Nota Média',
        'roi': 'ROI Médio',
        'budget_x': 'Orçamento Médio'
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Top gêneros por receita
        st.markdown("#### 💰 Top Gêneros por Receita Média")
        top_genres = genre_stats.nlargest(10, 'Receita Média')
        fig_genres = px.bar(
            top_genres.reset_index(),
            x='genero_individual',
            y='Receita Média',
            title='Top 10 Gêneros por Receita Média',
            color='Receita Média',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Estatísticas por Gênero")
        st.dataframe(genre_stats.head(10), use_container_width=True)

def insights_avancados_colab(df):
    """Insights avançados baseados no Colab"""
    
    st.markdown('<div class="section-header">💡 Insights Avançados do Colab</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Filmes Mais Lucrativos")
        
        # Filmes com melhor ROI
        top_roi = df.nlargest(5, 'roi')[['nome_pt', 'roi', 'revenue', 'budget_x', 'score']]
        for idx, filme in top_roi.iterrows():
            st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"**{filme['nome_pt']}**")
            st.markdown(f"ROI: **{filme['roi']:.1f}%** | Receita: **${filme['revenue']:,.0f}**")
            st.markdown(f"Orçamento: **${filme['budget_x']:,.0f}** | Nota: **{filme['score']:.1f}**")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚠️ Maiores Decepções")
        
        # Filmes com pior ROI (com orçamento significativo)
        filmes_com_orcamento = df[df['budget_x'] > 1000000]
        pior_roi = filmes_com_orcamento.nsmallest(5, 'roi')[['nome_pt', 'roi', 'revenue', 'budget_x', 'score']]
        
        for idx, filme in pior_roi.iterrows():
            st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"**{filme['nome_pt']}**")
            st.markdown(f"ROI: **{filme['roi']:.1f}%** | Prejuízo: **${abs(filme['revenue'] - filme['budget_x']):,.0f}**")
            st.markdown(f"Orçamento: **${filme['budget_x']:,.0f}** | Nota: **{filme['score']:.1f}**")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise de relação orçamento vs receita
    st.markdown("#### 📊 Relação Orçamento vs Receita")
    
    fig_relacao = px.scatter(
        df[df['budget_x'] > 0],
        x='budget_x',
        y='revenue',
        color='score',
        size='roi',
        hover_name='nome_pt',
        title='Relação entre Orçamento e Receita',
        labels={'budget_x': 'Orçamento', 'revenue': 'Receita', 'score': 'Nota IMDb'}
    )
    
    # Adicionar linha de referência (y = x)
    max_val = max(df['budget_x'].max(), df['revenue'].max())
    fig_relacao.add_shape(
        type="line", line=dict(dash="dash", color="white"),
        x0=0, y0=0, x1=max_val, y1=max_val
    )
    
    st.plotly_chart(fig_relacao, use_container_width=True)

# =========================
# INTERFACE PRINCIPAL
# =========================

# Carregar dados
df = carregar_dados_colab()
if df is None:
    st.error("Não foi possível carregar os dados. Verifique a conexão.")
    st.stop()

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4ECDC4;'>🎛️ Painel de Controle</h2>", unsafe_allow_html=True)
    
    st.markdown("### 📅 Filtro por Ano")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )
    
    st.markdown("---")
    
    # Filtro por gênero
    st.markdown("### 🎭 Filtro por Gênero")
    generos_disponiveis = sorted([g for g in df["genero_pt"].unique() if pd.notna(g)])
    generos_selecionados = st.multiselect(
        "Selecione os gêneros:",
        options=generos_disponiveis,
        default=generos_disponiveis[:3] if generos_disponiveis else []
    )
    
    st.markdown("---")
    
    # Filtros de performance
    st.markdown("### 📊 Filtros de Performance")
    score_min, score_max = st.slider(
        "⭐ Nota IMDb:",
        0.0, 10.0, (0.0, 10.0), 0.1
    )
    
    roi_min, roi_max = st.slider(
        "📈 ROI (%):",
        float(df["roi"].min()), float(df["roi"].max()), 
        (float(df["roi"].quantile(0.1)), float(df["roi"].quantile(0.9))), 
        50.0
    )

# Aplicar filtros
df_filtrado = df[
    (df["ano"] >= ano_min) & (df["ano"] <= ano_max) &
    (df["score"] >= score_min) & (df["score"] <= score_max) &
    (df["roi"] >= roi_min) & (df["roi"] <= roi_max)
]

if generos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["genero_pt"].isin(generos_selecionados)]

# =========================
# CABEÇALHO PRINCIPAL
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Adaptado do Google Colab - Análise Completa de Filmes</p>', unsafe_allow_html=True)

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
if not df_filtrado.empty:
    total_filmes = df_filtrado.shape[0]
    receita_total = df_filtrado["revenue"].sum()
    nota_media = df_filtrado["score"].mean()
    roi_medio = df_filtrado["roi"].mean()
    orcamento_total = df_filtrado["budget_x"].sum()
else:
    total_filmes = receita_total = nota_media = roi_medio = orcamento_total = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎬 Total de Filmes", f"{total_filmes:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card-success">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("⭐ Nota Média", f"{nota_media:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card-danger">', unsafe_allow_html=True)
    st.metric("📈 ROI Médio", f"{roi_medio:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# SISTEMA DE ABAS PRINCIPAL
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Análise Exploratória", 
    "📊 Correlações", 
    "📅 Análise Temporal",
    "🎭 Análise por Gênero",
    "💡 Insights Avançados",
    "📋 Base de Dados"
])

with tab1:
    analise_exploratoria_colab(df_filtrado)

with tab2:
    analise_correlacao_colab(df_filtrado)

with tab3:
    analise_temporal_colab(df_filtrado)

with tab4:
    analise_generos_colab(df_filtrado)

with tab5:
    insights_avancados_colab(df_filtrado)

with tab6:
    st.markdown('<div class="section-header">📋 Base de Dados Completa</div>', unsafe_allow_html=True)
    
    # Filtros de busca
    col_search, col_sort = st.columns([2, 1])
    
    with col_search:
        busca = st.text_input("🔍 Buscar filme:", placeholder="Digite o nome do filme...")
    
    with col_sort:
        ordenacao = st.selectbox(
            "Ordenar por:",
            ["Nome A-Z", "Data Recente", "Maior Receita", "Maior ROI", "Melhor Nota"]
        )
    
    # Aplicar busca
    if busca:
        df_display = df_filtrado[
            df_filtrado["nome_pt"].str.contains(busca, case=False, na=False) |
            df_filtrado["genero_pt"].str.contains(busca, case=False, na=False)
        ]
    else:
        df_display = df_filtrado.copy()
    
    # Aplicar ordenação
    ordenacao_map = {
        "Nome A-Z": "nome_pt",
        "Data Recente": "date_x", 
        "Maior Receita": "revenue",
        "Maior ROI": "roi",
        "Melhor Nota": "score"
    }
    
    if ordenacao in ordenacao_map:
        coluna = ordenacao_map[ordenacao]
        ascending = ordenacao == "Nome A-Z"
        df_display = df_display.sort_values(coluna, ascending=ascending)
    
    # Colunas para exibição
    colunas_exibicao = ['nome_pt', 'genero_pt', 'data_completa_pt', 'score', 'revenue', 'budget_x', 'roi', 'categoria_receita']
    colunas_disponiveis = [col for col in colunas_exibicao if col in df_display.columns]
    
    if not df_display.empty:
        df_exibicao = df_display[colunas_disponiveis].copy()
        
        # Formatação
        if 'revenue' in df_exibicao.columns:
            df_exibicao['revenue'] = df_exibicao['revenue'].apply(lambda x: f"${x:,.0f}")
        if 'budget_x' in df_exibicao.columns:
            df_exibicao['budget_x'] = df_exibicao['budget_x'].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
        if 'roi' in df_exibicao.columns:
            df_exibicao['roi'] = df_exibicao['roi'].apply(lambda x: f"{x:.1f}%")
        if 'score' in df_exibicao.columns:
            df_exibicao['score'] = df_exibicao['score'].apply(lambda x: f"{x:.1f}")
        
        # Renomear colunas
        df_exibicao = df_exibicao.rename(columns={
            'nome_pt': '🎬 Filme',
            'genero_pt': '🎭 Gênero', 
            'data_completa_pt': '📅 Data',
            'score': '⭐ Nota',
            'revenue': '💰 Receita',
            'budget_x': '💸 Orçamento',
            'roi': '📈 ROI',
            'categoria_receita': '🏆 Categoria'
        })
        
        st.dataframe(df_exibicao, use_container_width=True, height=600)
        st.markdown(f"**📊 Mostrando {len(df_display)} de {len(df_filtrado)} filmes**")
    else:
        st.warning("Nenhum filme encontrado com os critérios selecionados.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>🎬 <strong>CineAnalytics Pro</strong> - Adaptado do Google Colab</p>
    <p>📊 Análise Exploratória | 📈 Correlações | 📅 Análise Temporal | 💡 Insights Avançados</p>
    <p>Desenvolvido com base na análise do notebook colaborativo</p>
</div>
""", unsafe_allow_html=True)
