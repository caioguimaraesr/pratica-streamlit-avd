import altair as alt
import streamlit as st

from src.data_loader import ORDEM_AVALIACAO, load_data

st.set_page_config(
    page_title="Avaliação de Carros — Correlação e Distribuição (Car Evaluation)",
    layout="wide",
)

st.title("Avaliação de carros (Car Evaluation)")

df = load_data()

# Variáveis quantitativas do estudo: as colunas numéricas do dataset tratado,
# ou seja, a codificação ordinal (_cod) gerada no notebook de EDA, mais o
# avaliacao_cod derivado no data_loader. Nenhuma coluna qualitativa entra.
VARS_QUANTITATIVAS = df.select_dtypes(include="number").columns.tolist()

# Atributos categóricos originais do carro (sem a codificação _cod), usados
# como widgets de segmentação no Dashboard 2.
ATRIBUTOS_CATEGORICOS = ["buying", "maint", "doors", "persons", "lug_boot", "safety"]

# Cores da distribuição por avaliação do carro — clara para o desfecho bom,
# escura para o ruim, com contraste suficiente nos dois temas (claro/escuro)
CORES_AVALIACAO = {
    "Aceitável": "#f2a65a",
    "Não Aceitável": "#9e2a2b",
}

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

tab_dashboard1, tab_dashboard2 = st.tabs(
    ["Dashboard 1 — Correlação e distribuição", "Dashboard 2 — KPIs"]
)

