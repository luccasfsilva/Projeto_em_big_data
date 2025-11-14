# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="CineAnalytics",
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
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2c3e50;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: #2c3e50;
        font-weight: bold;
    }
    .info-box {
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CARREGAR DADOS
# =========================
@st.cache_data
def carregar_dados():
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
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
    """Traduz o nome do filme para português"""
    if pd.isna(nome_original):
        return nome_original
    return TRADUCOES_FILMES.get(nome_original, nome_original)

# =========================
# BARRA LATERAL MODERNIZADA
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
        value=(min(anos_disponiveis), max(anos_disponiveis)),
        help="Filtre os filmes por ano de lançamento"
    )
    
    st.markdown("---")
    
    # Filtro de notas
    st.markdown("#### ⭐ Filtro por Nota")
    score_min, score_max = st.slider(
        "Selecione a faixa de notas:",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1,
        help="Filtre os filmes pela nota no IMDb"
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
        format="$%.0f",
        help="Filtre os filmes pela receita de bilheteria"
    )
    
    st.markdown("---")
    
    # Informações sobre o dataset
    with st.expander("ℹ️ Sobre os Dados"):
        st.markdown("""
        **Fonte dos dados:** IMDb Movies Dataset
        
        **Conteúdo:**
        - Informações sobre filmes e suas bilheterias
        - Notas de avaliação
        - Anos de lançamento
        - Gêneros e idiomas
        
        **Atualização:** Dados carregados automaticamente
        """)

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
# CABEÇALHO E MÉTRICAS PRINCIPAIS
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Interativo de Análise de Filmes e Bilheterias</p>', unsafe_allow_html=True)

# Cartões de métricas principais
if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Receita Total", f"${receita_total:,.0f}", help="Soma total da receita de todos os filmes filtrados")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Receita Média", f"${receita_media:,.0f}", help="Receita média por filme")
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⭐ Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—", 
                 help="Nota média dos filmes no IMDb")
        st.markdown('</div>', unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎭 Total de Filmes", f"{total_filmes:,}", help="Número total de filmes que correspondem aos filtros")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# NAVEGAÇÃO POR ABAS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Análise Geral", "🎭 Top Filmes", "📈 Tendências", "🔍 Base de Dados"])

