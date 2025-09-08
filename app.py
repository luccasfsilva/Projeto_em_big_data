import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise de Veículos",
    page_icon="🚙",
    layout="wide",
)

# --- Carregamento e Pré-processamento dos Dados ---
@st.cache_data
def load_data():
    # URL to the raw CSV file on GitHub (from the Colab notebook)
    url = 'https://raw.githubusercontent.com/albuquerque22/Colab-Notebooks/main/Automobile.csv'
    df = pd.read_csv(url)

    # Clean up column names
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace('-', '_')
    df.columns = df.columns.str.lower()

    # Drop columns not needed for this analysis
    df = df.drop(columns=['unnamed_0', 'normalized_losses'])

    # Convert object columns to numeric where appropriate
    for col in ['bore', 'stroke', 'horsepower', 'peak_rpm', 'price']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with any NaN values for a cleaner dataset
    df = df.dropna()

    return df

# Load the data
df = load_data()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro por Fabricante
fabricantes_disponiveis = sorted(df['make'].unique())
fabricantes_selecionados = st.sidebar.multiselect("Fabricante", fabricantes_disponiveis, default=fabricantes_disponiveis)

# Filtro por Tipo de Combustível
tipos_combustivel_disponiveis = sorted(df['fuel_type'].unique())
tipos_combustivel_selecionados = st.sidebar.multiselect("Tipo de Combustível", tipos_combustivel_disponiveis, default=tipos_combustivel_disponiveis)

# Filtro por Estilo de Carroceria
estilos_carroceria_disponiveis = sorted(df['body_style'].unique())
estilos_carroceria_selecionados = st.sidebar.multiselect("Estilo de Carroceria", estilos_carroceria_disponiveis, default=estilos_carroceria_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['make'].isin(fabricantes_selecionados)) &
    (df['fuel_type'].isin(tipos_combustivel_selecionados)) &
    (df['body_style'].isin(estilos_carroceria_selecionados))
]

# --- Conteúdo Principal ---
st.title("🚙 Dashboard de Análise de Veículos")
st.markdown("Explore os dados de veículos. Use os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

if not df_filtrado.empty:
    preco_medio = df_filtrado['price'].mean()
    preco_maximo = df_filtrado['price'].max()
    media_hp = df_filtrado['horsepower'].mean()
    total_registros = df_filtrado.shape[0]
else:
    preco_medio, preco_maximo, media_hp, total_registros = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço médio (USD)", f"${preco_medio:,.0f}")
col2.metric("Preço máximo (USD)", f"${preco_maximo:,.0f}")
col3.metric("Média de Cavalos de Potência", f"{media_hp:,.0f} HP")
col4.metric("Total de registros", f"{total_registros:,}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

if not df_filtrado.empty:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # Gráfico: MPG na Cidade por Fabricante (top 10)
        avg_city_mpg = df_filtrado.groupby('make')['city_mpg'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        fig1 = px.bar(avg_city_mpg, 
                      x='city_mpg', 
                      y='make', 
                      orientation='h',
                      title='Média de MPG na Cidade por Fabricante (Top 10)',
                      labels={'make': 'Fabricante', 'city_mpg': 'Média de MPG na Cidade'})
        fig1.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

    with col_graf2:
        # Gráfico: Distribuição de Preços por Tipo de Combustível
        fig2 = px.histogram(
            df_filtrado, 
            x='price', 
            color='fuel_type', 
            nbins=30,
            title="Distribuição de Preços por Tipo de Combustível",
            labels={'price': 'Faixa de Preço (USD)', 'count': 'Contagem'}
        )
        fig2.update_layout(title_x=0.1)
        st.plotly_chart(fig2, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        # Gráfico: Relação entre Cavalos de Potência e Preço
        fig3 = px.scatter(df_filtrado, 
                          x='horsepower', 
                          y='price', 
                          color='body_style',
                          hover_data=['make'],
                          title='Preço vs. Cavalos de Potência',
                          labels={'horsepower': 'Cavalos de Potência', 'price': 'Preço'})
        fig3.update_layout(title_x=0.1)
        st.plotly_chart(fig3, use_container_width=True)

    with col_graf4:
        # Gráfico: Proporção de Veículos por Estilo de Carroceria
        body_style_counts = df_filtrado['body_style'].value_counts().reset_index()
        body_style_counts.columns = ['estilo', 'quantidade']
        fig4 = px.pie(
            body_style_counts,
            names='estilo',
            values='quantidade',
            title='Proporção por Estilo de Carroceria',
            hole=0.5
        )
        fig4.update_traces(textinfo='percent+label')
        fig4.update_layout(title_x=0.1)
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir com os filtros selecionados.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
