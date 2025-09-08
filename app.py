import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set a title for the app
st.set_page_config(page_title="Análise de Dados de Veículos", layout="wide")
st.title("🚙 Análise de Dados de Veículos")
st.markdown("---")
st.write("Este aplicativo web interativo apresenta uma análise do conjunto de dados de veículos, baseado no notebook do Google Colab.")

# Function to load and preprocess the data
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

# --- Display Dataset Information ---
st.header("Visão Geral dos Dados")
st.write(f"O conjunto de dados contém **{df.shape[0]}** linhas e **{df.shape[1]}** colunas.")
st.dataframe(df.head())

st.header("Estatísticas Descritivas")
st.dataframe(df.describe().T.astype(int))

st.markdown("---")

# --- Interactive Visualizations ---
st.header("Visualizações Interativas")

# A visualization from the notebook: Fuel Type Distribution
st.subheader("Distribuição do Tipo de Combustível")
fuel_counts = df['fuel_type'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(fuel_counts, labels=fuel_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
ax1.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig1)

st.markdown("---")

# A visualization from the notebook: City MPG by Manufacturer
st.subheader("MPG na Cidade por Fabricante")
# Group by make and calculate average city_mpg
avg_city_mpg = df.groupby('make')['city_mpg'].mean().sort_values(ascending=False).reset_index()
fig2 = px.bar(avg_city_mpg, 
              x='make', 
              y='city_mpg', 
              title='Média de MPG na Cidade por Fabricante',
              labels={'make': 'Fabricante', 'city_mpg': 'Média de MPG na Cidade'})
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# New visualization based on the analysis: Horsepower vs. Price
st.subheader("Relação entre Cavalos de Potência e Preço")
# Create a scatter plot with price on the y-axis and horsepower on the x-axis
fig3 = px.scatter(df, x='horsepower', y='price', color='body_style',
                  hover_data=['make', 'fuel_type'],
                  title='Preço vs. Cavalos de Potência',
                  labels={'horsepower': 'Cavalos de Potência', 'price': 'Preço'})
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# A filterable section
st.header("Filtre os Dados")
body_styles = sorted(df['body_style'].unique())
selected_body_style = st.selectbox("Selecione o Estilo da Carroceria:", body_styles)

filtered_df = df[df['body_style'] == selected_body_style]

st.subheader(f"Dados para Carrocerias do Tipo '{selected_body_style}'")
st.dataframe(filtered_df[['make', 'price', 'horsepower', 'engine_size']].reset_index(drop=True))

st.write(f"Há **{filtered_df.shape[0]}** veículos com este estilo de carroceria no conjunto de dados.")
