import pandas as pd
import GoogleTranslator
import time

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

# Função para traduzir os títulos
def traduzir_titulo(titulo):
    try:
        # Dicionário com traduções específicas para filmes conhecidos
        traducoes_especificas = {
            'Fast X': 'Velozes e Furiosos 10',
            'The Little Mermaid': 'A Pequena Sereia',
            'Transformers: Rise of the Beasts': 'Transformers: O Despertar das Feras',
            'Spider-Man: Across the Spider-Verse': 'Homem-Aranha: Através do Aranhaverso',
            'Guardians of the Galaxy Volume 3': 'Guardiões da Galáxia Volume 3',
            'Extraction 2': 'Resgate 2',
            'The Nun 2': 'A Freira 2'
        }
        
        # Verifica se tem tradução específica
        if titulo in traducoes_especificas:
            return traducoes_especificas[titulo]
        
        # Para outros filmes, usa tradução automática
        if titulo == 'Barbie' or titulo == 'The Flash':
            return titulo  # Mantém original (já é usado no Brasil)
        
        # Tradução automática para os demais
        translator = GoogleTranslator(source='en', target='pt')
        traducao = translator.translate(titulo)
        time.sleep(0.5)  # Delay para não sobrecarregar a API
        return traducao
        
    except Exception as e:
        print(f"Erro ao traduzir '{titulo}': {e}")
        return titulo

# Aplicando a tradução na coluna Filme
print("Traduzindo títulos...")
df['Filme_Portugues'] = df['Filme'].apply(traduzir_titulo)

# Reorganizando as colunas
colunas = ['Filme', 'Filme_Portugues', 'Ano', 'Nota', 'Receita', 'Orçamento', 'ROI']
df = df[colunas]

# Exibindo o resultado
print("\nDataFrame com traduções:")
print(df)

# Opcional: Salvar em CSV
df.to_csv('filmes_traduzidos.csv', index=False, encoding='utf-8-sig')
print("\nArquivo 'filmes_traduzidos.csv' salvo com sucesso!")
