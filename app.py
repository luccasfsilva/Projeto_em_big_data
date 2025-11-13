# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    .stMetric {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# TENTATIVA DE IMPORTAR PYCOUNTRY
# =========================
try:
    import pycountry
    HAS_PYCOUNTRY = True
except Exception:
    pycountry = None
    HAS_PYCOUNTRY = False

# =========================
# FUNÇÃO PARA CARREGAR OS DADOS
# =========================
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

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.header("🎛️ Painel de Controle")
    
    # Filtro de anos
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o Intervalo de Anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis))
    )
    
    # Filtro de score
    score_min, score_max = st.slider(
        "Filtrar por Nota:",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=0.1
    )
    
    # Filtro de receita
    receita_max = df["revenue"].max()
    receita_min, receita_max = st.slider(
        "Filtrar por Receita:",
        min_value=0.0,
        max_value=float(receita_max),
        value=(0.0, float(receita_max)),
        step=1000000.0,
        format="$%.0f"
    )

# Aplicar filtros
df_filtrado = df[
    (df["ano"] >= ano_min) & 
    (df["ano"] <= ano_max) &
    (df["score"] >= score_min) & 
    (df["score"] <= score_max) &
    (df["revenue"] >= receita_min) & 
    (df["revenue"] <= receita_max)
]

# =========================
# HEADER
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics </h1>', unsafe_allow_html=True)

# =========================
# MÉTRICAS (KPI CARDS)
# =========================
if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Receita Média", f"${receita_media:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⭐ Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—")
    st.markdown('</div>', unsafe_allow_html=True)
    
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎭 Total de Filmes", f"{total_filmes:,}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# GRÁFICOS INTERATIVOS
# =========================
st.subheader("📈 Análises Visuais Interativas")

col_g1, col_g2 = st.columns(2)

# Gráfico 1 — Top filmes por receita
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

# Gráfico 2 — Dispersão: Receita vs Nota
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

# Gráfico 3 — Evolução temporal
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

# Gráfico 4 — Pizza de idiomas
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
# MAPA INTERATIVO
# =========================
st.subheader("📋 Base de Dados Completa")

with st.expander("Explorar Dados dos Filmes", expanded=False):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_term = st.text_input("🔍 Buscar pelo nome do filme:")
    with col_f2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "Ano"],
            index=0
        )

    # Cria uma cópia do DataFrame filtrado
    df_display = df_filtrado.copy()

    # Traduz os nomes das colunas para português (ajuste conforme seus dados)
    df_display = df_display.rename(columns={
        "names": "Nome do Filme",
        "revenue": "Receita",
        "score": "Pontuação",
        "ano": "Ano"
    })

    # Converte coluna de ano para data no formato dd/mm/aaaa
    if "Ano" in df_display.columns:
        df_display["Ano"] = pd.to_datetime(df_display["Ano"], errors='coerce').dt.strftime("%d/%m/%Y")

    # Busca por nome
    if search_term:
        df_display = df_display[df_display["Nome do Filme"].str.contains(search_term, case=False, na=False)]

    # Ordenação
    sort_map = {"Receita": "Receita", "Pontuação": "Pontuação", "Ano": "Ano"}
    if sort_by in sort_map and sort_map[sort_by] in df_display.columns:
        df_display = df_display.sort_values(by=sort_map[sort_by], ascending=False)

    # Exibição
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    else:
        fig5 = px.choropleth(
            receita_pais,
            locations="country_iso3",
            color="Receita Total",
            color_continuous_scale="tealrose",
            title="🌍 Receita Total por País",
            hover_name="country_raw",
            projection="natural earth"
        )
        fig5.update_layout(height=500)
        st.plotly_chart(fig5, use_container_width=True)

# =========================
# TABELA INTERATIVA — CORRIGIDA
# =========================
st.subheader("📋 Base de Dados Completa")

with st.expander("Explorar Dados dos Filmes", expanded=False):
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        search_term = st.text_input("🔍 Buscar pelo nome do filme:")

    with col_f2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "Ano"],
            index=0
        )

    # Cria uma cópia do DataFrame filtrado
    df_display = df_filtrado.copy()

    # Renomeia colunas para português (ajuste conforme as colunas reais)
    df_display = df_display.rename(columns={
        "names": "Nome do Filme",
        "revenue": "Receita",
        "score": "Pontuação",
        "ano": "Ano"
    })

    # Converte coluna de ano para o formato dd/mm/aaaa (caso seja numérica)
    if "Ano" in df_display.columns:
        try:
            df_display["Ano"] = pd.to_datetime(df_display["Ano"].astype(str), errors='coerce').dt.strftime("%d/%m/%Y")
        except Exception as e:
            st.warning(f"Erro ao formatar a data: {e}")

    # Filtro de busca
    if search_term:
        df_display = df_display[df_display["Nome do Filme"].str.contains(search_term, case=False, na=False)]

    # Ordenação
    sort_map = {
        "Receita": "Receita",
        "Pontuação": "Pontuação",
        "Ano": "Ano"
    }

    if sort_by in sort_map and sort_map[sort_by] in df_display.columns:
        df_display = df_display.sort_values(by=sort_map[sort_by], ascending=False)

    # Exibe tabela formatada
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )


# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "📊 Dashboard desenvolvido com Streamlit • "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>",
    unsafe_allow_html=True
)
