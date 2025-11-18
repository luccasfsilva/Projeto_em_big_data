# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="CineAnalytics Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILOS CSS PERSONALIZADOS MODERNOS
# =========================
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .metric-card-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .section-header {
        font-size: 1.5rem;
        color: #667eea;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
        font-weight: 600;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
    }
    .prediction-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# DICIONÁRIOS DE TRADUÇÃO COMPLETOS
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
    
    # Filmes em Português
    "Cidade de Deus": "Cidade de Deus",
    "Tropa de Elite": "Tropa de Elite",
    "Central do Brasil": "Central do Brasil",
    "O Auto da Compadecida": "O Auto da Compadecida",
    "Lisbela e o Prisioneiro": "Lisbela e o Prisioneiro",
    "Ó Paí, Ó": "Ó Paí, Ó",
    "Carandiru": "Carandiru",
    "Que Horas Ela Volta?": "Que Horas Ela Volta?",
    "Hoje Eu Quero Voltar Sozinho": "Hoje Eu Quero Voltar Sozinho",
}

# Dicionário de tradução de gêneros
TRADUCOES_GENEROS = {
    "Action": "Ação",
    "Adventure": "Aventura",
    "Animation": "Animação",
    "Comedy": "Comédia",
    "Crime": "Crime",
    "Documentary": "Documentário",
    "Drama": "Drama",
    "Family": "Família",
    "Fantasy": "Fantasia",
    "History": "História",
    "Horror": "Terror",
    "Music": "Música",
    "Mystery": "Mistério",
    "Romance": "Romance",
    "Science Fiction": "Ficção Científica",
    "TV Movie": "Filme de TV",
    "Thriller": "Suspense",
    "War": "Guerra",
    "Western": "Faroeste",
    "Action & Adventure": "Ação e Aventura",
    "Sci-Fi & Fantasy": "Ficção Científica e Fantasia",
    "Kids": "Infantil",
    "News": "Notícias",
    "Reality": "Reality Show",
    "Talk": "Talk Show",
    "Soap": "Novela",
}

# Dicionário de meses em português
MESES_PORTUGUES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# =========================
# SISTEMA DE TRADUÇÃO AVANÇADO
# =========================
class SistemaTraducao:
    def __init__(self):
        self.cache_traducoes = {}
        self.cache_generos = {}
    
    def traduzir_filme(self, nome_original):
        """Traduz nome do filme com cache"""
        if pd.isna(nome_original) or not isinstance(nome_original, str):
            return nome_original
        
        if nome_original in self.cache_traducoes:
            return self.cache_traducoes[nome_original]
        
        traducao = TRADUCOES_FILMES.get(nome_original, nome_original)
        self.cache_traducoes[nome_original] = traducao
        return traducao
    
    def traduzir_genero(self, genero_original):
        """Traduz gênero com suporte para múltiplos gêneros"""
        if pd.isna(genero_original) or not isinstance(genero_original, str):
            return "Gênero não disponível"
        
        if genero_original in self.cache_generos:
            return self.cache_generos[genero_original]
        
        # Se for uma string com múltiplos gêneros separados por vírgula
        if ',' in genero_original:
            generos = [g.strip() for g in genero_original.split(',')]
            generos_traduzidos = [TRADUCOES_GENEROS.get(g, g) for g in generos]
            traducao = ', '.join(generos_traduzidos)
        else:
            traducao = TRADUCOES_GENEROS.get(genero_original, genero_original)
        
        self.cache_generos[genero_original] = traducao
        return traducao
    
    def formatar_data_completa(self, data):
        """Formata data completa em português: dia, mês e ano"""
        if pd.isna(data):
            return "Data não disponível"
        
        try:
            if isinstance(data, str):
                data = pd.to_datetime(data)
            
            dia = data.day
            mes_numero = data.month
            mes = MESES_PORTUGUES.get(mes_numero, f"Mês {mes_numero}")
            ano = data.year
            
            return f"{dia} de {mes} de {ano}"
        except Exception as e:
            return f"Data inválida: {str(e)}"

