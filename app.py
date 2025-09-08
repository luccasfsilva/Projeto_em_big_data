# Create the app.py file content
app_py_content = """
import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# Set the title of the web application
st.title('Análise de Dados de Filmes do IMDb')

# Load and process the data
# Read the CSV file from the GitHub repository
@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/luccasfsilva/projetopy/refs/heads/main/imdb_movies.csv")
    # Drop rows with missing values in 'genre' or 'crew'
    df_limpo = df.dropna(subset=['genre', 'crew']).copy()
    return df_limpo

df_limpo = load_data()

# Display the cleaned data
st.subheader("Dados Limpos dos Filmes")
st.dataframe(df_limpo)

# Add interactivity: Search and Filter
st.subheader("Pesquisar e Filtrar Filmes")

# Text input for searching by movie name
search_term = st.text_input("Pesquisar por nome do filme:")

# Get unique genres from the cleaned dataframe
all_genres = []
for genre_list in df_limpo['genre'].unique():
    if isinstance(genre_list, str):
        genres = [g.strip() for g in genre_list.split(',')]
        all_genres.extend(genres)
all_genres = sorted(list(set(all_genres)))

# Multiselect for filtering by genre
selected_genres = st.multiselect("Filtrar por gênero:", all_genres)

# Filter the DataFrame based on search term and selected genres
filtered_df = df_limpo.copy()

if search_term:
    filtered_df = filtered_df[filtered_df['names'].str.contains(search_term, case=False, na=False)]

if selected_genres:
    filtered_df = filtered_df[filtered_df['genre'].apply(lambda x: any(genre.strip() in x for genre in selected_genres))]

# Display the filtered data
st.subheader("Filmes Encontrados")
st.dataframe(filtered_df)

# Data Visualization Section
st.subheader("Visualizações de Dados")

# Plot 1: Distribution of Top 10 Genres
st.write("#### Distribuição dos Top 10 Gêneros de Filmes")
# Count the occurrences of each value in the 'genre' column
contagem_genre = df_limpo['genre'].value_counts().head(10)
fig_genre = px.bar(x=contagem_genre.index, y=contagem_genre.values, labels={'x':'Gênero', 'y':'Número de Filmes'}, title='Distribuição dos Top 10 Gêneros de Filmes')
st.plotly_chart(fig_genre)

# Plot 2: Top N Movies by Revenue
st.write("#### Top 10 Filmes por Receita")
top_n = 10
df_top_revenue = df_limpo.sort_values(by='revenue', ascending=False).head(top_n)
fig_revenue = px.bar(df_top_revenue,
                     x='names',
                     y='revenue',
                     title=f'Top {top_n} Filmes por Receita',
                     labels={'names': 'Filme', 'revenue': 'Receita'})
st.plotly_chart(fig_revenue)

# Plot 3: Total Revenue by Country (using Plotly choropleth map)
st.write("#### Receita Total por País")
# Calculate the total revenue for each country
total_revenue_by_country = df_limpo.groupby('country')['revenue'].sum().reset_index()

# Function to convert ISO-2 to ISO 3
def iso2_to_iso3(iso2):
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except AttributeError:
        return None

# Create a new column with ISO-3 codes for mapping
total_revenue_by_country['country_iso3'] = total_revenue_by_country['country'].apply(iso2_to_iso3)

# Remove rows where ISO-3 conversion failed
total_revenue_by_country = total_revenue_by_country.dropna(subset=['country_iso3'])

# Create a choropleth map of total revenue by country using ISO-3
fig_map = px.choropleth(total_revenue_by_country,
                        locations='country_iso3',
                        color='Total Revenue',
                        color_continuous_scale='Plasma',
                        title='Receita Total por País',
                        labels={'Total Revenue':'Receita Total','country_iso3':'País'})
st.plotly_chart(fig_map)

# Plot 4: Distribution of Movie Scores
st.write("#### Distribuição das Notas dos Filmes")
fig_score = px.histogram(df_limpo,
                        x='score',
                        nbins=20,
                        title='Distribuição das Notas dos Filmes',
                        labels={'score': 'Nota', 'count': 'Frequência'})
st.plotly_chart(fig_score)

# Plot 5: Count of Top 10 Original Languages
st.write("#### Contagem dos Top 10 Idiomas Originais dos Filmes")
contagem_idiomas = df_limpo['orig_lang'].value_counts().head(10).reset_index()
contagem_idiomas.columns = ['Idioma Original', 'Número de Filmes']
fig_lang = px.pie(contagem_idiomas,
                 values='Número de Filmes',
                 names='Idioma Original',
                 title='Contagem dos Top 10 Idiomas Originais dos Filmes',
                 hole=.3)
st.plotly_chart(fig_lang)
"""

# Write the content to app.py
with open("app.py", "w") as f:
    f.write(app_py_content)

# Create the requirements.txt file content
requirements_content = """
streamlit
pandas
plotly
pycountry
"""

# Write the content to requirements.txt
with open("requirements.txt", "w") as f:
    f.write(requirements_content)

# Create the .gitignore file content
gitignore_content = """
# Ignore Jupyter Notebook checkpoints
.ipynb_checkpoints/

# Ignore Python bytecode
__pycache__/

# Ignore local configuration files
*.env
.vscode/

# Ignore data files that might be generated
*.csv
*.pkl
"""

# Write the content to .gitignore
with open(".gitignore", "w") as f:
    f.write(gitignore_content)

print("app.py, requirements.txt, and .gitignore files created successfully.")
