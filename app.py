# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="CineAnalytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILOS CSS PERSONALIZADOS
# =========================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #cccccc, #8f8f8f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #8a0b0b;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dataframe {
        font-size: 14px;
    }
    .dataframe thead th {
        background-color: #2c2c2c;
        color: white;
        font-weight: bold;
        padding: 12px;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #1a1a1a;
    }
    .dataframe tbody tr:hover {
        background-color: #3a3a3a;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CARREGAR DADOS
# =========================
@st.cache_data
def carregar_dados():
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar o CSV.\nDetalhe: {e}")
        st.stop()

df = carregar_dados()
if df is None:
    st.stop()

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.header("🎛️ Painel de Controle")

    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )

    score_min, score_max = st.slider(
        "Filtrar por nota:",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1
    )

    receita_max = df["revenue"].max()
    receita_min, receita_max = st.slider(
        "Filtrar por receita:",
        min_value=0.0,
        max_value=float(receita_max),
        value=(0.0, float(receita_max)),
        step=1_000_000.0,
        format="$%.0f"
    )

# Filtro principal
df_filtrado = df[
    (df["ano"] >= ano_min) &
    (df["ano"] <= ano_max) &
    (df["score"] >= score_min) &
    (df["score"] <= score_max) &
    (df["revenue"] >= receita_min) &
    (df["revenue"] <= receita_max)
]

# =========================
# CABEÇALHO E MÉTRICAS
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics</h1>', unsafe_allow_html=True)

if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Receita Total", f"${receita_total:,.0f}")
with col2:
    st.metric("📊 Receita Média", f"${receita_media:,.0f}")
with col3:
    st.metric("⭐ Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—")
with col4:
    st.metric("🎭 Total de Filmes", f"{total_filmes:,}")

st.markdown("---")

# =========================
# GRÁFICOS INTERATIVOS
# =========================
st.subheader("📈 Análises Visuais Interativas")

col_g1, col_g2 = st.columns(2)
with col_g1:
    top_n = st.slider("Quantos filmes no TOP?", 5, 20, 10)
    df_top = df_filtrado.sort_values(by="revenue", ascending=False).head(top_n)
    fig1 = px.bar(
        df_top,
        x="names",
        y="revenue",
        title=f"🏆 Top {top_n} Filmes por Receita",
        labels={"names": "Filme", "revenue": "Receita"},
        color="revenue",
        color_continuous_scale="viridis",
        hover_data=["score", "ano"]
    )
    fig1.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    fig2 = px.scatter(
        df_filtrado,
        x="score",
        y="revenue",
        title="🎯 Relação: Nota vs Receita",
        labels={"score": "Nota", "revenue": "Receita"},
        color="score",
        size="revenue",
        hover_data=["names", "ano"],
        color_continuous_scale="plasma"
    )
    st.plotly_chart(fig2, use_container_width=True)

col_g3, col_g4 = st.columns(2)
with col_g3:
    receita_anual = df_filtrado.groupby("ano")["revenue"].sum().reset_index()
    fig3 = px.area(
        receita_anual,
        x="ano",
        y="revenue",
        title="📈 Evolução da Receita Anual",
        labels={"ano": "Ano", "revenue": "Receita Total"}
    )
    fig3.update_traces(line=dict(color="#4ECDC4"), fillcolor="rgba(78,205,196,0.2)")
    st.plotly_chart(fig3, use_container_width=True)

with col_g4:
    contagem_idiomas = df_filtrado["orig_lang"].value_counts().head(8).reset_index()
    contagem_idiomas.columns = ["Idioma Original", "Quantidade de Filmes"]
    fig4 = px.pie(
        contagem_idiomas,
        values="Quantidade de Filmes",
        names="Idioma Original",
        title="🌎 Distribuição de Idiomas Originais",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig4, use_container_width=True)

# =========================
# TABELA INTERATIVA EM PORTUGUÊS - MELHORADA
# =========================
st.subheader("📋 Base de Dados Completa")

