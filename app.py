# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Dinâmico do Projeto",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
# Substitua o caminho abaixo pelo dataset do seu projeto
# Exemplo: um CSV exportado do seu Colab
df = pd.read_csv("seus_dados.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Ajuste os filtros de acordo com as colunas que você tiver no dataset
colunas = df.columns.tolist()

# Exemplo de filtros:
if "ano" in colunas:
    anos_disponiveis = sorted(df['ano'].dropna().unique())
    anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)
else:
    anos_selecionados = df.index

if "categoria" in colunas:
    categorias_disp = sorted(df['categoria'].dropna().unique())
    categorias_sel = st.sidebar.multiselect("Categoria", categorias_disp, default=categorias_disp)
else:
    categorias_sel = df.index

# --- Filtragem do DataFrame ---
df_filtrado = df.copy()

if "ano" in colunas:
    df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos_selecionados)]

if "categoria" in colunas:
    df_filtrado = df_filtrado[df_filtrado["categoria"].isin(categorias_sel)]

# --- Conteúdo Principal ---
st.title("📊 Dashboard Dinâmico do Projeto")
st.markdown("Explore os dados com base nos filtros à esquerda.")

# --- Métricas Principais ---
st.subheader("Métricas gerais")

if not df_filtrado.empty and "valor" in colunas:
    media_valor = df_filtrado["valor"].mean()
    max_valor = df_filtrado["valor"].max()
    min_valor = df_filtrado["valor"].min()
    total_registros = df_filtrado.shape[0]
else:
    media_valor, max_valor, min_valor, total_registros = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Média", f"{media_valor:,.2f}")
col2.metric("Máximo", f"{max_valor:,.2f}")
col3.metric("Mínimo", f"{min_valor:,.2f}")
col4.metric("Total Registros", f"{total_registros:,}")

st.markdown("---")

# --- Gráficos ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty and "categoria" in colunas and "valor" in colunas:
        graf1 = px.bar(df_filtrado, x="categoria", y="valor",
                       title="Valores por Categoria", color="categoria")
        st.plotly_chart(graf1, use_container_width=True)
    else:
        st.warning("Adicione colunas 'categoria' e 'valor' para este gráfico.")

with col_graf2:
    if not df_filtrado.empty and "valor" in colunas:
        graf2 = px.histogram(df_filtrado, x="valor", nbins=30,
                             title="Distribuição dos Valores")
        st.plotly_chart(graf2, use_container_width=True)
    else:
        st.warning("Adicione coluna 'valor' para este gráfico.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty and "tipo" in colunas:
        graf3 = px.pie(df_filtrado, names="tipo", title="Proporção por Tipo", hole=0.5)
        st.plotly_chart(graf3, use_container_width=True)
    else:
        st.warning("Adicione coluna 'tipo' para este gráfico.")

with col_graf4:
    if not df_filtrado.empty and "pais" in colunas and "valor" in colunas:
        graf4 = px.choropleth(df_filtrado, locations="pais", color="valor",
                              color_continuous_scale="rdylgn",
                              title="Valores médios por país")
        st.plotly_chart(graf4, use_container_width=True)
    else:
        st.warning("Adicione colunas 'pais' e 'valor' para este gráfico.")

# --- Tabela de Dados ---
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado)
