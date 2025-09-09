import streamlit as st
import pandas as pd
import plotly.express as px

# Para rodar este app, você precisa ter as bibliotecas instaladas.
# Instale-as no seu ambiente virtual com os seguintes comandos:
# pip install streamlit
# pip install pandas
# pip install plotly

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise de Filmes",
    page_icon="🎬",
    layout="wide",
)

# --- Carregamento e Pré-processamento dos Dados ---
@st.cache_data
def load_data():
    # URL para o arquivo CSV de filmes no GitHub
    url = 'https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv'
    df = pd.read_csv(url)
    
    # Renomear colunas para facilitar o uso
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

    # Tratar valores ausentes
    df = df.dropna(subset=['genre', 'director', 'year', 'avg_vote', 'country', 'votes'])

    # Converter colunas para o tipo numérico adequado
    df['avg_vote'] = pd.to_numeric(df['avg_vote'], errors='coerce')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce')

    # Filtrar dados inválidos
    df = df[df['year'] > 1900]

    return df

# Carregar os dados
df = load_data()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro por Gênero
generos_disponiveis = sorted(df['genre'].unique())
generos_selecionados = st.sidebar.multiselect("Gênero", generos_disponiveis, default=generos_disponiveis)

# Filtro por Diretor
diretores_disponiveis = sorted(df['director'].unique())
diretores_selecionados = st.sidebar.multiselect("Diretor", diretores_disponiveis, default=diretores_disponiveis[:10])

# Filtro por Ano
anos_disponiveis = sorted(df['year'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['genre'].isin(generos_selecionados)) &
    (df['director'].isin(diretores_selecionados)) &
    (df['year'].isin(anos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎬 Dashboard de Análise de Filmes IMDb")
st.markdown("Explore os dados de filmes. Use os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

if not df_filtrado.empty:
    media_avaliacao = df_filtrado['avg_vote'].mean()
    media_votos = df_filtrado['votes'].mean()
    total_filmes = df_filtrado.shape[0]
    genero_mais_comum = df_filtrado['genre'].mode()[0]
else:
    media_avaliacao, media_votos, total_filmes, genero_mais_comum = 0, 0, 0, "Nenhum"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Média de Avaliação", f"{media_avaliacao:.2f}")
col2.metric("Média de Votos", f"{media_votos:,.0f}")
col3.metric("Total de Filmes", f"{total_filmes:,}")
col4.metric("Gênero Mais Comum", genero_mais_comum)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

if not df_filtrado.empty:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # Gráfico: Top 10 Filmes por Avaliação
        top_filmes = df_filtrado.sort_values('avg_vote', ascending=False).head(10)
        fig1 = px.bar(top_filmes, 
                      x='avg_vote', 
                      y='title',
                      orientation='h',
                      title='Top 10 Filmes por Avaliação',
                      labels={'avg_vote': 'Avaliação Média', 'title': ''})
        fig1.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

    with col_graf2:
        # Gráfico: Distribuição das Avaliações
        fig2 = px.histogram(
            df_filtrado, 
            x='avg_vote', 
            nbins=20,
            title="Distribuição das Avaliações",
            labels={'avg_vote': 'Faixa de Avaliação', 'count': 'Contagem'}
        )
        fig2.update_layout(title_x=0.1)
        st.plotly_chart(fig2, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        # Gráfico: Avaliação vs. Votos
        fig3 = px.scatter(df_filtrado, 
                          x='votes', 
                          y='avg_vote', 
                          color='genre',
                          hover_data=['title', 'director'],
                          title='Avaliação vs. Votos por Gênero',
                          labels={'votes': 'Total de Votos', 'avg_vote': 'Avaliação Média'})
        fig3.update_layout(title_x=0.1)
        st.plotly_chart(fig3, use_container_width=True)

    with col_graf4:
        # Gráfico: Média de Avaliação por Gênero (top 10)
        genre_avg_rating = df_filtrado.groupby('genre')['avg_vote'].mean().sort_values(ascending=False).reset_index()
        fig4 = px.bar(
            genre_avg_rating.head(10),
            x='avg_vote',
            y='genre',
            orientation='h',
            title='Média de Avaliação por Gênero (Top 10)',
            labels={'genre': 'Gênero', 'avg_vote': 'Avaliação Média'}
        )
        fig4.update_layout(title_x=0.1)
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir com os filtros selecionados.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