# =========================
# CARREGAR E PROCESSAR DADOS
# =========================
@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def carregar_dados_completos():
    """
    Carrega e processa dados com traduções completas
    """
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    
    try:
        # Carregar dados
        df = pd.read_csv(CSV_URL)
        
        # Verificar colunas disponíveis
        st.info(f"📊 Colunas disponíveis no dataset: {list(df.columns)}")
        
        # Inicializar sistema de tradução
        tradutor = SistemaTraducao()
        
        # Processar dados básicos - com tratamento de erros robusto
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce").fillna(0)
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        
        # Processar datas - com múltiplas tentativas
        date_columns = ['date_x', 'date_published', 'release_date']
        date_column = None
        
        for col in date_columns:
            if col in df.columns:
                date_column = col
                break
        
        if date_column:
            df["date_x"] = pd.to_datetime(df[date_column], errors='coerce')
        else:
            st.warning("⚠️ Nenhuma coluna de data encontrada. Criando datas fictícias.")
            # Criar datas fictícias baseadas no índice
            start_date = datetime(2000, 1, 1)
            df["date_x"] = [start_date + timedelta(days=x*30) for x in range(len(df))]
        
        # Extrair componentes de data
        df["ano"] = df["date_x"].dt.year.fillna(2000).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(1).astype(int)
        df["dia"] = df["date_x"].dt.day.fillna(1).astype(int)
        
        # Aplicar traduções
        with st.spinner("🔄 Aplicando traduções..."):
            
            # Traduzir nomes dos filmes
             if 'names' in df.columns:
                df["nome_pt"] = df["names"].apply(tradutor.traduzir_filme)
             else:
                st.error("❌ Coluna 'names' não encontrada no dataset")
                df["nome_pt"] = "Nome não disponível"
            
           
                    # Traduzir gêneros - verificar colunas possíveis
        genre_columns = ['genre', 'genres', 'category', 'type']
        genre_column = None

        for col in genre_columns:
            if col in df.columns:
                genre_column = col
                break

        if genre_column:
            df["genero_pt"] = df[genre_column].apply(tradutor.traduzir_genero)
            st.success(f"✅ Gêneros traduzidos da coluna: {genre_column}")
        else:
            st.warning("⚠️ Nenhuma coluna de gênero encontrada. Usando valor padrão.")
            df["genero_pt"] = "Gênero não disponível"

            
            # Adicionar data formatada em português
            df["data_completa_pt"] = df["date_x"].apply(tradutor.formatar_data_completa)
        
        # Calcular métricas financeiras
        df["roi"] = np.where(
            df["budget_x"] > 0,
            (df["revenue"] - df["budget_x"]) / df["budget_x"] * 100,
            0
        )
        
        df["lucro"] = df["revenue"] - df["budget_x"]
        
        # Categorizar sucesso
 revenue_q = df['revenue'].quantile([0.3, 0.5, 0.7, 0.9])

        conditions = [
            (df['revenue'] >= revenue_q.loc[0.9]),
            (df['revenue'] >= revenue_q.loc[0.7]),
            (df['revenue'] >= revenue_q.loc[0.5]),
            (df['revenue'] >= revenue_q.loc[0.3]),
            (df['revenue'] <  revenue_q.loc[0.3])
        ]

        choices = [
            'Super Blockbuster',
            'Blockbuster',
            'High',
            'Medium',
            'Low'
        ]

        df['success_category'] = np.select(conditions, choices, default='Low')

        st.success(f"✅ Dados carregados com sucesso! {len(df)} filmes processados.")
        return df

    except Exception as e:
        st.error(f"❌ Erro crítico ao carregar dados: {str(e)}")
        return None

# =========================
# INTERFACE PRINCIPAL
# =========================

# Carregar dados
df = carregar_dados_completos()
if df is None:
    st.error("Não foi possível carregar os dados. Verifique a conexão e tente novamente.")
    st.stop()

# Verificar se as colunas necessárias existem
colunas_necessarias = ['genero_pt', 'nome_pt', 'data_completa_pt']
colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]

