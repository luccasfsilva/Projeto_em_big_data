# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Filmes", page_icon="🎬", layout="wide")

# --- tentativa de importar pycountry (corrige erro na linha 5 caso não esteja instalado) ---
try:
    import pycountry
    HAS_PYCOUNTRY = True
except Exception:
    pycountry = None
    HAS_PYCOUNTRY = False

# --- Carregar os dados ---
# Use a URL raw correta do GitHub (ajuste se o arquivo estiver em outra pasta)
CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"

try:
    df_limpo = pd.read_csv(CSV_URL)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo CSV.\nVerifique a URL ou se o arquivo existe.\nDetalhe: {e}")
    st.stop()

# Garantir tipos corretos e tratar NaNs
df_limpo["revenue"] = pd.to_numeric(df_limpo.get("revenue"), errors="coerce").fillna(0)
df_limpo["score"] = pd.to_numeric(df_limpo.get("score"), errors="coerce")
df_limpo["year"] = pd.to_numeric(df_limpo.get("year"), errors="coerce").fillna(0).astype(int)

# --- Adicionar o filtro na sidebar ---
st.sidebar.header("Filtros")

# Criar a lista de anos para o filtro
anos_disponiveis = sorted(df_limpo["year"].unique())
anos_disponiveis.insert(0, "Todos os Anos")

ano_selecionado = st.sidebar.selectbox("Selecione o Ano", anos_disponiveis)

# Filtrar o DataFrame com base na seleção do usuário
if ano_selecionado == "Todos os Anos":
    df_filtrado = df_limpo.copy()
else:
    df_filtrado = df_limpo[df_limpo["year"] == ano_selecionado]

# --- KPIs ---
st.title("🎬 Dashboard de Filmes")

if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total", f"${receita_total:,.0f}")
col2.metric("Receita Média", f"${receita_media:,.0f}")
col3.metric("Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—")
col4.metric("Total de Filmes", f"{total_filmes:,}")

st.markdown("---")

# --- Gráficos ---
st.subheader("📊 Análises Visuais")

col_g1, col_g2 = st.columns(2)

with col_g1:
    top_n = 10
    df_top_revenue = df_filtrado.sort_values(by="revenue", ascending=False).head(top_n)
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
        df_filtrado,
        x="score",
        nbins=20,
        title="Distribuição das Notas dos Filmes",
        labels={"score": "Nota", "count": "Frequência"}
    )
    st.plotly_chart(graf2, use_container_width=True)

col_g3, col_g4 = st.columns(2)

with col_g3:
    contagem_idiomas = df_filtrado["orig_lang"].value_counts().head(10).reset_index()
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
    revenue_country = df_filtrado.groupby("country")["revenue"].sum().reset_index()
    revenue_country.columns = ["country_raw", "Total Revenue"]

    # Detecta se 'country_raw' já está em ISO3
    sample_lengths = revenue_country["country_raw"].dropna().astype(str).apply(len)
    is_mostly_iso3 = False
    if not sample_lengths.empty:
        is_mostly_iso3 = (sample_lengths.median() == 3)

    if is_mostly_iso3:
        revenue_country["country_iso3"] = revenue_country["country_raw"].astype(str)
    else:
        # tenta converter ISO2 -> ISO3 se pycountry estiver disponível
        if HAS_PYCOUNTRY:
            def iso2_to_iso3(iso2):
                try:
                    if not isinstance(iso2, str):
                        return None
                    iso2 = iso2.strip()
                    if len(iso2) == 3:  # talvez já seja ISO3
                        return iso2.upper()
                    return pycountry.countries.get(alpha_2=iso2.upper()).alpha_3
                except Exception:
                    return None
            revenue_country["country_iso3"] = revenue_country["country_raw"].apply(iso2_to_iso3)
        else:
            # sem pycountry e sem ISO3 -> não conseguimos criar o mapa
            revenue_country["country_iso3"] = None

    revenue_country = revenue_country.dropna(subset=["country_iso3"])

    if revenue_country.empty:
        st.warning(
            "Não foi possível gerar o mapa de receita por país.\n"
            "- Se sua coluna 'country' contém códigos ISO2, instale o pacote 'pycountry' (adicione em requirements.txt) ou\n"
            "- forneça códigos ISO-3 na coluna 'country'."
        )
    else:
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
st.dataframe(df_filtrado)
