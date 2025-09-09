# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

st.set_page_config(page_title="Dashboard de Filmes", page_icon="🎬", layout="wide")

# --- Carregar os dados ---
# Substitua pelo caminho ou link raw do GitHub
df = pd.read_csv("https://raw.githubusercontent.com/seu_usuario/seu_repo/main/filmes.csv")

# Garantir colunas corretas
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["score"] = pd.to_numeric(df["score"], errors="coerce")

# --- KPIs ---
st.subheader("📌 Métricas Gerais dos Filmes")

if not df.empty:
    receita_total = df["revenue"].sum()
    receita_media = df["revenue"].mean()
    nota_media = df["score"].mean()
    total_filmes = df.shape[0]
else:
    receita_total, receita_media, nota_media, total_filmes = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total", f"${receita_total:,.0f}")
col2.metric("Receita Média", f"${receita_media:,.0f}")
col3.metric("Nota Média", f"{nota_media:.2f}")
col4.metric("Total de Filmes", f"{total_filmes:,}")

st.markdown("---")

# --- Gráficos ---
st.subheader("📊 Análises Visuais")

col_g1, col_g2 = st.columns(2)

with col_g1:
    top_n = 10
    df_top_revenue = df.sort_values(by="revenue", ascending=False).head(top_n)
    graf1 = px.bar(
        df_top_revenue,
        x="names",
        y="revenue",
        title=f"Top {top_n} Filmes por Receita",
        labels={"names": "Filme", "revenue": "Receita"}
    )
    st.plotly_chart(graf1, use_container_width=True)

with col_g2:
    graf2 = px.histogram(
        df,
        x="score",
        nbins=20,
        title="Distribuição das Notas dos Filmes",
        labels={"score": "Nota", "count": "Frequência"}
    )
    st.plotly_chart(graf2, use_container_width=True)

col_g3, col_g4 = st.columns(2)

with col_g3:
    contagem_idiomas = df["orig_lang"].value_counts().head(10).reset_index()
    contagem_idiomas.columns = ["Idioma Original", "Número de Filmes"]
    graf3 = px.pie(
        contagem_idiomas,
        values="Número de Filmes",
        names="Idioma Original",
        title="Top 10 Idiomas Originais",
        hole=0.3
    )
    st.plotly_chart(graf3, use_container_width=True)

with col_g4:
    # Receita total por país
    revenue_country = df.groupby("country")["revenue"].sum().reset_index()
    revenue_country.columns = ["iso_alpha", "Total Revenue"]

    def iso2_to_iso3(iso2):
        try:
            return pycountry.countries.get(alpha_2=iso2).alpha_3
        except:
            return None

    revenue_country["country_iso3"] = revenue_country["iso_alpha"].apply(iso2_to_iso3)
    revenue_country = revenue_country.dropna(subset=["country_iso3"])

    graf4 = px.choropleth(
        revenue_country,
        locations="country_iso3",
        color="Total Revenue",
        color_continuous_scale="Plasma",
        title="Receita Total por País",
        labels={"Total Revenue": "Receita Total", "country_iso3": "País"}
    )
    st.plotly_chart(graf4, use_container_width=True)

st.markdown("---")

# --- Tabela Completa ---
st.subheader("📋 Dados dos Filmes")
st.dataframe(df)
