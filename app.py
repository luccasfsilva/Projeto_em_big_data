# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
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
# ESTILOS CSS PERSONALIZADOS
# =========================
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA726);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #8f8f8f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FFA726;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .metric-card-danger {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF6B6B;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        color: white;
        height: 100%;
    }
    .section-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #34495e;
    }
    .insight-box {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #FFA726;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .prediction-box {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4ECDC4;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CARREGAR E PREPROCESSAR DADOS
# =========================
@st.cache_data
def carregar_dados():
    CSV_URL = "https://raw.githubusercontent.com/luccasfsilva/projetopy/main/imdb_movies.csv"
    try:
        df = pd.read_csv(CSV_URL, parse_dates=['date_x'])
        
        # Limpeza e transformação mais robusta
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce").fillna(0)
        df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
        df["budget_x"] = pd.to_numeric(df.get("budget_x"), errors="coerce").fillna(0)
        
        # Extrair ano e mês
        df["ano"] = df["date_x"].dt.year.fillna(0).astype(int)
        df["mes"] = df["date_x"].dt.month.fillna(0).astype(int)
        
        # Calcular ROI (Return on Investment)
        df["roi"] = np.where(
            df["budget_x"] > 0,
            (df["revenue"] - df["budget_x"]) / df["budget_x"] * 100,
            0
        )
        
        # Categorizar sucesso
        conditions = [
            df['revenue'] >= df['revenue'].quantile(0.8),
            df['revenue'] >= df['revenue'].quantile(0.6),
            df['revenue'] >= df['revenue'].quantile(0.4),
            df['revenue'] < df['revenue'].quantile(0.4)
        ]
        choices = ['Blockbuster', 'High', 'Medium', 'Low']
        df['success_category'] = np.select(conditions, choices, default='Low')
        
        # Popularidade normalizada
        if 'vote_count' in df.columns:
            df['popularity_norm'] = (df['vote_count'] - df['vote_count'].min()) / (df['vote_count'].max() - df['vote_count'].min())
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar o CSV.\nDetalhe: {e}")
        st.stop()

df = carregar_dados()
if df is None:
    st.stop()

# =========================
# DICIONÁRIO DE TRADUÇÃO DOS FILMES (mantido do código anterior)
# =========================
TRADUCOES_FILMES = {
    # ... (mantenha o mesmo dicionário de traduções do código anterior)
}

def traduzir_nome_filme(nome_original):
    """Traduz o nome do filme para português"""
    if pd.isna(nome_original):
        return nome_original
    return TRADUCOES_FILMES.get(nome_original, nome_original)

# =========================
# FUNÇÕES DE ANÁLISE AVANÇADA
# =========================
def calcular_tendencia_anual(df, coluna):
    """Calcula tendência linear anual para uma coluna"""
    anual = df.groupby('ano')[coluna].mean().reset_index()
    if len(anual) > 1:
        X = anual['ano'].values.reshape(-1, 1)
        y = anual[coluna].values
        model = LinearRegression()
        model.fit(X, y)
        return model.coef_[0]  # Retorna a inclinação da tendência
    return 0

def prever_receita(modelo, features):
    """Função simplificada para prever receita"""
    try:
        return modelo.predict(features)[0]
    except:
        return 0

# =========================
# BARRA LATERAL AVANÇADA
# =========================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #4ECDC4;'>🎛️ Painel de Controle Avançado</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtro de anos
    st.markdown("#### 📅 Filtro por Ano")
    anos_disponiveis = sorted(df["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Selecione o intervalo de anos:",
        options=anos_disponiveis,
        value=(min(anos_disponiveis), max(anos_disponiveis)),
        help="Filtre os filmes por ano de lançamento"
    )
    
    st.markdown("---")
    
    # Filtros múltiplos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⭐ Filtro por Nota")
        score_min, score_max = st.slider(
            "Nota IMDb:",
            min_value=0.0,
            max_value=10.0,
            value=(0.0, 10.0),
            step=0.1,
            help="Filtre os filmes pela nota no IMDb"
        )
    
    with col2:
        st.markdown("#### 💰 Filtro por ROI")
        roi_min, roi_max = st.slider(
            "ROI (%):",
            min_value=-100.0,
            max_value=1000.0,
            value=(-100.0, 1000.0),
            step=50.0,
            help="Retorno sobre Investimento"
        )
    
    st.markdown("---")
    
    # Filtro por categoria de sucesso
    st.markdown("#### 🏆 Categoria de Sucesso")
    categorias = st.multiselect(
        "Selecione as categorias:",
        options=['Blockbuster', 'High', 'Medium', 'Low'],
        default=['Blockbuster', 'High', 'Medium', 'Low'],
        help="Filtre pela categoria de sucesso financeiro"
    )
    
    st.markdown("---")
    
    # Análise rápida
    with st.expander("🔍 Análise Rápida"):
        if st.button("Calcular Insights Automáticos"):
            st.session_state.calcular_insights = True

# Aplicar filtro principal
df_filtrado = df[
    (df["ano"] >= ano_min) &
    (df["ano"] <= ano_max) &
    (df["score"] >= score_min) &
    (df["score"] <= score_max) &
    (df["roi"] >= roi_min) &
    (df["roi"] <= roi_max) &
    (df['success_category'].isin(categorias))
]

# Aplicar tradução aos nomes dos filmes
df_filtrado = df_filtrado.copy()
df_filtrado["names"] = df_filtrado["names"].apply(traduzir_nome_filme)

# =========================
# CABEÇALHO E MÉTRICAS PRINCIPAIS
# =========================
st.markdown('<h1 class="main-header">🎬 CineAnalytics Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dashboard Avançado de Análise Cinematográfica com IA</p>', unsafe_allow_html=True)

# Métricas principais expandidas
if not df_filtrado.empty:
    receita_total = df_filtrado["revenue"].sum()
    receita_media = df_filtrado["revenue"].mean()
    nota_media = df_filtrado["score"].mean(skipna=True)
    total_filmes = df_filtrado.shape[0]
    roi_medio = df_filtrado["roi"].mean()
    orcamento_medio = df_filtrado["budget_x"].mean()
    
    # Análises avançadas
    tendencia_receita = calcular_tendencia_anual(df_filtrado, 'revenue')
    tendencia_nota = calcular_tendencia_anual(df_filtrado, 'score')
    blockbusters = df_filtrado[df_filtrado['success_category'] == 'Blockbuster'].shape[0]
else:
    receita_total = receita_media = nota_media = total_filmes = roi_medio = orcamento_medio = 0
    tendencia_receita = tendencia_nota = blockbusters = 0

# Primeira linha de métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Receita Total", f"${receita_total:,.0f}", 
             f"{tendencia_receita:+.1f}%/ano" if tendencia_receita != 0 else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Receita Média", f"${receita_media:,.0f}", 
             help="Receita média por filme")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⭐ Nota Média", f"{nota_media:.2f}" if pd.notna(nota_media) else "—",
             f"{tendencia_nota:+.2f}/ano" if tendencia_nota != 0 else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎭 Total de Filmes", f"{total_filmes:,}", 
             help="Número total de filmes que correspondem aos filtros")
    st.markdown('</div>', unsafe_allow_html=True)