if colunas_faltantes:
    st.warning(f"⚠️ Colunas faltantes: {colunas_faltantes}")
    # Criar colunas faltantes com valores padrão
    for col in colunas_faltantes:
        if col == 'genero_pt':
            df['genero_pt'] = "Gênero não disponível"
        elif col == 'nome_pt':
            df['nome_pt'] = df.get('names', 'Nome não disponível')
        elif col == 'data_completa_pt':
            df['data_completa_pt'] = "Data não disponível"

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #667eea;'>🎛️ Painel de Controle</h2>", unsafe_allow_html=True)
    
    st.markdown("### 📅 Filtros por Data")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )
    
    st.markdown("---")
    
    # Filtro por gênero - com verificação segura
    st.markdown("### 🎭 Filtro por Gênero")
    
    # Verificar se a coluna genero_pt existe e tem dados
    if 'genero_pt' in df.columns:
        generos_disponiveis = sorted([g for g in df["genero_pt"].unique() if pd.notna(g) and g != ""])
        
        if generos_disponiveis:
            generos_selecionados = st.multiselect(
                "Selecione os gêneros:",
                options=generos_disponiveis,
                default=generos_disponiveis[:3] if len(generos_disponiveis) > 3 else generos_disponiveis,
                help="Escolha os gêneros para filtrar"
            )
        else:
            st.warning("Nenhum gênero disponível para filtro")
            generos_selecionados = []
    else:
        st.error("Coluna de gêneros não disponível")
        generos_selecionados = []
    
    st.markdown("---")
    
    # Filtros de performance
    st.markdown("### 📊 Filtros de Performance")
    score_min, score_max = st.slider(
        "⭐ Nota IMDb:",
        0.0, 10.0, (0.0, 10.0), 0.1
    )
    
    roi_min, roi_max = st.slider(
        "📈 ROI (%):",
        float(df["roi"].min()), float(df["roi"].max()), 
        (float(df["roi"].quantile(0.1)), float(df["roi"].quantile(0.9))), 
        50.0
    )

# Aplicar filtros de forma segura
try:
    df_filtrado = df.copy()
    
    # Aplicar filtro de anos
    df_filtrado = df_filtrado[
        (df_filtrado["ano"] >= ano_min) & 
        (df_filtrado["ano"] <= ano_max)
    ]
    
    # Aplicar filtro de gêneros se houver gêneros selecionados
    if generos_selecionados:
        df_filtrado = df_filtrado[df_filtrado["genero_pt"].isin(generos_selecionados)]
    
    # Aplicar outros filtros
    df_filtrado = df_filtrado[
        (df_filtrado["score"] >= score_min) & 
        (df_filtrado["score"] <= score_max) &
        (df_filtrado["roi"] >= roi_min) & 
        (df_filtrado["roi"] <= roi_max)
    ]
    
except Exception as e:
    st.error(f"Erro ao aplicar filtros: {e}")
    df_filtrado = df

# =========================
# CABEÇALHO PRINCIPAL
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Completo com Filmes em Português</p>', unsafe_allow_html=True)

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
if not df_filtrado.empty:
    total_filmes = df_filtrado.shape[0]
    total_generos = df_filtrado["genero_pt"].nunique()
    periodo_anos = f"{ano_min} - {ano_max}"
    receita_total = df_filtrado["revenue"].sum()
else:
    total_filmes = total_generos = receita_total = 0
    periodo_anos = "N/A"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎬 Total de Filmes", f"{total_filmes:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card-success">', unsafe_allow_html=True)
    st.metric("🎭 Gêneros Diferentes", f"{total_generos}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("📅 Período", periodo_anos)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# SISTEMA DE ABAS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Catálogo Completo", 
    "📊 Análise por Gênero", 
    "📅 Linha do Tempo",
    "🔍 Busca Avançada"
])