with st.expander("🔍 Explorar Dados dos Filmes", expanded=False):
    # Campos de busca e ordenação
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        search_term = st.text_input("Buscar pelo nome do filme:", placeholder="Digite o nome do filme...")
    with col_f2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "Ano de Lançamento", "Nome do Filme"],
            index=0
        )
    with col_f3:
        resultados_por_pagina = st.selectbox("Itens por página:", [10, 25, 50, 100], index=0)

    # Copia e renomeia colunas do DataFrame original
    df_display = df_filtrado.copy().rename(columns={
        "names": "Nome do Filme",
        "orig_lang": "Idioma Original",
        "revenue": "Receita",
        "score": "Pontuação",
        "ano": "Ano de Lançamento",
        "date_x": "Data de Lançamento",
        "country": "País de Origem",
        "genre": "Gênero"
    })

    # Dicionário de traduções dos nomes dos filmes (expandido)
    traducao_filmes = {
        "It": "It: A Coisa",
        "Barbie": "Barbie",
        "The Little Mermaid": "A Pequena Sereia",
        "Elemental": "Elementos",
        "The Professional Bridesmaid": "A Dama de Honra Profissional",
        "Munthiri Kaadu": "A Floresta das Uvas",
        "No Hard Feelings": "Quer Saber?",
        "Pretty Young Sister": "Jovem e Bonita",
        "The Expendables 4": "Os Mercenários 4",
        "Oppenheimer": "Oppenheimer",
        "The Flash": "The Flash",
        "Fast X": "Velozes e Furiosos 10",
        "Guardians of the Galaxy Vol. 3": "Guardiões da Galáxia Vol. 3",
        "The Marvels": "As Marvels",
        "Haunted Mansion": "Mansão Mal-Assombrada",
        "Spider-Man: Across the Spider-Verse": "Homem-Aranha: Através do Aranhaverso",
        "Avatar: The Way of Water": "Avatar: O Caminho da Água",
        "Black Panther": "Pantera Negra",
        "Avengers: Endgame": "Vingadores: Ultimato",
        "The Batman": "Batman",
        "Jurassic World": "Mundo Jurássico",
        "Frozen": "Frozen: Uma Aventura Congelante",
        "The Super Mario Bros. Movie": "Super Mario Bros.: O Filme",
        "Transformers": "Transformers",
        "Iron Man": "Homem de Ferro"
    }

    # Substitui os nomes em inglês pelos traduzidos
    df_display["Nome do Filme"] = df_display["Nome do Filme"].replace(traducao_filmes)

    # Formata a data no padrão brasileiro (dd/mm/aaaa)
    if "Data de Lançamento" in df_display.columns:
        df_display["Data de Lançamento"] = pd.to_datetime(
            df_display["Data de Lançamento"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    # Formata a receita como moeda
    df_display["Receita"] = df_display["Receita"].apply(
        lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A"
    )

    # Formata a pontuação
    df_display["Pontuação"] = df_display["Pontuação"].apply(
        lambda x: f"{x:.1f}" if pd.notnull(x) else "N/A"
    )

    # Filtro de busca (ignora maiúsculas/minúsculas)
    if search_term:
        df_display = df_display[
            df_display["Nome do Filme"].str.contains(search_term, case=False, na=False) |
            df_display["Gênero"].str.contains(search_term, case=False, na=False) |
            df_display["País de Origem"].str.contains(search_term, case=False, na=False)
        ]

    # Ordenação
    sort_map = {
        "Receita": "Receita",
        "Pontuação": "Pontuação",
        "Ano de Lançamento": "Ano de Lançamento",
        "Nome do Filme": "Nome do Filme"
    }
    
    if sort_by in sort_map and sort_map[sort_by] in df_display.columns:
        ascending = sort_by == "Nome do Filme"  # Ordem alfabética para nomes
        df_display = df_display.sort_values(by=sort_map[sort_by], ascending=ascending)

    # Colunas a exibir
    colunas_para_mostrar = [
        "Nome do Filme", "Gênero", "Idioma Original", "País de Origem",
        "Pontuação", "Receita", "Ano de Lançamento", "Data de Lançamento"
    ]

    # Sistema de paginação
    total_resultados = len(df_display)
    if total_resultados > 0:
        total_paginas = (total_resultados + resultados_por_pagina - 1) // resultados_por_pagina
        pagina_atual = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
        
        inicio = (pagina_atual - 1) * resultados_por_pagina
        fim = inicio + resultados_por_pagina
        
        df_paginado = df_display.iloc[inicio:fim]
        
        # Exibe informações da paginação
        st.caption(f"Mostrando {inicio + 1}-{min(fim, total_resultados)} de {total_resultados} resultados")
        
        # Exibe a tabela formatada
        st.dataframe(
            df_paginado[colunas_para_mostrar],
            use_container_width=True,
            height=400,
            hide_index=True
        )
    else:
        st.warning("Nenhum resultado encontrado com os filtros aplicados.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>📊 Dashboard desenvolvido com Streamlit • Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>",
    unsafe_allow_html=True
)
