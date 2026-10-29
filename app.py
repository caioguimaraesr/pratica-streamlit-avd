
import altair as alt
import streamlit as st

from src.data_loader import load_data

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

# Cores da distribuição por avaliação do carro — os mesmos azuis do
# primaryColor do tema (claro/escuro), clara para o desfecho bom e escura
# para o ruim, com contraste suficiente nos dois temas
CORES_AVALIACAO = {
    "Aceitável": "#5fa8d3",
    "Não Aceitável": "#1f4e6b",
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
    from src.kpi_charts import (
        ATRIBUTOS, barras_aceitacao, distribuicao_avaliacoes, mapa_aceitacao,
    )

    st.subheader("Aceitação dos veículos")
    st.caption(
        "Compare custo, segurança e capacidade. Os filtros abaixo e os intervalos "
        "da barra lateral se aplicam a todos os indicadores e gráficos desta aba."
    )
    df_segmento = df_filtrado.copy()
    with st.expander("Filtrar características", expanded=True):
        for linha in (ATRIBUTOS_CATEGORICOS[:3], ATRIBUTOS_CATEGORICOS[3:]):
            for coluna, atributo in zip(st.columns(3), linha):
                titulo, rotulos = ATRIBUTOS[atributo]
                disponiveis = [nivel for nivel in rotulos if nivel in df[atributo].astype(str).unique()]
                selecionados = coluna.multiselect(
                    titulo, options=disponiveis, default=disponiveis,
                    format_func=rotulos.get, key=f"kpi_{atributo}",
                    help="Remover todas as opções deixa a seleção vazia.",
                )
                df_segmento = df_segmento[df_segmento[atributo].astype(str).isin(selecionados)]

    total = len(df_segmento)
    taxa_geral = df["avaliacao"].eq("Aceitável").mean() * 100
    taxa = df_segmento["avaliacao"].eq("Aceitável").mean() * 100 if total else None
    melhores = df_segmento["avaliacao_4"].isin(["good", "vgood"]).mean() * 100 if total else None
    m1, m2, m3, m4 = st.columns(4, border=True)
    m1.metric("Configurações selecionadas", f"{total:,}".replace(",", "."), help=f"Base completa: {len(df)} configurações.")
    m2.metric("Taxa de aceitação", f"{taxa:.1f}%" if total else "—", help="Aceitáveis divididos pelo total selecionado. Inclui acc, good e vgood.")
    m3.metric("Bom ou muito bom", f"{melhores:.1f}%" if total else "—", help="Avaliações good e vgood divididas pelo total selecionado.")
    m4.metric("Diferença para a base", f"{taxa - taxa_geral:+.1f} p.p." if total else "—", help="Taxa selecionada menos a taxa de aceitação da base completa, sem filtros.")
    st.caption(
        f"Referência fixa: {taxa_geral:.1f}% de aceitação na base completa. "
        "Cada taxa dos gráficos usa o total do próprio grupo. Passe o mouse para ver as contagens."
    )

    if not total:
        st.warning("Nenhuma configuração atende aos filtros. Selecione níveis ou amplie os intervalos laterais.")
    else:
        esquerda, direita = st.columns(2)
        with esquerda, st.container(border=True):
            st.subheader("Aceitação por segurança")
            st.altair_chart(barras_aceitacao(df_segmento, "safety"), width="stretch", alt="Taxa de aceitação por nível de segurança.")
        with direita, st.container(border=True):
            st.subheader("Compra e manutenção")
            st.altair_chart(mapa_aceitacao(df_segmento, "buying", "maint"), width="stretch", alt="Taxa de aceitação por combinação de custo de compra e manutenção.")
        esquerda, direita = st.columns(2)
        with esquerda, st.container(border=True):
            st.subheader("Capacidade e porta-malas")
            st.altair_chart(mapa_aceitacao(df_segmento, "persons", "lug_boot"), width="stretch", alt="Taxa de aceitação por capacidade e tamanho do porta-malas.")
        with direita, st.container(border=True):
            st.subheader("Distribuição das avaliações")
            st.altair_chart(distribuicao_avaliacoes(df_segmento), width="stretch", alt="Quantidade e percentual das quatro classes de avaliação na seleção.")
        with st.container(border=True):
            st.subheader("Aceitação por número de portas")
            st.altair_chart(barras_aceitacao(df_segmento, "doors"), width="stretch", alt="Taxa de aceitação por número de portas.")
        st.caption("Células ausentes nos mapas indicam combinações sem registros após os filtros; 0% indica um grupo existente sem configurações aceitáveis.")
