# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Filmes", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- tentativa de importar pycountry ---
try:
    import pycountry
    HAS_PYCOUNTRY = True
except Exception:
    pycountry = None
    HAS_PYCOUNTRY = False

# --- Carregar os dados (função com cache) ---
@st.cache_data
def carregar_dados():
    """Carrega os dados do CSV e faz o pré-processamento."""
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        
        # Garantir tipos corretos e tratar valores ausentes
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        
        # Extrair o ano da coluna 'date_x'
        df['ano'] = df['date_x'].dt.year.fillna(0).astype(int)
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo CSV. Verifique a URL ou se o arquivo existe.\nDetalhe: {e}")
        st.stop()
        return None

df = carregar_dados()
if df is None:
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

anos_disponiveis = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Ano(s):",
    options=anos_disponiveis,
    default=anos_disponiveis
)

if not anos_selecionados:
    df_filtrado = df.copy()
else:
    df_filtrado = df[df["ano"].isin(anos_selecionados)]

# --- Título principal ---
st.title("🎬 Dashboard de Filmes")

# --- Indicadores principais (KPIs) ---
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
    df_top = df_filtrado.sort_values(by="revenue", ascending=False).head(top_n)
    graf1 = px.bar(
        df_top,
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
        title="Distribuição das Notas",
        labels={"score": "Nota", "count": "Quantidade"}
    )
    st.plotly_chart(graf2, use_container_width=True)

col_g3, col_g4 = st.columns(2)

with col_g3:
    contagem_idiomas = df_filtrado["orig_lang"].value_counts().head(10).reset_index()
    contagem_idiomas.columns = ["Idioma Original", "Quantidade de Filmes"]
    graf3 = px.pie(
        contagem_idiomas,
        values="Quantidade de Filmes",
        names="Idioma Original",
        title="Top 10 Idiomas Originais",
        hole=0.3
    )
    st.plotly_chart(graf3, use_container_width=True)

with col_g4:
    receita_pais = df_filtrado.groupby("country")["revenue"].sum().reset_index()
    receita_pais.columns = ["country_raw", "Receita Total"]

    sample_lengths = receita_pais["country_raw"].dropna().astype(str).apply(len)
    is_mostly_iso3 = False
    if not sample_lengths.empty:
        is_mostly_iso3 = (sample_lengths.median() == 3)

    if is_mostly_iso3:
        receita_pais["country_iso3"] = receita_pais["country_raw"].astype(str)
    else:
        if HAS_PYCOUNTRY:
            def iso2_para_iso3(iso2):
                try:
                    if not isinstance(iso2, str):
                        return None
                    iso2 = iso2.strip()
                    if len(iso2) == 3:
                        return iso2.upper()
                    return pycountry.countries.get(alpha_2=iso2.upper()).alpha_3
                except Exception:
                    return None
            receita_pais["country_iso3"] = receita_pais["country_raw"].apply(iso2_para_iso3)
        else:
            receita_pais["country_iso3"] = None

    receita_pais = receita_pais.dropna(subset=["country_iso3"])

    if receita_pais.empty:
        st.warning(
            "⚠️ Não foi possível gerar o mapa de receita por país.\n"
            "- Se sua coluna 'country' contém códigos ISO2, instale o pacote 'pycountry' (adicione em requirements.txt) ou\n"
            "- forneça códigos ISO-3 na coluna 'country'."
        )
    else:
        graf4 = px.choropleth(
            receita_pais,
            locations="country_iso3",
            color="Receita Total",
            color_continuous_scale="Plasma",
            title="Receita Total por País",
            labels={"Receita Total": "Receita", "country_iso3": "País"}
        )
        st.plotly_chart(graf4, use_container_width=True)

st.markdown("---")

# --- Tabela completa ---
st.subheader("📋 Dados dos Filmes")
st.dataframe(df_filtrado)