# Segunda linha de métricas avançadas
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("📈 ROI Médio", f"{roi_medio:.1f}%", 
             help="Retorno sobre Investimento médio")
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💸 Orçamento Médio", f"${orcamento_medio:,.0f}" if orcamento_medio > 0 else "N/A",
             help="Orçamento médio dos filmes")
    st.markdown('</div>', unsafe_allow_html=True)

with col7:
    st.markdown('<div class="metric-card-warning">', unsafe_allow_html=True)
    st.metric("🏆 Blockbusters", f"{blockbusters:,}",
             help="Filmes na categoria Blockbuster")
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    st.markdown('<div class="metric-card-danger">', unsafe_allow_html=True)
    eficiencia = receita_total / max(orcamento_medio * total_filmes, 1)
    st.metric("⚡ Eficiência", f"{eficiencia:.2f}x",
             help="Relação Receita/Orçamento")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# SISTEMA DE ABAS AVANÇADO
# =========================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard Principal", 
    "🎭 Análise de Performance", 
    "📈 Tendências & Previsões",
    "🔍 Insights Avançados",
    "🏆 Benchmarking",
    "📋 Base de Dados"
])

with tab1:
    st.markdown('<div class="section-header">📊 Visão Geral do Mercado</div>', unsafe_allow_html=True)
    
    # Análise de correlação em tempo real
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de dispersão multivariado
        fig_scatter = px.scatter(
            df_filtrado,
            x="score",
            y="revenue",
            size="budget_x",
            color="success_category",
            title="🎯 Relação: Nota vs Receita vs Orçamento",
            labels={"score": "Nota IMDb", "revenue": "Receita", "budget_x": "Orçamento"},
            hover_data=["names", "ano", "roi"],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Distribuição de ROI
        fig_roi = px.histogram(
            df_filtrado,
            x="roi",
            nbins=50,
            title="📊 Distribuição de ROI (Return on Investment)",
            labels={"roi": "ROI (%)"},
            color_discrete_sequence=['#FFA726']
        )
        fig_roi.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Mapa de calor de correlações
        numeric_cols = df_filtrado.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df_filtrado[numeric_cols].corr()
            fig_heatmap = px.imshow(
                corr_matrix,
                title="🔥 Mapa de Correlações (Matriz Completa)",
                color_continuous_scale="RdBu_r",
                aspect="auto",
                text_auto=True
            )
            fig_heatmap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Evolução temporal múltipla
        evolucao_anual = df_filtrado.groupby('ano').agg({
            'revenue': 'mean',
            'score': 'mean',
            'roi': 'mean'
        }).reset_index()
        
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_anual['ano'], 
            y=evolucao_anual['revenue'],
            name='Receita Média',
            line=dict(color='#4ECDC4', width=3)
        ))
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao_anual['ano'], 
            y=evolucao_anual['score'] * (evolucao_anual['revenue'].max() / evolucao_anual['score'].max()),
            name='Nota Média (escala ajustada)',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig_evolucao.update_layout(
            title="📈 Evolução Comparativa: Receita vs Nota",
            xaxis_title="Ano",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">🎭 Análise de Performance Detalhada</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top filmes por ROI
        st.markdown("#### 💰 Melhores Investimentos (ROI)")
        top_roi = df_filtrado.nlargest(10, 'roi')[['names', 'roi', 'revenue', 'budget_x']]
        top_roi['ROI'] = top_roi['roi'].apply(lambda x: f"{x:.1f}%")
        top_roi['Receita'] = top_roi['revenue'].apply(lambda x: f"${x:,.0f}")
        top_roi['Orçamento'] = top_roi['budget_x'].apply(lambda x: f"${x:,.0f}" if x > 0 else "N/A")
        st.dataframe(top_roi[['names', 'ROI', 'Receita', 'Orçamento']].rename(
            columns={'names': 'Filme'}), use_container_width=True)
    
    with col2:
        # Performance por categoria de sucesso
        st.markdown("#### 🏆 Distribuição por Categoria")
        success_dist = df_filtrado['success_category'].value_counts()
        fig_pie_success = px.pie(
            values=success_dist.values,
            names=success_dist.index,
            title="Distribuição de Categorias de Sucesso",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie_success, use_container_width=True)
    
    # Análise de eficiência
    st.markdown("#### ⚡ Análise de Eficiência: Receita vs Orçamento")
    fig_efficiency = px.scatter(
        df_filtrado,
        x="budget_x",
        y="revenue",
        color="success_category",
        size="score",
        title="Eficiência: Receita Gerada vs Orçamento Investido",
        labels={"budget_x": "Orçamento", "revenue": "Receita"},
        hover_data=["names", "roi"]
    )
    fig_efficiency.add_shape(
        type="line", line=dict(dash="dash", color="white"),
        x0=0, y0=0, x1=df_filtrado['budget_x'].max(), 
        y1=df_filtrado['budget_x'].max()
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">📈 Análise Preditiva e Tendências</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔮 Simulador de Performance")
        
        with st.form("simulador_performance"):
            st.markdown("##### Parâmetros do Filme")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                orcamento_simulado = st.number_input("Orçamento (USD)", 
                                                   min_value=1000000, 
                                                   max_value=500000000,
                                                   value=100000000,
                                                   step=1000000)
                nota_esperada = st.slider("Nota IMDb Esperada", 0.0, 10.0, 7.0, 0.1)
            
            with col_s2:
                mes_lancamento = st.selectbox("Mês de Lançamento", 
                                            range(1, 13),
                                            format_func=lambda x: datetime(2020, x, 1).strftime('%B'))
                categoria_genero = st.selectbox("Gênero Principal", 
                                              df_filtrado['genre'].value_counts().head(10).index.tolist())
            
            submitted = st.form_submit_button("🎯 Calcular Previsão")
            
            if submitted:
                # Cálculo simplificado baseado em médias históricas
                similar_movies = df_filtrado[
                    (df_filtrado['score'].between(nota_esperada-1, nota_esperada+1)) &
                    (df_filtrado['budget_x'].between(orcamento_simulado*0.5, orcamento_simulado*1.5))
                ]
                
                if not similar_movies.empty:
                    receita_estimada = similar_movies['revenue'].mean()
                    roi_estimado = (receita_estimada - orcamento_simulado) / orcamento_simulado * 100
                    
                    st.markdown(f'<div class="prediction-box">', unsafe_allow_html=True)
                    st.metric("💰 Receita Estimada", f"${receita_estimada:,.0f}")
                    st.metric("📈 ROI Estimado", f"{roi_estimado:.1f}%")
                    st.metric("🎯 Categoria Prevista", 
                             "Blockbuster" if receita_estimada > df_filtrado['revenue'].quantile(0.8) else "Alto Sucesso")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📊 Tendências Temporais Avançadas")
        
        # Tendência de ROI ao longo do tempo
        roi_temporal = df_filtrado.groupby('ano')['roi'].mean().reset_index()
        fig_roi_trend = px.line(
            roi_temporal,
            x='ano',
            y='roi',
            title="📈 Evolução do ROI Médio Anual",
            markers=True
        )
        fig_roi_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_roi_trend, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">🔍 Insights e Recomendações</div>', unsafe_allow_html=True)
    
    # Insights automáticos
    st.markdown("#### 💡 Insights Automáticos")
    
    # Insight 1: Melhor custo-benefício
    if not df_filtrado.empty:
        melhor_custo_beneficio = df_filtrado.loc[df_filtrado['roi'].idxmax()]
        pior_custo_beneficio = df_filtrado.loc[df_filtrado[df_filtrado['roi'] > -100]['roi'].idxmin()]
        
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"##### 🏆 Melhor Investimento")
            st.markdown(f"**{melhor_custo_beneficio['names']}**")
            st.markdown(f"ROI: **{melhor_custo_beneficio['roi']:.1f}%**")
            st.markdown(f"Nota: **{melhor_custo_beneficio['score']:.1f}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_i2:
            st.markdown(f'<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"##### ⚠️ Investimento de Risco")
            st.markdown(f"**{pior_custo_beneficio['names']}**")
            st.markdown(f"ROI: **{pior_custo_beneficio['roi']:.1f}%**")
            st.markdown(f"Nota: **{pior_custo_beneficio['score']:.1f}**")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise de sazonalidade
    st.markdown("#### 📅 Análise de Sazonalidade")
    if 'mes' in df_filtrado.columns:
        sazonalidade = df_filtrado.groupby('mes').agg({
            'revenue': 'mean',
            'score': 'mean',
            'roi': 'mean'
        }).reset_index()
        
        fig_sazonal = go.Figure()
        fig_sazonal.add_trace(go.Bar(
            x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec'],
            y=sazonalidade['revenue'],
            name='Receita Média',
            marker_color='#4ECDC4'
        ))
        fig_sazonal.update_layout(
            title="Receita Média por Mês",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_sazonal, use_container_width=True)

with tab5:
    st.markdown('<div class="section-header">🏆 Benchmarking e Comparações</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Benchmark por gênero
        st.markdown("#### 🎭 Performance por Gênero")
        genre_benchmark = df_filtrado.groupby('genre').agg({
            'revenue': 'mean',
            'score': 'mean',
            'roi': 'mean',
            'names': 'count'
        }).round(2).nlargest(10, 'revenue')
        
        st.dataframe(genre_benchmark.rename(columns={
            'revenue': 'Receita Média',
            'score': 'Nota Média',
            'roi': 'ROI Médio',
            'names': 'Nº Filmes'
        }), use_container_width=True)
    
    with col2:
        # Comparação de décadas
        st.markdown("#### 📊 Evolução por Década")
        df_filtrado['decada'] = (df_filtrado['ano'] // 10) * 10
        decada_stats = df_filtrado.groupby('decada').agg({
            'revenue': 'mean',
            'score': 'mean',
            'budget_x': 'mean'
        }).reset_index()
        
        fig_decada = px.line(
            decada_stats,
            x='decada',
            y=['revenue', 'budget_x'],
            title="Evolução da Receita e Orçamento por Década",
            markers=True
        )
        st.plotly_chart(fig_decada, use_container_width=True)

with tab6:
    st.markdown('<div class="section-header">🔍 Base de Dados Completa</div>', unsafe_allow_html=True)
    
    # Sistema de busca e filtros (similar ao anterior, mas expandido)
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        search_term = st.text_input("🔍 Buscar filme:", placeholder="Digite o nome do filme...")
    with col_f2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Receita", "Pontuação", "ROI", "Orçamento", "Ano de Lançamento"],
            index=0
        )
    with col_f3:
        resultados_por_pagina = st.selectbox("Itens por página:", [10, 25, 50, 100], index=0)
    
    # Preparar dados para exibição (similar ao anterior, mas com mais colunas)
    # ... (código similar ao tab4 do código anterior, mas com colunas adicionais como ROI, Orçamento, etc.)

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>"
    f"📊 Dashboard CineAnalytics Pro • Análise Avançada com IA • "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} • "
    f"💡 {len(df_filtrado):,} filmes analisados"
    f"</div>",
    unsafe_allow_html=True
)
