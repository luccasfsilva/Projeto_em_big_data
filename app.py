# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Filmes",
    page_icon="🎬",
    layout="wide"
)

# Carregar dados
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    df = pd.read_csv(url)
    
    # Processar dados básicos
    df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
    df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
    df["score"] = pd.to_numeric(df.get("score"), errors="coerce").fillna(0)
    
    # Processar datas
    df["date_x"] = pd.to_datetime(df["date_x"], errors='coerce')
    df["ano"] = df["date_x"].dt.year.fillna(2000).astype(int)
    
    # Calcular ROI
    df["roi"] = np.where(
        df["budget_x"] > 0,
        (df["revenue"] - df["budget_x"]) / df["budget_x"] * 100,
        0
    )
    
    return df

# Carregar dados
df = carregar_dados()

# Sidebar simples
with st.sidebar:
    st.header("Filtros")
    
    # Filtro de anos
    anos = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos,
        value=(min(anos), max(anos))
    )
    
    # Filtro de nota
    nota_min, nota_max = st.slider(
        "Nota IMDb:",
        0.0, 10.0, (0.0, 10.0), 0.1
    )

# Aplicar filtros
df_filtrado = df[
    (df["ano"] >= ano_min) & 
    (df["ano"] <= ano_max) &
    (df["score"] >= nota_min) & 
    (df["score"] <= nota_max)
]

# Título
st.title("🎬 Análise de Filmes")
st.write(f"Mostrando {len(df_filtrado)} filmes de {ano_min} a {ano_max}")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Filmes", f"{len(df_filtrado):,}")

with col2:
    receita_total = df_filtrado["revenue"].sum()
    st.metric("Receita Total", f"${receita_total:,.0f}")

with col3:
    nota_media = df_filtrado["score"].mean()
    st.metric("Nota Média", f"{nota_media:.2f}")

with col4:
    roi_medio = df_filtrado["roi"].mean()
    st.metric("ROI Médio", f"{roi_medio:.1f}%")

st.divider()

# Análises principais
tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "🎭 Top Filmes", "📈 Análises"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dispersão
        fig = px.scatter(
            df_filtrado,
            x="budget_x",
            y="revenue",
            title="Orçamento vs Receita",
            labels={"budget_x": "Orçamento", "revenue": "Receita"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de notas
        fig = px.histogram(
            df_filtrado,
            x="score",
            title="Distribuição de Notas",
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Evolução temporal
    evolucao = df_filtrado.groupby("ano").agg({
        "revenue": "mean",
        "score": "mean"
    }).reset_index()
    
    fig = px.line(
        evolucao,
        x="ano",
        y=["revenue", "score"],
        title="Evolução da Receita e Nota por Ano",
        labels={"value": "Valor", "variable": "Métrica"}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Maior Receita")
        top_receita = df_filtrado.nlargest(10, "revenue")[["names", "revenue", "score"]]
        for idx, filme in top_receita.iterrows():
            st.write(f"**{filme['names']}**")
            st.write(f"Receita: ${filme['revenue']:,.0f} | Nota: {filme['score']:.1f}")
            st.divider()
    
    with col2:
        st.subheader("📈 Melhor ROI")
        top_roi = df_filtrado.nlargest(10, "roi")[["names", "roi", "revenue"]]
        for idx, filme in top_roi.iterrows():
            st.write(f"**{filme['names']}**")
            st.write(f"ROI: {filme['roi']:.1f}% | Receita: ${filme['revenue']:,.0f}")
            st.divider()

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Correlações")
        
        # Calcular correlações
        correlacoes = df_filtrado[["revenue", "budget_x", "score", "roi"]].corr()
        
        fig = px.imshow(
            correlacoes,
            title="Correlação entre Variáveis",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💡 Insights")
        
        # Insights simples
        filme_maior_receita = df_filtrado.loc[df_filtrado["revenue"].idxmax()]
        filme_melhor_nota = df_filtrado.loc[df_filtrado["score"].idxmax()]
        filme_melhor_roi = df_filtrado.loc[df_filtrado["roi"].idxmax()]
        
        st.metric("Filme com Maior Receita", 
                 f"{filme_maior_receita['names'][:30]}...",
                 f"${filme_maior_receita['revenue']:,.0f}")
        
        st.metric("Filme com Melhor Nota",
                 f"{filme_melhor_nota['names'][:30]}...", 
                 f"{filme_melhor_nota['score']:.1f}")
        
        st.metric("Filme com Melhor ROI",
                 f"{filme_melhor_roi['names'][:30]}...",
                 f"{filme_melhor_roi['roi']:.1f}%")

# Tabela de dados
st.divider()
st.subheader("📋 Dados dos Filmes")

# Busca simples
busca = st.text_input("🔍 Buscar filme:")

if busca:
    df_tabela = df_filtrado[df_filtrado["names"].str.contains(busca, case=False, na=False)]
else:
    df_tabela = df_filtrado

# Mostrar tabela
if not df_tabela.empty:
    colunas = ["names", "ano", "score", "revenue", "budget_x", "roi"]
    df_display = df_tabela[colunas].copy()
    
    # Formatar colunas
    df_display["revenue"] = df_display["revenue"].apply(lambda x: f"${x:,.0f}")
    df_display["budget_x"] = df_display["budget_x"].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
    df_display["roi"] = df_display["roi"].apply(lambda x: f"{x:.1f}%")
    df_display["score"] = df_display["score"].apply(lambda x: f"{x:.1f}")
    
    # Renomear colunas
    df_display = df_display.rename(columns={
        "names": "Filme",
        "ano": "Ano", 
        "score": "Nota",
        "revenue": "Receita",
        "budget_x": "Orçamento",
        "roi": "ROI"
    })
    
    st.dataframe(df_display, use_container_width=True, height=400)
else:
    st.info("Nenhum filme encontrado com os filtros atuais.")

# Rodapé
st.divider()
st.caption("Desenvolvido para análise de dados de filmes | Fonte: IMDb")
