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
    page_title="Dashboard de Análise de Carros",
    page_icon="🚗",
    layout="wide",
)

# --- Carregamento e Pré-processamento dos Dados ---
@st.cache_data
def load_data():
    # URL do arquivo CSV de carros no GitHub (corrigido para uma URL estável)
    url = 'https://raw.githubusercontent.com/luccasfsilva/projetopy/main/auto-mpg.csv'
    df = pd.read_csv(url, na_values=['?'])  # Tratar '?' como NaN
    
    # Renomear colunas para facilitar o uso
    df.columns = df.columns.str.lower().str.replace('-', '_').str.replace(' ', '_')

    # Tratar valores ausentes na coluna 'horsepower'
    df = df.dropna(subset=['horsepower'])
    
    # Converter a coluna 'horsepower' para o tipo numérico adequado
    df['horsepower'] = pd.to_numeric(df['horsepower'])

    return df

# Carregar os dados
df = load_data()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro por Cilindros
cilindros_disponiveis = sorted(df['cylinders'].unique())
cilindros_selecionados = st.sidebar.multiselect("Cilindros", cilindros_disponiveis, default=cilindros_disponiveis)

# Filtro por Ano do Modelo
anos_modelo_disponiveis = sorted(df['model_year'].unique())
anos_modelo_selecionados = st.sidebar.multiselect("Ano do Modelo", anos_modelo_disponiveis, default=anos_modelo_disponiveis)

# Filtro por Origem
origens_disponiveis = sorted(df['origin'].unique())
origens_selecionadas = st.sidebar.multiselect("Origem", origens_disponiveis, default=origens_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['cylinders'].isin(cilindros_selecionados)) &
    (df['model_year'].isin(anos_modelo_selecionados)) &
    (df['origin'].isin(origens_selecionadas))
]

# --- Conteúdo Principal ---
st.title("🚗 Dashboard de Análise de Carros")
st.markdown("Explore os dados de carros. Use os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

if not df_filtrado.empty:
    media_mpg = df_filtrado['mpg'].mean()
    media_hp = df_filtrado['horsepower'].mean()
    media_peso = df_filtrado['weight'].mean()
    total_registros = df_filtrado.shape[0]
else:
    media_mpg, media_hp, media_peso, total_registros = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Média de MPG", f"{media_mpg:.2f}")
col2.metric("Média de Cavalos", f"{media_hp:.2f} HP")
col3.metric("Média de Peso", f"{media_peso:,.0f} lbs")
col4.metric("Total de Registros", f"{total_registros:,}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

if not df_filtrado.empty:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # Gráfico: MPG vs. Cavalos de Potência
        fig1 = px.scatter(df_filtrado, 
                          x='horsepower', 
                          y='mpg', 
                          color='cylinders',
                          hover_data=['car_name', 'origin'],
                          title='MPG vs. Cavalos de Potência por Cilindros',
                          labels={'horsepower': 'Cavalos de Potência', 'mpg': 'Milhas por Galão (MPG)'})
        fig1.update_layout(title_x=0.1)
        st.plotly_chart(fig1, use_container_width=True)

    with col_graf2:
        # Gráfico: Distribuição de MPG por Origem
        fig2 = px.box(
            df_filtrado, 
            x='origin', 
            y='mpg',
            color='origin',
            title="Distribuição de MPG por Origem",
            labels={'origin': 'Origem', 'mpg': 'Milhas por Galão (MPG)'}
        )
        fig2.update_layout(title_x=0.1)
        st.plotly_chart(fig2, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        # Gráfico: Média de Cavalos de Potência por Origem
        hp_by_origin = df_filtrado.groupby('origin')['horsepower'].mean().reset_index()
        fig3 = px.bar(
            hp_by_origin,
            x='origin',
            y='horsepower',
            color='origin',
            title='Média de Cavalos de Potência por Origem',
            labels={'origin': 'Origem', 'horsepower': 'Média de Cavalos'}
        )
        fig3.update_layout(title_x=0.1)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_graf4:
        # Gráfico: Contagem de Carros por Ano do Modelo
        count_by_year = df_filtrado['model_year'].value_counts().sort_index().reset_index()
        count_by_year.columns = ['model_year', 'count']
        fig4 = px.line(
            count_by_year,
            x='model_year',
            y='count',
            markers=True,
            title='Contagem de Carros por Ano do Modelo',
            labels={'model_year': 'Ano do Modelo', 'count': 'Número de Carros'}
        )
        fig4.update_layout(title_x=0.1)
        st.plotly_chart(fig4, use_container_width=True)

else:
    st.warning("Nenhum dado para exibir com os filtros selecionados.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
