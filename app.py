import pandas as pd
import streamlit as st

# Criando o DataFrame com os dados fornecidos
data = {
    'Filme': [
        'Fast X',
        'The Little Mermaid', 
        'Transformers: Rise of the Beasts',
        'Spider-Man: Across the Spider-Verse',
        'Housewife Sex Slaves: Hatano Yui',
        'Barbie',
        'Guardians of the Galaxy Volume 3',
        'Extraction 2',
        'The Flash',
        'The Nun 2'
    ],
    'Ano': [2023, 2023, 2023, 2023, 2015, 2023, 2023, 2023, 2023, 2023],
    'Nota': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'Receita': ['$0', '$178,359,863', '$1,240,262', '$175,269,999', '$175,269,999', 
                '$178,359,863', '$1,240,262', '$175,269,999', '$1,240,262', '$175,269,999'],
    'Orçamento': ['$340,000,000', '$205,000,000', '$200,000,000', '$264,940,000', 
                  '$167,540,000', '$175,000,000', '$250,000,000', '$226,000,000', 
                  '$200,000,000', '$246,000,000'],
    'ROI': ['-100.0%', '-13.0%', '-99.4%', '-33.8%', '4.6%', '1.9%', '-99.5%', 
            '-22.4%', '-99.4%', '-28.8%']
}

df = pd.DataFrame(data)

# Dicionário completo com traduções para português
traducoes_filmes = {
    'Fast X': 'Velozes e Furiosos 10',
    'The Little Mermaid': 'A Pequena Sereia',
    'Transformers: Rise of the Beasts': 'Transformers: O Despertar das Feras',
    'Spider-Man: Across the Spider-Verse': 'Homem-Aranha: Através do Aranhaverso',
    'Housewife Sex Slaves: Hatano Yui': 'Escravas Sexuais Donas de Casa: Hatano Yui',
    'Barbie': 'Barbie',
    'Guardians of the Galaxy Volume 3': 'Guardiões da Galáxia Volume 3',
    'Extraction 2': 'Resgate 2',
    'The Flash': 'The Flash',
    'The Nun 2': 'A Freira 2'
}

# Função simples para traduzir baseada no dicionário
def traduzir_filme(titulo_original):
    return traducoes_filmes.get(titulo_original, titulo_original)

# Aplicando a tradução
df['Filme_Portugues'] = df['Filme'].apply(traduzir_filme)

# Interface Streamlit
st.title("🎬 Tradução de Filmes para Português")

st.write("### DataFrame Original")
st.dataframe(df[['Filme', 'Ano', 'Nota', 'Receita', 'Orçamento', 'ROI']])

st.write("### DataFrame com Traduções")
st.dataframe(df[['Filme_Portugues', 'Ano', 'Nota', 'Receita', 'Orçamento', 'ROI']])

# Mostrar apenas as colunas traduzidas
st.write("### Apenas os Filmes Traduzidos")
st.dataframe(df[['Filme', 'Filme_Portugues']])

# Download do CSV
csv = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Baixar CSV com traduções",
    data=csv,
    file_name="filmes_traduzidos.csv",
    mime="text/csv"
)

st.success("Traduções concluídas com sucesso!")
