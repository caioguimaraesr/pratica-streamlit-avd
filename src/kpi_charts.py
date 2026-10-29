"""Agregações e gráficos de aceitabilidade com a paleta azul do aplicativo."""

import altair as alt

ATRIBUTOS = {
    "buying": ("Custo de compra", {"low": "Baixo", "med": "Médio", "high": "Alto", "vhigh": "Muito alto"}),
    "maint": ("Custo de manutenção", {"low": "Baixo", "med": "Médio", "high": "Alto", "vhigh": "Muito alto"}),
    "doors": ("Portas", {"2": "2", "3": "3", "4": "4", "5more": "5 ou mais"}),
    "persons": ("Capacidade", {"2": "2 pessoas", "4": "4 pessoas", "more": "Mais de 4"}),
    "lug_boot": ("Porta-malas", {"small": "Pequeno", "med": "Médio", "big": "Grande"}),
    "safety": ("Segurança", {"low": "Baixa", "med": "Média", "high": "Alta"}),
}
NOTAS = {"unacc": "Não aceitável", "acc": "Aceitável", "good": "Bom", "vgood": "Muito bom"}
AZUIS = ["#1f4e6b", "#3d7ca3", "#79bde0", "#bfe3f5"]


def taxas_por_grupo(dados, campos):
    """Cada taxa usa somente os registros do próprio grupo como denominador."""
    resumo = (
        dados.assign(aceito=dados["avaliacao"].eq("Aceitável"))
        .groupby(campos, observed=True)["aceito"]
        .agg(total="size", aceitos="sum", taxa="mean")
        .reset_index()
    )
    for campo in campos:
        resumo[campo] = resumo[campo].astype(str).map(ATRIBUTOS[campo][1])
    return resumo


def barras_aceitacao(dados, campo):
    titulo, niveis = ATRIBUTOS[campo]
    base = alt.Chart(taxas_por_grupo(dados, [campo])).encode(
        x=alt.X(f"{campo}:N", sort=list(niveis.values()), title=titulo, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("taxa:Q", title="Taxa de aceitação", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".0%")),
        tooltip=[alt.Tooltip(f"{campo}:N", title=titulo),
                 alt.Tooltip("taxa:Q", title="Aceitação", format=".1%"),
                 alt.Tooltip("aceitos:Q", title="Aceitáveis"),
                 alt.Tooltip("total:Q", title="Configurações")],
    )
    return (base.mark_bar(color="#5fa8d3") + base.mark_text(dy=-8).encode(
        text=alt.Text("taxa:Q", format=".1%")
    )).properties(height=280)


def mapa_aceitacao(dados, campo_x, campo_y):
    base = alt.Chart(taxas_por_grupo(dados, [campo_x, campo_y])).encode(
        x=alt.X(f"{campo_x}:N", title=ATRIBUTOS[campo_x][0], sort=list(ATRIBUTOS[campo_x][1].values()), axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f"{campo_y}:N", title=ATRIBUTOS[campo_y][0], sort=list(ATRIBUTOS[campo_y][1].values())),
        tooltip=[alt.Tooltip(f"{campo_x}:N", title=ATRIBUTOS[campo_x][0]),
                 alt.Tooltip(f"{campo_y}:N", title=ATRIBUTOS[campo_y][0]),
                 alt.Tooltip("taxa:Q", title="Aceitação", format=".1%"),
                 alt.Tooltip("aceitos:Q", title="Aceitáveis"),
                 alt.Tooltip("total:Q", title="Configurações")],
    )
    mapa = base.mark_rect().encode(color=alt.Color(
        "taxa:Q", title="Aceitação", scale=alt.Scale(domain=[0, 1], range=[AZUIS[0], AZUIS[-1]]),
        legend=alt.Legend(format=".0%"),
    ))
    texto = base.mark_text(fontSize=14).encode(
        text=alt.Text("taxa:Q", format=".1%"),
        color=alt.condition("datum.taxa < 0.5", alt.value("white"), alt.value("#1f2a33")),
    )
    return (mapa + texto).properties(height=280)


def distribuicao_avaliacoes(dados):
    resumo = dados["avaliacao_4"].value_counts().reindex(NOTAS, fill_value=0).rename_axis("nota").reset_index(name="total")
    resumo["percentual"] = resumo["total"] / len(dados)
    resumo["nota"] = resumo["nota"].map(NOTAS)
    return alt.Chart(resumo).mark_bar().encode(
        x=alt.X("percentual:Q", title="Participação na seleção", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".0%")),
        y=alt.Y("nota:N", title=None, sort=list(NOTAS.values())),
        color=alt.Color("nota:N", scale=alt.Scale(domain=list(NOTAS.values()), range=AZUIS), legend=None),
        tooltip=[alt.Tooltip("nota:N", title="Avaliação"), alt.Tooltip("total:Q", title="Configurações"),
                 alt.Tooltip("percentual:Q", title="Participação", format=".1%")],
    ).properties(height=280)