with tab1:
    st.markdown('<div class="section-header">📊 Visão Geral do Mercado Cinematográfico</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dispersão - Nota vs Receita
        fig_scatter = px.scatter(
            df_filtrado,
            x="score",
            y="revenue",
            title="🎯 Relação entre Nota e Receita",
            labels={"score": "Nota (IMDb)", "revenue": "Receita (USD)"},
            color="score",
            size="revenue",
            hover_data=["names", "ano"],
            color_continuous_scale="viridis"
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Distribuição de idiomas
        contagem_idiomas = df_filtrado["orig_lang"].value_counts().head(8).reset_index()
        contagem_idiomas.columns = ["Idioma Original", "Quantidade de Filmes"]
        fig_pie = px.pie(
            contagem_idiomas,
            values="Quantidade de Filmes",
            names="Idioma Original",
            title="🌎 Distribuição por Idioma Original",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Evolução temporal da receita
        receita_anual = df_filtrado.groupby("ano")["revenue"].sum().reset_index()
        fig_area = px.area(
            receita_anual,
            x="ano",
            y="revenue",
            title="📈 Evolução da Receita Anual",
            labels={"ano": "Ano", "revenue": "Receita Total (USD)"}
        )
        fig_area.update_traces(
            line=dict(color="#4ECDC4", width=3), 
            fillcolor="rgba(78,205,196,0.2)"
        )
        fig_area.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_area, use_container_width=True)
        
        # Distribuição de notas
        fig_hist = px.histogram(
            df_filtrado,
            x="score",
            title="📊 Distribuição de Notas dos Filmes",
            labels={"score": "Nota", "count": "Número de Filmes"},
            nbins=20,
            color_discrete_sequence=['#FF6B6B']
        )
        fig_hist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">🎭 Ranking dos Filmes Mais Bem Sucedidos</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        top_n = st.slider("Número de filmes no TOP:", 5, 25, 10, key="top_slider")
        ordenar_por = st.selectbox("Ordenar por:", ["Receita", "Nota"], index=0, key="ordenar_por")
    
    with col2:
        if ordenar_por == "Receita":
            df_top = df_filtrado.sort_values(by="revenue", ascending=False).head(top_n)
            titulo = f"🏆 Top {top_n} Filmes por Receita"
            eixo_y = "revenue"
            label_y = "Receita (USD)"
        else:
            df_top = df_filtrado.sort_values(by="score", ascending=False).head(top_n)
            titulo = f"🏆 Top {top_n} Filmes por Nota"
            eixo_y = "score"
            label_y = "Nota"
        
        fig_bar = px.bar(
            df_top,
            x="names",
            y=eixo_y,
            title=titulo,
            labels={"names": "Filme", eixo_y: label_y},
            color=eixo_y,
            color_continuous_scale="viridis",
            hover_data=["score", "revenue", "ano"] if ordenar_por == "Nota" else ["score", "ano"]
        )
        fig_bar.update_layout(
            xaxis_tickangle=-45, 
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tabela dos top filmes
    st.markdown("#### 📋 Detalhes dos Filmes em Destaque")
    df_display_top = df_top[["names", "score", "revenue", "ano", "orig_lang"]].copy()
    df_display_top.columns = ["Filme", "Nota", "Receita (USD)", "Ano", "Idioma"]
    df_display_top["Receita (USD)"] = df_display_top["Receita (USD)"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(df_display_top, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">📈 Análise de Tendências e Padrões</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Média de notas por ano
        media_notas_anual = df_filtrado.groupby("ano")["score"].mean().reset_index()
        fig_line = px.line(
            media_notas_anual,
            x="ano",
            y="score",
            title="📈 Evolução da Nota Média por Ano",
            labels={"ano": "Ano", "score": "Nota Média"},
            markers=True
        )
        fig_line.update_traces(line=dict(color="#FF6B6B", width=3))
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        # Contagem de filmes por ano
        contagem_filmes_anual = df_filtrado.groupby("ano").size().reset_index(name="count")
        fig_bar_count = px.bar(
            contagem_filmes_anual,
            x="ano",
            y="count",
            title="🎬 Número de Filmes por Ano",
            labels={"ano": "Ano", "count": "Número de Filmes"},
            color="count",
            color_continuous_scale="blues"
        )
        fig_bar_count.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_bar_count, use_container_width=True)
    
    # Heatmap de correlação
    st.markdown("#### 🔍 Mapa de Correlações")
    numeric_cols = df_filtrado.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        corr_matrix = df_filtrado[numeric_cols].corr()
        fig_heatmap = px.imshow(
            corr_matrix,
            title="Mapa de Calor de Correlações entre Variáveis Numéricas",
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )
        fig_heatmap.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">🔍 Explorar Base de Dados Completa</div>', unsafe_allow_html=True)
    
    # Informações sobre o dataset
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("Total de Filmes no Dataset", f"{len(df):,}")
    
    with col_info2:
        st.metric("Período Abrangido", f"{df['ano'].min()} - {df['ano'].max()}")
    
    with col_info3:
        st.metric("Idiomas Diferentes", f"{df['orig_lang'].nunique()}")
    
    # Filtros de busca
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        search_term = st.text_input("🔍 Buscar filme:", placeholder="Digite o nome do filme...")
    with col_f2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "Ano de Lançamento", "Nome do Filme"],
            index=0
        )
    with col_f3:
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
        "genre": "Gênero"
    })

    # Formata a data no padrão brasileiro (dd/mm/aaaa)
    if "Data de Lançamento" in df_display.columns:
        df_display["Data de Lançamento"] = pd.to_datetime(
            df_display["Data de Lançamento"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    # Formata a receita como moeda (mantém como número para ordenação)
    df_display["Receita_Original"] = df_display["Receita"]
    df_display["Receita"] = df_display["Receita"].apply(
        lambda x: f"${x:,.0f}" if pd.notnull(x) and x > 0 else "N/A"
    )

    # Formata a pontuação (mantém como número para ordenação)
    df_display["Pontuação_Original"] = df_display["Pontuação"]
    df_display["Pontuação"] = df_display["Pontuação"].apply(
        lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A"
    )

    # Filtro de busca
    if search_term:
        df_display = df_display[
            df_display["Nome do Filme"].str.contains(search_term, case=False, na=False) |
            df_display["Gênero"].str.contains(search_term, case=False, na=False) |
            df_display["País de Origem"].str.contains(search_term, case=False, na=False)
        ]

    # Ordenação
    sort_map = {
        "Receita": "Receita_Original",
        "Pontuação": "Pontuação_Original", 
        "Ano de Lançamento": "Ano de Lançamento",
        "Nome do Filme": "Nome do Filme"
    }
    
    if sort_by in sort_map and sort_map[sort_by] in df_display.columns:
        ascending = sort_by == "Nome do Filme"
        df_display = df_display.sort_values(by=sort_map[sort_by], ascending=ascending)

    # Colunas a exibir
    colunas_para_mostrar = [
        "Nome do Filme", "Gênero", "Idioma Original", "País de Origem",
        "Pontuação", "Receita", "Ano de Lançamento", "Data de Lançamento"
    ]

    # Sistema de paginação
    total_resultados = len(df_display)
    if total_resultados > 0:
        total_paginas = (total_resultados + resultados_por_pagina - 1) // resultados_por_pagina
        pagina_atual = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
        
        inicio = (pagina_atual - 1) * resultados_por_pagina
        fim = inicio + resultados_por_pagina
        
        df_paginado = df_display.iloc[inicio:fim]
        
        # Exibe informações da paginação
        st.caption(f"Mostrando {inicio + 1}-{min(fim, total_resultados)} de {total_resultados} resultados")
        
        # Exibe a tabela formatada
        st.dataframe(
            df_paginado[colunas_para_mostrar],
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Botão para exportar dados
        col_export1, col_export2 = st.columns([3, 1])
        with col_export2:
            if st.button("📥 Exportar Dados para CSV", use_container_width=True):
                csv = df_display[colunas_para_mostrar].to_csv(index=False)
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name="filmes_traduzidos.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.warning("🎭 Nenhum filme encontrado com os filtros aplicados.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>"
    f"📊 Dashboard CineAnalytics • Desenvolvido com Streamlit • "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    f"</div>",
    unsafe_allow_html=True
)
