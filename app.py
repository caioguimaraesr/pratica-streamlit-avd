import plotly.express as px
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Avaliação de Carros — Correlação e Distribuição (Car Evaluation)",
    layout="wide",
)

st.title("Avaliação de Carros — Correlação e Distribuição das Variáveis Ordinais")

df = load_data()

# Variáveis ordinais do estudo, com as categorias em ordem crescente
# (mesma ORDEM_CATEGORIAS do notebook de EDA)
ORDEM_CATEGORIAS = {
    "buying": ["low", "med", "high", "vhigh"],
    "maint": ["low", "med", "high", "vhigh"],
    "doors": ["2", "3", "4", "5more"],
    "persons": ["2", "4", "more"],
    "lug_boot": ["small", "med", "big"],
    "safety": ["low", "med", "high"],
}
VARS_ORDINAIS_COD = [f"{col}_cod" for col in ORDEM_CATEGORIAS]

# Sidebar: filtros
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis (codificação ordinal)",
        options=VARS_ORDINAIS_COD,
        default=VARS_ORDINAIS_COD,
        help="Selecione as variáveis ordinais codificadas que deseja analisar no dashboard.",
    )

    separar_por_classe = st.toggle(
        "Distinguir por Avaliação",
        value=False,
        help="Colore a distribuição pela avaliação do carro (Aceitável ou Não Aceitável).",
    )

    # Um select_slider de intervalo de categorias para cada variável selecionada
    intervalos = {}
    for col, ordem in ORDEM_CATEGORIAS.items():
        if f"{col}_cod" in variaveis:
            intervalos[col] = st.select_slider(
                f"Intervalo de {col}",
                options=ordem,
                value=(ordem[0], ordem[-1]),
                key=f"intervalo_{col}",
            )

# Mantém só os carros dentro de todas as faixas de categorias escolhidas
df_filtrado = df
for col, (inicio, fim) in intervalos.items():
    ordem = ORDEM_CATEGORIAS[col]
    faixa = ordem[ordem.index(inicio) : ordem.index(fim) + 1]
    df_filtrado = df_filtrado[df_filtrado[col].isin(faixa)]

st.caption(f"{len(df_filtrado)} de {len(df)} carros dentro das faixas escolhidas.")

# Dashboard 1: Correlação (topo) e Distribuição (abaixo), ambos em largura total
st.subheader("Correlação")

if len(variaveis) < 2:
    st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
else:
    # Spearman: adequado para variáveis ordinais (ver notebook de EDA)
    corr = df_filtrado[variaveis].corr(method="spearman")
    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

st.subheader("Distribuição")

if not variaveis:
    st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
else:
    variavel_dist = st.selectbox("Variável", options=variaveis)
    coluna_original = variavel_dist.removesuffix("_cod")

    # Variáveis categóricas: distribuição = gráfico de barras de frequência
    fig_dist = px.histogram(
        df_filtrado,
        x=coluna_original,
        color="avaliacao" if separar_por_classe else None,
        category_orders={coluna_original: ORDEM_CATEGORIAS[coluna_original]},
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# TODO: Dashboard 2 — KPIs (Aula 22)