with tab_dashboard1:
    st.caption(f"{len(df_filtrado)} de {len(df)} carros dentro das faixas escolhidas.")

    # Dashboard 1: Correlação (topo) e Distribuição (abaixo), ambos em largura total
    st.subheader("Correlação")

    if df_filtrado.empty:
        st.warning("Nenhum carro dentro das faixas escolhidas. Amplie os intervalos para ver a correlação.")
    elif len(variaveis) < 2:
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

    if df_filtrado.empty:
        st.warning("Nenhum carro dentro das faixas escolhidas. Amplie os intervalos para ver a distribuição.")
    elif not variaveis:
        st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
    else:
        # Os seis atributos são uniformes por construção (o dataset é um
        # fatorial completo: toda combinação de categorias aparece o mesmo
        # número de vezes). Colorir por avaliação é o que revela um padrão real
        # — ex.: safety_cod=0 nunca é aceitável.
        st.caption(
            "Os atributos do carro têm a mesma contagem em cada nível (dataset "
            "fatorial completo); o padrão aparece na composição por avaliação."
        )

        # Um gráfico de distribuição para cada variável quantitativa, numa grade
        # de duas colunas. Formato longo + facet: o Altair repete o mesmo gráfico
        # para cada variável.
        dist_longo = df_filtrado[variaveis + ["avaliacao"]].melt(
            id_vars="avaliacao", var_name="variavel", value_name="valor"
        )

        grafico_dist = (
            alt.Chart(dist_longo)
            .mark_bar(opacity=0.75)
            .encode(
                # Os códigos são inteiros com poucos níveis: uma barra por código
                x=alt.X("valor:O", title=None),
                # stack=None sobrepõe as duas classes (em vez de empilhar), para
                # comparar as alturas diretamente, como no gráfico de referência
                y=alt.Y("count():Q", title="Carros", stack=None),
                color=alt.Color(
                    "avaliacao:N",
                    title="Avaliação",
                    scale=alt.Scale(
                        domain=list(CORES_AVALIACAO),
                        range=list(CORES_AVALIACAO.values()),
                    ),
                ),
                tooltip=[
                    alt.Tooltip("valor:O", title="Código"),
                    alt.Tooltip("avaliacao:N", title="Avaliação"),
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
            "cada variável quantitativa, sobrepondo a contagem de carros "
            "aceitáveis e não aceitáveis.",
        )

with tab_dashboard2:
    st.subheader("KPIs de aceitabilidade")

    col_atributo, col_niveis = st.columns(2)
    with col_atributo:
        atributo_kpi = st.selectbox(
            "Agrupar por",
            options=ATRIBUTOS_CATEGORICOS,
            help="Atributo do carro usado para segmentar as métricas abaixo.",
        )
    with col_niveis:
        niveis_disponiveis = sorted(df[atributo_kpi].unique().tolist())
        niveis_selecionados = st.multiselect(
            f"Níveis de {atributo_kpi}",
            options=niveis_disponiveis,
            default=niveis_disponiveis,
            help="Níveis do atributo escolhido que entram no segmento comparado.",
        )

    df_segmento = (
        df[df[atributo_kpi].isin(niveis_selecionados)]
        if niveis_selecionados
        else df.iloc[0:0]
    )
    total_geral = len(df)

    taxa_geral = (df["avaliacao"] == "Aceitável").mean() * 100
    pct_vgood_geral = (df["avaliacao_4"] == "vgood").mean() * 100

    # Atributo mais associado à avaliação: maior |correlação de Spearman| com
    # avaliacao_cod, reaproveitando a mesma lógica do Dashboard 1.
    cod_cols = [c for c in VARS_QUANTITATIVAS if c != "avaliacao_cod"]
    corr_avaliacao = df[cod_cols + ["avaliacao_cod"]].corr(method="spearman")["avaliacao_cod"].drop("avaliacao_cod")
    atributo_top = corr_avaliacao.abs().idxmax()
    valor_top = corr_avaliacao[atributo_top]

    # Reserva o espaço dos cartões de KPI ACIMA do gráfico (a ordem visual não
    # segue a ordem de execução: o clique no gráfico, lido mais abaixo, pode
    # refinar esses números).
    metricas_container = st.container()

    st.subheader("Carros por nível e distribuição da avaliação")
    st.caption(
        "Clique numa barra do gráfico à esquerda para refinar as métricas acima "
        "e destacar a distribuição da avaliação à direita."
    )

    df_metricas = df_segmento

    if df_segmento.empty:
        st.warning("Nenhum carro no segmento escolhido. Ajuste os níveis selecionados.")
    else:
        # Seleção por clique: liga os dois gráficos (Altair) e, via on_select,
        # chega até o Python para refinar as métricas (ver ALTAIR-CROSSFILTER.md).
        clique = alt.selection_point(name="clique", fields=[atributo_kpi])

        grafico_niveis = (
            alt.Chart(df_segmento)
            .mark_bar()
            .encode(
                x=alt.X(f"{atributo_kpi}:N", sort=niveis_selecionados, title=atributo_kpi),
                y=alt.Y("count():Q", title="Carros"),
                opacity=alt.condition(clique, alt.value(1), alt.value(0.35)),
                tooltip=[
                    alt.Tooltip(f"{atributo_kpi}:N", title=atributo_kpi),
                    alt.Tooltip("count():Q", title="Carros"),
                ],
            )
            .add_params(clique)
            .properties(title="Carros por nível selecionado", width=320, height=260)
        )

        grafico_avaliacao = (
            alt.Chart(df_segmento)
            .mark_bar()
            .encode(
                x=alt.X("avaliacao_4:N", sort=ORDEM_AVALIACAO, title="Avaliação"),
                y=alt.Y("count():Q", title="Carros"),
                tooltip=[
                    alt.Tooltip("avaliacao_4:N", title="Avaliação"),
                    alt.Tooltip("count():Q", title="Carros"),
                ],
            )
            .transform_filter(clique)
            .properties(title="Distribuição da avaliação no nível clicado", width=320, height=260)
        )

        evento = st.altair_chart(
            grafico_niveis | grafico_avaliacao,
            key=f"crossfilter_dashboard2_{atributo_kpi}",
            on_select="rerun",
            width="stretch",
            alt="Gráfico de barras com a contagem de carros por nível do atributo escolhido, "
            "ao lado da distribuição da avaliação filtrada pelo nível clicado.",
        )

        itens_clicados = evento.selection.get("clique", [])
        niveis_clicados = [item[atributo_kpi] for item in itens_clicados]
        if niveis_clicados:
            df_metricas = df_segmento[df_segmento[atributo_kpi].isin(niveis_clicados)]

    with metricas_container:
        total_metricas = len(df_metricas)

        m1, m2, m3, m4, m5 = st.columns(5, border=True)
        m1.metric(
            "Carros selecionados",
            f"{total_metricas}",
            help=f"De {total_geral} carros no total. Reflete os níveis escolhidos e o clique no gráfico abaixo.",
        )
        m2.metric("Aceitabilidade geral", f"{taxa_geral:.0f}%")

        if total_metricas:
            taxa_metricas = (df_metricas["avaliacao"] == "Aceitável").mean() * 100
            pct_vgood_metricas = (df_metricas["avaliacao_4"] == "vgood").mean() * 100
            m3.metric(
                "Aceitabilidade selecionada",
                f"{taxa_metricas:.0f}%",
                delta=f"{taxa_metricas - taxa_geral:+.0f} p.p.",
                delta_description="vs. aceitabilidade geral",
            )
            m4.metric(
                "Carros 'vgood' selecionados",
                f"{pct_vgood_metricas:.0f}%",
                delta=f"{pct_vgood_metricas - pct_vgood_geral:+.0f} p.p.",
                delta_description="vs. % 'vgood' geral",
            )
        else:
            m3.metric("Aceitabilidade selecionada", "—")
            m4.metric("Carros 'vgood' selecionados", "—")

        m5.metric(
            "Atributo mais associado à avaliação",
            atributo_top.removesuffix("_cod"),
            help=f"Maior |correlação de Spearman| com a avaliação: {valor_top:.2f}.",
        )
