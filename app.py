import altair as alt
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Avaliação de Carros — Correlação e Distribuição (Car Evaluation)",
    layout="wide",
)

st.title("Avaliação de carros — correlação e distribuição das variáveis quantitativas")

df = load_data()

# Variáveis quantitativas do estudo: as colunas numéricas do dataset tratado,
# ou seja, a codificação ordinal (_cod) gerada no notebook de EDA, mais o
# avaliacao_cod derivado no data_loader. Nenhuma coluna qualitativa entra.
VARS_QUANTITATIVAS = df.select_dtypes(include="number").columns.tolist()

# Série única: a cor não codifica nada, só precisa de contraste sobre o fundo
# (>= 3:1 no tema claro e no escuro)
COR_BARRA = "#d95926"

# Sidebar: filtros
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=VARS_QUANTITATIVAS,
        default=VARS_QUANTITATIVAS,
        help="Selecione as variáveis quantitativas que deseja analisar no dashboard.",
    )

    # Um slider de intervalo para cada variável quantitativa selecionada.
    # Os limites vêm do dataset inteiro, então a faixa não encolhe conforme
    # os outros filtros vão cortando linhas.
    intervalos = {}
    for variavel in variaveis:
        minimo, maximo = int(df[variavel].min()), int(df[variavel].max())
        intervalos[variavel] = st.slider(
            f"Intervalo de {variavel}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            key=f"intervalo_{variavel}",
        )

# Mantém só os carros dentro de todas as faixas escolhidas
df_filtrado = df
for variavel, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[variavel].between(inicio, fim)]

st.caption(f"{len(df_filtrado)} de {len(df)} carros dentro das faixas escolhidas.")

# Dashboard 1: Correlação (topo) e Distribuição (abaixo), ambos em largura total
st.subheader("Correlação")

if len(variaveis) < 2:
    st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
else:
    # Spearman: adequado para variáveis ordinais (ver notebook de EDA)
    corr = df_filtrado[variaveis].corr(method="spearman")

    # Formato longo, que é o que o Altair consome
    corr_longo = corr.reset_index(names="linha").melt(
        id_vars="linha", var_name="coluna", value_name="rho"
    )
    # Correlação exatamente zero às vezes sai como -1e-17 e o rótulo vira
    # "-0.00"; o + 0.0 normaliza o zero negativo
    corr_longo["rho"] = corr_longo["rho"].round(10) + 0.0

    # A matriz é simétrica: fica só o triângulo superior (sem a diagonal, que
    # é sempre 1.0), para não repetir cada par duas vezes
    posicao = {variavel: i for i, variavel in enumerate(variaveis)}
    corr_longo = corr_longo[
        corr_longo["linha"].map(posicao) < corr_longo["coluna"].map(posicao)
    ]

    base = alt.Chart(corr_longo).encode(
        x=alt.X("coluna:N", sort=variaveis, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("linha:N", sort=variaveis, title=None),
    )
    mapa = base.mark_rect().encode(
        color=alt.Color(
            "rho:Q",
            scale=alt.Scale(scheme="redblue", domain=[-1, 1]),
            title="Spearman",
        ),
        tooltip=[
            alt.Tooltip("linha:N", title="Variável"),
            alt.Tooltip("coluna:N", title="Variável"),
            alt.Tooltip("rho:Q", title="Spearman", format=".3f"),
        ],
    )
    # Rótulo em branco onde o fundo é escuro (as pontas da escala)
    rotulos = base.mark_text(fontSize=13).encode(
        text=alt.Text("rho:Q", format=".2f"),
        color=alt.condition(
            "abs(datum.rho) > 0.5", alt.value("white"), alt.value("black")
        ),
    )

    st.altair_chart(
        (mapa + rotulos).properties(height=70 * (len(variaveis) - 1)),
        width="stretch",
        alt="Matriz de correlação de Spearman entre as variáveis quantitativas, "
        "com apenas o triângulo superior preenchido.",
    )

st.subheader("Distribuição")

if not variaveis:
    st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
else:
    # Um gráfico de distribuição para cada variável quantitativa, numa grade
    # de duas colunas. Formato longo + facet: o Altair repete o mesmo gráfico
    # para cada variável.
    dist_longo = df_filtrado[variaveis].melt(var_name="variavel", value_name="valor")

    grafico_dist = (
        alt.Chart(dist_longo)
        .mark_bar(color=COR_BARRA)
        .encode(
            # Os códigos são inteiros com poucos níveis: uma barra por código
            x=alt.X("valor:O", title=None),
            y=alt.Y("count():Q", title="Carros"),
            tooltip=[
                alt.Tooltip("valor:O", title="Código"),
                alt.Tooltip("count():Q", title="Carros"),
            ],
        )
        .properties(width=430, height=200)
        .facet(alt.Facet("variavel:N", title=None, sort=variaveis), columns=2)
        # Cada variável tem a sua própria faixa de códigos e a sua contagem
        .resolve_scale(x="independent", y="independent")
    )

    st.altair_chart(
        grafico_dist,
        width="content",
        alt="Grade de gráficos de barras com a distribuição de frequência de "
        "cada variável quantitativa.",
    )

# TODO: Dashboard 2 — KPIs (Aula 22)
