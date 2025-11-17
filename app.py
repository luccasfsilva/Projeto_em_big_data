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
# DICIONÁRIO DE TRADUÇÃO DOS FILMES
# =========================
# ATENÇÃO: PREENCHA O DICIONÁRIO COMPLETO AQUI.
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

# =========================
# FUNÇÕES DE TRADUÇÃO OTIMIZADA
# =========================
@st.cache_data(show_spinner=False)
def traduzir_dinamico(texto):
    """Tenta traduzir um texto e retorna o original em caso de falha."""
    if not texto or pd.isna(texto):
        return texto
    try:
        # Tenta traduzir de inglês ('en') para português ('pt')
        return translator.translate(texto, src='en', dest='pt').text
    except Exception:
        # Em caso de falha (limite de API, conexão), retorna o texto original
        return texto

def traduzir_nome_filme_avancado(nome_original):
    """Usa o dicionário estático e, se falhar, tenta a tradução dinâmica."""
    if pd.isna(nome_original):
        return nome_original
    
    # 1. Tenta o dicionário estático (mais rápido)
    traduzido = TRADUCOES_FILMES.get(nome_original)
    
    if traduzido:
        return traduzido
    
    # 2. Se não estiver no dicionário, tenta a tradução dinâmica (com cache)
    return traduzir_dinamico(nome_original)

# =========================
# CARREGAR E PREPROCESSAR DADOS
# =========================
@st.cache_data
def carregar_dados():
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

# APLICAR TRADUÇÃO AVANÇADA AQUI
df_filtrado = df_filtrado.copy()
df_filtrado["names"] = df_filtrado["names"].apply(traduzir_nome_filme_avancado)

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

