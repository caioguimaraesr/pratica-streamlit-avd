
import altair as alt
import streamlit as st

from src.data_loader import load_data
from src.kpi_charts import ATRIBUTOS, NOTAS

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

# Rótulos de apresentação; os cálculos continuam usando os códigos ordinais.
NOMES = {f"{campo}_cod": titulo for campo, (titulo, _) in ATRIBUTOS.items()}
NOMES["avaliacao_cod"] = "Avaliação do veículo"
NIVEIS = {}
for campo, (_, rotulos) in ATRIBUTOS.items():
    pares = df[[campo, f"{campo}_cod"]].drop_duplicates().sort_values(f"{campo}_cod")
    NIVEIS[f"{campo}_cod"] = {
        int(codigo): rotulos[str(valor)] for valor, codigo in pares.itertuples(index=False, name=None)
    }
NIVEIS["avaliacao_cod"] = dict(enumerate(NOTAS.values()))

# Sidebar: filtros
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis para analisar",
        options=VARS_QUANTITATIVAS,
        default=VARS_QUANTITATIVAS,
        format_func=lambda nome: NOMES.get(nome, nome),
        help="Selecione as variáveis quantitativas que deseja analisar no dashboard.",
    )

    # Um slider de intervalo para cada variável quantitativa selecionada.
    # Os limites vêm do dataset inteiro, então a faixa não encolhe conforme
    # os outros filtros vão cortando linhas.
    intervalos = {}
    for variavel in variaveis:
        minimo, maximo = int(df[variavel].min()), int(df[variavel].max())
        intervalos[variavel] = st.slider(
            f"Intervalo de {NOMES.get(variavel, variavel)}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            key=f"intervalo_{variavel}",
            help=" · ".join(f"{codigo} = {nome}" for codigo, nome in NIVEIS.get(variavel, {}).items()),
        )

# Mantém só os carros dentro de todas as faixas escolhidas
df_filtrado = df
for variavel, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[variavel].between(inicio, fim)]

tab_dashboard1, tab_dashboard2 = st.tabs(
    ["Dashboard 1 — Correlação e distribuição", "Dashboard 2 — KPIs"]
)