with tab1:
    st.markdown('<div class="section-header">📋 Catálogo Completo de Filmes</div>', unsafe_allow_html=True)
    
    # Filtros rápidos
    col_search, col_sort = st.columns([2, 1])
    
    with col_search:
        termo_busca = st.text_input("🔍 Buscar filme:", placeholder="Digite o nome do filme...")
    
    with col_sort:
        ordenacao = st.selectbox(
            "Ordenar por:",
            ["Nome A-Z", "Nome Z-A", "Maior Receita", "Maior Nota", "Data Recente", "Data Antiga"]
        )
    
    # Aplicar busca
    if termo_busca:
        df_display = df_filtrado[
            df_filtrado["nome_pt"].str.contains(termo_busca, case=False, na=False) |
            df_filtrado["genero_pt"].str.contains(termo_busca, case=False, na=False)
        ]
    else:
        df_display = df_filtrado.copy()
    
    # Aplicar ordenação
    ordenacao_map = {
        "Nome A-Z": "nome_pt",
        "Nome Z-A": "nome_pt", 
        "Maior Receita": "revenue",
        "Maior Nota": "score",
        "Data Recente": "date_x",
        "Data Antiga": "date_x"
    }
    
    if ordenacao in ordenacao_map:
        coluna_ordenacao = ordenacao_map[ordenacao]
        ascending = ordenacao in ["Nome A-Z", "Data Antiga"]
        
        if coluna_ordenacao in df_display.columns:
            df_display = df_display.sort_values(coluna_ordenacao, ascending=ascending)
    
    # Exibir catálogo
    if not df_display.empty:
        # Selecionar colunas para exibição
        colunas_disponiveis = df_display.columns.tolist()
        colunas_desejadas = ['nome_pt', 'genero_pt', 'data_completa_pt', 'score', 'revenue', 'budget_x', 'roi']
        colunas_exibicao = [col for col in colunas_desejadas if col in colunas_disponiveis]
        
        # Formatar DataFrame para exibição
        df_exibicao = df_display[colunas_exibicao].copy()
        
        # Formatar colunas numéricas
        if 'revenue' in df_exibicao.columns:
            df_exibicao['revenue'] = df_exibicao['revenue'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
        
        if 'budget_x' in df_exibicao.columns:
            df_exibicao['budget_x'] = df_exibicao['budget_x'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "N/A")
        
        if 'roi' in df_exibicao.columns:
            df_exibicao['roi'] = df_exibicao['roi'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        
        if 'score' in df_exibicao.columns:
            df_exibicao['score'] = df_exibicao['score'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
        
        # Renomear colunas
        mapeamento_nomes = {
            'nome_pt': '🎬 Filme',
            'genero_pt': '🎭 Gênero',
            'data_completa_pt': '📅 Data de Lançamento',
            'score': '⭐ Nota',
            'revenue': '💰 Receita',
            'budget_x': '💸 Orçamento',
            'roi': '📈 ROI'
        }
        
        df_exibicao = df_exibicao.rename(columns=mapeamento_nomes)
        
        # Exibir tabela
        st.dataframe(df_exibicao, use_container_width=True, height=600)
        
        # Estatísticas do catálogo
        st.markdown(f"**📊 Mostrando {len(df_display)} de {len(df_filtrado)} filmes**")
        
    else:
        st.warning("Nenhum filme encontrado com os critérios selecionados.")

with tab2:
    st.markdown('<div class="section-header">📊 Análise Detalhada por Gênero</div>', unsafe_allow_html=True)
    
    if not df_filtrado.empty and 'genero_pt' in df_filtrado.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Estatísticas por gênero
            st.markdown("#### 📈 Performance por Gênero")
            
            stats_genero = df_filtrado.groupby('genero_pt').agg({
                'nome_pt': 'count',
                'revenue': 'mean',
                'score': 'mean',
                'roi': 'mean'
            }).round(2).sort_values('revenue', ascending=False)
            
            stats_genero = stats_genero.rename(columns={
                'nome_pt': 'Nº Filmes',
                'revenue': 'Receita Média',
                'score': 'Nota Média',
                'roi': 'ROI Médio'
            })
            
            st.dataframe(stats_genero, use_container_width=True)
        
        with col2:
            # Gráfico de distribuição por gênero
            st.markdown("#### 🎭 Distribuição por Gênero")
            
            contagem_generos = df_filtrado['genero_pt'].value_counts().head(10)
            
            if not contagem_generos.empty:
                fig_generos = px.pie(
                    values=contagem_generos.values,
                    names=contagem_generos.index,
                    title="Top 10 Gêneros Mais Comuns",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_generos, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o gráfico de gêneros")
        
        # Análise de receita por gênero ao longo do tempo
        st.markdown("#### 📈 Evolução Temporal por Gênero")
        
        # Agrupar por ano e gênero
        evolucao_genero = df_filtrado.groupby(['ano', 'genero_pt']).agg({
            'revenue': 'mean',
            'score': 'mean'
        }).reset_index()
        
        # Top 5 gêneros por receita
        top_generos = df_filtrado.groupby('genero_pt')['revenue'].mean().nlargest(5).index
        
        if not top_generos.empty and not evolucao_genero.empty:
            fig_evolucao = px.line(
                evolucao_genero[evolucao_genero['genero_pt'].isin(top_generos)],
                x='ano',
                y='revenue',
                color='genero_pt',
                title="Evolução da Receita Média dos Principais Gêneros",
                labels={'revenue': 'Receita Média', 'ano': 'Ano', 'genero_pt': 'Gênero'}
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
        else:
            st.info("Não há dados suficientes para a análise temporal por gênero")
    else:
        st.warning("Dados de gênero não disponíveis para análise")

with tab3:
    st.markdown('<div class="section-header">📅 Linha do Tempo Cinematográfica</div>', unsafe_allow_html=True)
    
    # Filtro por década
    decadas = sorted((df_filtrado['ano'] // 10 * 10).unique())
    
    if decadas:
        decada_selecionada = st.selectbox("Selecione a década:", decadas)
        
        if decada_selecionada:
            df_decada = df_filtrado[
                (df_filtrado['ano'] >= decada_selecionada) & 
                (df_filtrado['ano'] < decada_selecionada + 10)
            ]
            
            if not df_decada.empty:
                # Linha do tempo interativa
                st.markdown(f"#### 🎬 Filmes da Década de {decada_selecionada}s")
                
                # Criar linha do tempo com os filmes mais relevantes
                timeline_data = df_decada.nlargest(20, 'revenue')[['nome_pt', 'data_completa_pt', 'revenue', 'genero_pt', 'score']]
                
                for idx, filme in timeline_data.iterrows():
                    col_t1, col_t2 = st.columns([3, 1])
                    
                    with col_t1:
                        st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
                        st.markdown(f"**{filme['nome_pt']}**")
                        st.markdown(f"🎭 {filme['genero_pt']} | 📅 {filme['data_completa_pt']} | ⭐ {filme['score']:.1f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col_t2:
                        st.metric("💰 Receita", f"${filme['revenue']:,.0f}")
            
            else:
                st.info("Nenhum filme encontrado para esta década com os filtros atuais.")
    else:
        st.warning("Não há dados de décadas disponíveis")

with tab4:
    st.markdown('<div class="section-header">🔍 Busca Avançada e Filtros Detalhados</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Filtros Avançados")
        
        # Filtro por categoria de sucesso se existir
        if 'success_category' in df_filtrado.columns:
            categorias = st.multiselect(
                "Categorias de Sucesso:",
                options=df_filtrado['success_category'].unique(),
                default=df_filtrado['success_category'].unique()[:3]
            )
        else:
            categorias = []
        
        # Filtro por faixa de orçamento
        orcamento_min, orcamento_max = st.slider(
            "Faixa de Orçamento (USD):",
            float(df_filtrado['budget_x'].min()) if not df_filtrado.empty else 0,
            float(df_filtrado['budget_x'].max()) if not df_filtrado.empty else 100000000,
            (0.0, float(df_filtrado['budget_x'].max()) if not df_filtrado.empty else 100000000)
        )
        
        # Filtro por mês
        meses_selecionados = st.multiselect(
            "Meses de Lançamento:",
            options=list(MESES_PORTUGUES.values()),
            default=list(MESES_PORTUGUES.values())[:3]
        )
    
    with col2:
        st.markdown("#### 📊 Estatísticas dos Filtros")
        
        if not df_filtrado.empty:
            # Aplicar filtros adicionais
            df_avancado = df_filtrado.copy()
            
            # Aplicar filtro de categoria se selecionado
            if categorias:
                df_avancado = df_avancado[df_avancado['success_category'].isin(categorias)]
            
            # Aplicar filtro de orçamento
            df_avancado = df_avancado[
                (df_avancado['budget_x'] >= orcamento_min) &
                (df_avancado['budget_x'] <= orcamento_max)
            ]
            
            # Aplicar filtro de meses
            if meses_selecionados:
                meses_numeros = [k for k, v in MESES_PORTUGUES.items() if v in meses_selecionados]
                df_avancado = df_avancado[df_avancado['mes'].isin(meses_numeros)]
            
            if not df_avancado.empty:
                st.metric("Filmes Encontrados", len(df_avancado))
                st.metric("Receita Total", f"${df_avancado['revenue'].sum():,.0f}")
                st.metric("ROI Médio", f"{df_avancado['roi'].mean():.1f}%")
                st.metric("Nota Média", f"{df_avancado['score'].mean():.2f}")
                
                # Top 3 filmes
                st.markdown("#### 🏆 Top 3 Filmes")
                top3 = df_avancado.nlargest(3, 'revenue')
                for idx, filme in top3.iterrows():
                    st.markdown(f"**{filme['nome_pt']}** - ${filme['revenue']:,.0f}")
            else:
                st.warning("Nenhum filme encontrado com os filtros aplicados")
        else:
            st.warning("Nenhum dado disponível para os filtros")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>🎬 <strong>CineAnalytics Pro</strong> - Catálogo Completo em Português</p>
    <p>📅 Datas completas | 🎭 Gêneros traduzidos | 🎬 Nomes em português</p>
    <p>📊 Total de {:,} filmes disponíveis | 📅 Período: {} - {}</p>
</div>
""".format(len(df), df['ano'].min(), df['ano'].max()), unsafe_allow_html=True)
