# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Filmes",
    page_icon="🎬",
    layout="wide",
)

# --- Carregamento dos dados ---
# Substitua pelo link do seu CSV no GitHub ou outro host
df = pd.read_csv("https://raw.githubusercontent.com/luccasfsilva/projetopy/refs/heads/main/imdb_movies.csv")

# --- Barra Lateral (Filtro por Gênero) ---
st.sidebar.header("🎭 Filtro")
generos_disponiveis = sorted(df['genre'].dropna().unique())
generos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) gênero(s):",
    generos_disponiveis,
    default=generos_disponiveis
)

# --- Filtragem do DataFrame ---
df_filtrado = df[df['genre'].isin(generos_selecionados)]

# --- Título ---
st.title("🎬 Dashboard de Filmes")
st.markdown("Explore os filmes com base nos gêneros selecionados.")

st.markdown("---")

# --- Gráficos ---
st.subheader("📊 Gráficos")

col1, col2 = st.columns(2)

with col1:
    if not df_filtrado.empty:
        graf1 = px.histogram(
            df_filtrado,
            x="rating",
            nbins=20,
            title="Distribuição das Avaliações",
            labels={"rating": "Nota"}
        )
        st.plotly_chart(graf1, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir neste gráfico.")

with col2:
    if not df_filtrado.empty:
        graf2 = px.histogram(
            df_filtrado,
            x="year",
            title="Quantidade de Filmes por Ano",
            labels={"year": "Ano"}
        )
        st.plotly_chart(graf2, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir neste gráfico.")

col3, col4 = st.columns(2)

with col3:
    if not df_filtrado.empty:
        graf3 = px.bar(
            df_filtrado.groupby("genre")["rating"].mean().reset_index(),
            x="genre",
            y="rating",
            title="Média de Avaliações por Gênero",
            labels={"rating": "Média das Notas", "genre": "Gênero"}
        )
        st.plotly_chart(graf3, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir neste gráfico.")

with col4:
    if not df_filtrado.empty:
        graf4 = px.box(
            df_filtrado,
            x="genre",
            y="rating",
            title="Distribuição das Notas por Gênero",
            labels={"genre": "Gênero", "rating": "Nota"}
        )
        st.plotly_chart(graf4, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir neste gráfico.")

st.markdown("---")

# --- Tabela de Dados ---
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado)