with tab_dashboard1:
    st.caption(f"Analisando {len(df_filtrado):,} de {len(df):,} configurações de veículos, conforme os filtros laterais.".replace(",", "."))

    st.subheader("Correlação")
    st.markdown("**Quais características variam juntas?** Cada célula compara duas variáveis usando a correlação de Spearman.")
    st.caption(
        "De −1 a +1: valores positivos indicam que os níveis tendem a subir juntos; "
        "negativos indicam sentidos opostos. Próximo de zero significa pouca associação "
        "monotônica, mas não exclui outras relações. Correlação não demonstra causa."
    )
    with st.expander("Como ler os níveis e as cores"):
        st.markdown(
            "**Azul (+):** níveis maiores de uma variável acompanham níveis maiores da outra. "
            "**Vermelho (−):** níveis maiores de uma acompanham níveis menores da outra. "
            "Quanto mais intensa a cor, maior a associação em módulo."
        )
        st.markdown(
            "Nos custos, subir de nível significa ficar **mais caro**; na segurança, "
            "significa passar de **baixa para alta**; na avaliação, de **não aceitável para muito bom**. "
            "Os números são códigos ordenados, sem unidade monetária."
        )
        for variavel in variaveis:
            st.caption(f"{NOMES.get(variavel, variavel)}: " + " → ".join(NIVEIS.get(variavel, {}).values()))

    if df_filtrado.empty:
        st.warning("Nenhuma configuração atende aos filtros. Amplie os intervalos para ver a correlação.")
    elif len(variaveis) < 2:
        st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
    else:
        corr = df_filtrado[variaveis].corr(method="spearman")
        corr_longo = corr.reset_index(names="linha").melt(id_vars="linha", var_name="coluna", value_name="rho")
        corr_longo["rho"] = corr_longo["rho"].round(10) + 0.0
        posicao = {variavel: i for i, variavel in enumerate(variaveis)}
        corr_longo = corr_longo[corr_longo["linha"].map(posicao) < corr_longo["coluna"].map(posicao)].copy()
        corr_longo["rotulo"] = corr_longo["rho"].map(lambda valor: "N/D" if valor != valor else f"{valor:+.2f}" if valor else "0.00")
        corr_longo["linha"] = corr_longo["linha"].map(NOMES)
        corr_longo["coluna"] = corr_longo["coluna"].map(NOMES)
        ordem = [NOMES.get(v, v) for v in variaveis]
        base = alt.Chart(corr_longo).encode(
            x=alt.X("coluna:N", sort=ordem, title=None, axis=alt.Axis(labelAngle=-20, labelFontSize=13, labelLimit=200)),
            y=alt.Y("linha:N", sort=ordem, title=None, axis=alt.Axis(labelFontSize=13, labelLimit=200)),
            tooltip=[alt.Tooltip("linha:N", title="Característica"), alt.Tooltip("coluna:N", title="Comparada com"), alt.Tooltip("rotulo:N", title="Spearman")],
        )
        mapa = base.mark_rect(stroke="#d7dee5", strokeWidth=1).encode(
            color=alt.condition(
                "isValid(datum.rho)",
                alt.Color("rho:Q", scale=alt.Scale(scheme="redblue", domain=[-1, 1]), title="Correlação (−1 a +1)", legend=alt.Legend(orient="bottom", values=[-1, -0.5, 0, 0.5, 1])),
                alt.value("#eef2f6"),
            )
        )
        rotulos = base.mark_text(fontSize=16, fontWeight="bold").encode(
            text="rotulo:N",
            color=alt.condition("isValid(datum.rho) && abs(datum.rho) > 0.5", alt.value("white"), alt.value("#1f2a33")),
        )
        st.altair_chart((mapa + rotulos).properties(height=max(220, 65 * (len(variaveis) - 1))), width="stretch", alt="Matriz triangular de correlação, com nomes das características e coeficientes em cada célula.")
        st.caption("Mostramos cada par uma única vez: a outra metade e a diagonal foram omitidas. N/D = não calculável, por exemplo quando uma variável fica constante após os filtros.")
        validas = corr_longo.dropna(subset=["rho"])
        if not validas.empty:
            destaque = validas.loc[validas["rho"].abs().idxmax()]
            if abs(destaque["rho"]) >= 0.01:
                sentido = "no mesmo sentido" if destaque["rho"] > 0 else "em sentidos opostos"
                st.info(f"Neste recorte, a maior associação em módulo é entre {destaque['linha']} e {destaque['coluna']} (ρ = {destaque['rho']:+.2f}): os níveis tendem a variar {sentido}.")
            else:
                st.info("Neste recorte, todas as correlações calculáveis estão próximas de zero.")
        st.caption("Na base completa, as características foram combinadas de forma sistemática. Por isso, correlações próximas de zero entre atributos são esperadas; observe também as relações com a avaliação.")

    st.subheader("Distribuição")
    st.markdown("**Quantas configurações existem em cada nível e como são avaliadas?** Compare as duas barras de cada categoria.")
    st.caption("Azul claro = aceitável (inclui bom e muito bom). Azul escuro = não aceitável. A altura e o número sobre a barra mostram a quantidade; o tooltip informa a participação dentro do nível.")

    if df_filtrado.empty:
        st.warning("Nenhuma configuração atende aos filtros. Amplie os intervalos para ver a distribuição.")
    elif not variaveis:
        st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
    else:
        # Grade de duas colunas, com barras agrupadas para evitar ocultar valores.
        for inicio in range(0, len(variaveis), 2):
            for coluna, variavel in zip(st.columns(2), variaveis[inicio:inicio + 2]):
                with coluna, st.container(border=True):
                    st.markdown(f"**{NOMES.get(variavel, variavel)}**")
                    resumo = df_filtrado.groupby([variavel, "avaliacao"]).size().unstack(fill_value=0).reindex(columns=list(CORES_AVALIACAO), fill_value=0).stack().reset_index(name="quantidade")
                    resumo["total_nivel"] = resumo.groupby(variavel)["quantidade"].transform("sum")
                    resumo["percentual"] = resumo["quantidade"] / resumo["total_nivel"]
                    resumo["nivel"] = resumo[variavel].map(NIVEIS[variavel])
                    base = alt.Chart(resumo).encode(
                        x=alt.X("nivel:N", title=None, sort=list(NIVEIS[variavel].values()), axis=alt.Axis(labelAngle=0, labelFontSize=12, labelLimit=140)),
                        xOffset=alt.XOffset("avaliacao:N", sort=list(CORES_AVALIACAO)),
                        y=alt.Y("quantidade:Q", title="Configurações", scale=alt.Scale(domain=[0, int(resumo["quantidade"].max() * 1.18) + 1]), axis=alt.Axis(tickMinStep=1)),
                        tooltip=[alt.Tooltip("nivel:N", title="Nível"), alt.Tooltip("avaliacao:N", title="Avaliação"), alt.Tooltip("quantidade:Q", title="Configurações"), alt.Tooltip("percentual:Q", title="Dentro deste nível", format=".1%"), alt.Tooltip("total_nivel:Q", title="Total do nível")],
                    )
                    barras = base.mark_bar().encode(color=alt.Color("avaliacao:N", title=None, scale=alt.Scale(domain=list(CORES_AVALIACAO), range=list(CORES_AVALIACAO.values())), legend=alt.Legend(orient="bottom")))
                    numeros = base.mark_text(dy=-8, fontSize=12).encode(text=alt.Text("quantidade:Q", format=".0f"))
                    st.altair_chart((barras + numeros).properties(height=260), width="stretch", alt=f"Distribuição de {NOMES[variavel]}, com contagens de configurações aceitáveis e não aceitáveis por nível.")
                    if variavel == "avaliacao_cod":
                        st.caption("Aqui, as quatro notas foram agrupadas nas duas classes: aceitável reúne aceitável, bom e muito bom. Este gráfico mostra a composição do resultado.")
        st.caption("Os gráficos têm escalas verticais próprias: compare os números ao comparar painéis. Na base completa, os atributos têm totais iguais por nível; os filtros podem alterar esse equilíbrio.")
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