with tab1:
    st.markdown('<div class="section-header">📊 Visão Geral do Mercado</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dispersão multivariado
        fig_scatter = px.scatter(
            df_filtrado,
            x="score",
            y="revenue",
            size="budget_x",
            color="success_category",
            title="🎯 Relação: Nota vs Receita vs Orçamento",
            labels={"score": "Nota IMDb", "revenue": "Receita", "budget_x": "Orçamento"},
            hover_data=["names", "ano", "roi"],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Distribuição de ROI
        fig_roi = px.histogram(
            df_filtrado,
            x="roi",
            nbins=50,
            title="📊 Distribuição de ROI (Return on Investment)",
            labels={"roi": "ROI (%)"},
            color_discrete_sequence=['#FFA726']
        )
        fig_roi.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Mapa de calor de correlações
        numeric_cols = df_filtrado.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df_filtrado[numeric_cols].corr()
            fig_heatmap = px.imshow(
                corr_matrix,
                title="🔥 Mapa de Correlações (Matriz Completa)",
                color_continuous_scale="RdBu_r",
                aspect="auto",
                text_auto=True
            )
            fig_heatmap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Evolução temporal múltipla
        evolucao_anual = df_filtrado.groupby('ano').agg({
            'revenue': 'mean',
            'score': 'mean',
            'roi': 'mean'
        }).reset_index()
        
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_anual['ano'], 
            y=evolucao_anual['revenue'],
            name='Receita Média',
            line=dict(color='#4ECDC4', width=3)
        ))
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_anual['ano'], 
            y=evolucao_anual['score'] * (evolucao_anual['revenue'].max() / max(evolucao_anual['score'].max(), 1)),
            name='Nota Média (escala ajustada)',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig_evolucao.update_layout(
            title="📈 Evolução Comparativa: Receita vs Nota",
            xaxis_title="Ano",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">🎭 Análise de Performance Detalhada</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top filmes por ROI
        st.markdown("#### 💰 Melhores Investimentos (ROI)")
        top_roi = df_filtrado.nlargest(10, 'roi')[['names', 'roi', 'revenue', 'budget_x']]
        if not top_roi.empty:
            top_roi = top_roi.copy()
            top_roi['ROI'] = top_roi['roi'].apply(lambda x: f"{x:.1f}%")
            top_roi['Receita'] = top_roi['revenue'].apply(lambda x: f"${x:,.0f}")
            top_roi['Orçamento'] = top_roi['budget_x'].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
            st.dataframe(top_roi[['names', 'ROI', 'Receita', 'Orçamento']].rename(
                columns={'names': 'Filme'}), use_container_width=True)
        else:
            st.info("Nenhum dado disponível para exibir")
    
    with col2:
        # Performance por categoria de sucesso
        st.markdown("#### 🏆 Distribuição por Categoria")
        success_dist = df_filtrado['success_category'].value_counts()
        if not success_dist.empty:
            fig_pie_success = px.pie(
                values=success_dist.values,
                names=success_dist.index,
                title="Distribuição de Categorias de Sucesso",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie_success, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para exibir")
    
    # Análise de eficiência
    st.markdown("#### ⚡ Análise de Eficiência: Receita vs Orçamento")
    if not df_filtrado.empty:
        fig_efficiency = px.scatter(
            df_filtrado,
            x="budget_x",
            y="revenue",
            color="success_category",
            size="score",
            title="Eficiência: Receita Gerada vs Orçamento Investido",
            labels={"budget_x": "Orçamento", "revenue": "Receita"},
            hover_data=["names", "roi"]
        )
        # Adicionar linha de referência (y = x)
        max_val = max(df_filtrado['budget_x'].max(), df_filtrado['revenue'].max())
        fig_efficiency.add_shape(
            type="line", line=dict(dash="dash", color="white"),
            x0=0, y0=0, x1=max_val, y1=max_val
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para exibir")

with tab3:
    st.markdown('<div class="section-header">📈 Análise de Tendências</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Simulador de Performance")
        
        with st.form("simulador_performance"):
            st.markdown("##### Parâmetros do Filme")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                orcamento_simulado = st.number_input("Orçamento (USD)", 
                                                     min_value=1000000, 
                                                     max_value=500000000,
                                                     value=100000000,
                                                     step=1000000)
                nota_esperada = st.slider("Nota IMDb Esperada", 0.0, 10.0, 7.0, 0.1)
            
            with col_s2:
                mes_lancamento = st.selectbox("Mês de Lançamento", 
                                              range(1, 13),
                                              format_func=lambda x: datetime(2020, x, 1).strftime('%B'))
                if 'genre' in df_filtrado.columns and not df_filtrado.empty:
                    generos_disponiveis = df_filtrado['genre'].value_counts().head(10).index.tolist()
                    categoria_genero = st.selectbox("Gênero Principal", generos_disponiveis)
                else:
                    categoria_genero = st.selectbox("Gênero Principal", ["Ação", "Drama", "Comédia"])
            
            submitted = st.form_submit_button("🎯 Calcular Previsão")
            
            if submitted and not df_filtrado.empty:
                # Cálculo simplificado baseado em médias históricas
                similar_movies = df_filtrado[
                    (df_filtrado['score'].between(nota_esperada-1, nota_esperada+1)) &
                    (df_filtrado['budget_x'].between(orcamento_simulado*0.5, orcamento_simulado*1.5))
                ]
                
                if not similar_movies.empty:
                    receita_estimada = similar_movies['revenue'].mean()
                    roi_estimado = (receita_estimada - orcamento_simulado) / orcamento_simulado * 100
                    
                    st.markdown(f'<div class="prediction-box">', unsafe_allow_html=True)
                    st.metric("💰 Receita Estimada", f"${receita_estimada:,.0f}")
                    st.metric("📈 ROI Estimado", f"{roi_estimado:.1f}%")
                    
                    # Determinar categoria
                    if not df_filtrado.empty:
                        limiar_blockbuster = df_filtrado['revenue'].quantile(0.8)
                        categoria = "Blockbuster" if receita_estimada > limiar_blockbuster else "Alto Sucesso"
                        st.metric("🎯 Categoria Prevista", categoria)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("Não há filmes similares suficientes para fazer uma previsão precisa.")
    
    with col2:
        st.markdown("#### 📈 Tendências Temporais")
        
        if not df_filtrado.empty:
            # Tendência de ROI ao longo do tempo
            roi_temporal = df_filtrado.groupby('ano')['roi'].mean().reset_index()
            fig_roi_trend = px.line(
                roi_temporal,
                x='ano',
                y='roi',
                title="📈 Evolução do ROI Médio Anual",
                markers=True
            )
            fig_roi_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_roi_trend, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">🔍 Insights e Recomendações</div>', unsafe_allow_html=True)
    
    # Insights automáticos
    st.markdown("#### 💡 Insights Automáticos")
    
    if not df_filtrado.empty:
        # Insight 1: Melhor custo-benefício
        df_roi_valido = df_filtrado[df_filtrado['roi'] > -100]
        if not df_roi_valido.empty:
            melhor_custo_beneficio = df_roi_valido.loc[df_roi_valido['roi'].idxmax()]
            pior_custo_beneficio = df_roi_valido.loc[df_roi_valido['roi'].idxmin()]
            
            col_i1, col_i2 = st.columns(2)
            
            with col_i1:
                st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
                st.markdown(f"##### 🏆 Melhor Investimento")
                st.markdown(f"**{melhor_custo_beneficio['names']}**")
                st.markdown(f"ROI: **{melhor_custo_beneficio['roi']:.1f}%**")
                st.markdown(f"Nota: **{melhor_custo_beneficio['score']:.1f}**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_i2:
                st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
                st.markdown(f"##### ⚠️ Investimento de Risco")
                st.markdown(f"**{pior_custo_beneficio['names']}**")
                st.markdown(f"ROI: **{pior_custo_beneficio['roi']:.1f}%**")
                st.markdown(f"Nota: **{pior_custo_beneficio['score']:.1f}**")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Análise de correlações interessantes
        st.markdown("#### 🔗 Correlações Interessantes")
        col_c1, col_c2, col_c3 = st.columns(3)
        
        with col_c1:
            corr_nota_receita = calcular_correlacao_personalizada(df_filtrado, 'score', 'revenue')
            st.metric("Nota vs Receita", f"{corr_nota_receita:.2f}")
        
        with col_c2:
            corr_orcamento_receita = calcular_correlacao_personalizada(df_filtrado, 'budget_x', 'revenue')
            st.metric("Orçamento vs Receita", f"{corr_orcamento_receita:.2f}")
        
        with col_c3:
            corr_nota_roi = calcular_correlacao_personalizada(df_filtrado, 'score', 'roi')
            st.metric("Nota vs ROI", f"{corr_nota_roi:.2f}")
    
    # Análise de sazonalidade
    st.markdown("#### 📅 Análise de Sazonalidade")
    if 'mes' in df_filtrado.columns and not df_filtrado.empty:
        sazonalidade = df_filtrado.groupby('mes').agg({
            'revenue': 'mean',
            'score': 'mean',
            'roi': 'mean'
        }).reset_index()
        
        fig_sazonal = go.Figure()
        fig_sazonal.add_trace(go.Bar(
            x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec'],
            y=sazonalidade['revenue'],
            name='Receita Média',
            marker_color='#4ECDC4'
        ))
        fig_sazonal.update_layout(
            title="Receita Média por Mês",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_sazonal, use_container_width=True)

with tab5:
    st.markdown('<div class="section-header">🏆 Benchmarking e Comparações</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Benchmark por gênero
        st.markdown("#### 🎭 Performance por Gênero")
        if 'genre' in df_filtrado.columns and not df_filtrado.empty:
            genre_benchmark = df_filtrado.groupby('genre').agg({
                'revenue': 'mean',
                'score': 'mean',
                'roi': 'mean',
                'names': 'count'
            }).round(2).nlargest(10, 'revenue')
            
            st.dataframe(genre_benchmark.rename(columns={
                'revenue': 'Receita Média',
                'score': 'Nota Média',
                'roi': 'ROI Médio',
                'names': 'Nº Filmes'
            }), use_container_width=True)
        else:
            st.info("Dados de gênero não disponíveis")
    
    with col2:
        # Comparação de décadas
        st.markdown("#### 📊 Evolução por Década")
        if not df_filtrado.empty:
            df_filtrado_copy = df_filtrado.copy()
            df_filtrado_copy['decada'] = (df_filtrado_copy['ano'] // 10) * 10
            decada_stats = df_filtrado_copy.groupby('decada').agg({
                'revenue': 'mean',
                'score': 'mean',
                'budget_x': 'mean'
            }).reset_index()
            
            fig_decada = px.line(
                decada_stats,
                x='decada',
                y=['revenue', 'budget_x'],
                title="Evolução da Receita e Orçamento por Década",
                markers=True
            )
            fig_decada.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_decada, use_container_width=True)
            
with tab6:
    st.markdown('<div class="section-header">📋 Base de Dados Completa</div>', unsafe_allow_html=True)
    if not df_filtrado.empty:
        st.dataframe(df_filtrado.style.format({
            "revenue": "${:,.0f}",
            "budget_x": "${:,.0f}",
            "score": "{:.2f}",
            "roi": "{:.1f}%"
        }), use_container_width=True)
    else:
        st.warning("O DataFrame está vazio. Por favor, ajuste os filtros.")
