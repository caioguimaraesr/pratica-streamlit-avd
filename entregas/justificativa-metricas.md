# Justificativa das métricas — Dashboard 2

## Métrica 1: Carros selecionados
- **Variável:** nenhuma variável isolada — é a contagem de linhas do recorte atual (nível do atributo escolhido em "Agrupar por" + nível clicado no gráfico).
- **O que mede:** o tamanho da amostra (N) por trás das demais métricas.
- **Por que foi escolhida:** uma taxa (%) sem o N correspondente é enganosa — "100% de aceitação" soa ótimo tanto para 2 carros quanto para 2.000. Essa métrica dá contexto de confiança às outras quatro.
- **Público-alvo:** qualquer pessoa lendo o dashboard, especialmente quem for comparar segmentos diferentes entre si.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se um segmento é grande o suficiente para embasar uma conclusão, ou se é pequeno demais para generalizar.
- **O que comunica ao público-alvo:** "estes números vêm de X carros" — o tamanho da base por trás do recorte.

## Métrica 2: Aceitabilidade geral
- **Variável:** `avaliacao` (Aceitável / Não Aceitável).
- **O que mede:** a proporção de carros avaliados como "Aceitável" em todo o dataset (sem filtro), em percentual.
- **Por que foi escolhida:** é o KPI de referência (baseline) — toda comparação de segmento (Métrica 3) só faz sentido contra esse número fixo.
- **Público-alvo:** gestor ou comprador sem familiaridade com o dataset, que quer uma visão geral antes de entrar em detalhes.
- **Qual decisão pode ser apoiada por essa métrica?** Avaliar se o padrão de qualidade geral da frota/amostra está alto ou baixo, antes de investigar por quê.
- **O que comunica ao público-alvo:** "de modo geral, 3 em cada 10 carros avaliados são aceitáveis."

## Métrica 3: Aceitabilidade selecionada (com delta)
- **Variável:** `avaliacao`, recalculada sobre o recorte definido pelos widgets ("Agrupar por" + níveis) e, se houver, pelo clique no gráfico de barras.
- **O que mede:** a mesma taxa da Métrica 2, só que condicionada a um atributo específico do carro (ex.: `buying = vhigh`), com a diferença em pontos percentuais (p.p.) em relação à aceitabilidade geral.
- **Por que foi escolhida:** é a métrica central do dashboard — uma taxa condicional é o que de fato liga um atributo de entrada (preço, segurança etc.) a um resultado (aceitabilidade), e o delta deixa o tamanho do efeito explícito sem exigir que o público faça a conta de cabeça.
- **Público-alvo:** quem decide especificações do carro (ex.: comprador definindo orçamento, ou equipe de produto priorizando um atributo).
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar qual atributo (e qual nível dele) mais aproxima — ou afasta — os carros do padrão aceitável, ex.: "carros com `buying = vhigh` têm 13 p.p. a menos de aceitabilidade que a média".
- **O que comunica ao público-alvo:** se a condição escolhida torna os carros melhores ou piores que a média, e o quanto.

## Métrica 4: Carros "vgood" selecionados (com delta)
- **Variável:** `avaliacao_4` (categoria `vgood`, a nota máxima entre unacc/acc/good/vgood).
- **O que mede:** a proporção de carros com a nota mais alta dentro do mesmo recorte da Métrica 3, também com delta em p.p. contra o percentual geral de "vgood".
- **Por que foi escolhida:** "Aceitável" (Métrica 3) já mistura good+vgood num único rótulo binário; esta métrica isola o topo da escala, útil quando o objetivo não é só "passar no mínimo" mas identificar o segmento de excelência.
- **Público-alvo:** quem busca o melhor carro dentro de uma condição (ex.: "dentre os carros baratos, quantos são realmente muito bons?"), não apenas o aceitável.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se vale a pena relaxar uma restrição (ex.: aumentar o orçamento) para alcançar o segmento de melhor nota.
- **O que comunica ao público-alvo:** o quão raro (ou comum) é o desempenho máximo dentro da condição escolhida.

## Métrica 5: Atributo mais associado à avaliação
- **Variável:** todas as variáveis quantitativas (`buying_cod`, `maint_cod`, `doors_cod`, `persons_cod`, `lug_boot_cod`, `safety_cod`) comparadas via |correlação de Spearman| com `avaliacao_cod`; mostra o nome do atributo com maior associação (hoje, `safety`, ρ ≈ 0,47).
- **O que mede:** um ranking — qual atributo do carro mais "anda junto" com o resultado da avaliação, reaproveitando o mesmo cálculo de correlação do Dashboard 1.
- **Por que foi escolhida:** diferente das métricas 1 a 4 (que dependem do recorte escolhido pelo usuário), esta é uma métrica de "onde olhar primeiro" — aponta automaticamente qual atributo investigar, sem que o usuário precise testar um por um nos widgets.
- **Público-alvo:** quem está decidindo em qual atributo focar a análise ou o investimento (ex.: equipe de engenharia decidindo se vale mais a pena investir em segurança ou em espaço).
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar esforço/investimento no atributo que historicamente mais influencia se um carro é bem avaliado.
- **O que comunica ao público-alvo:** "se você só puder melhorar uma coisa no carro para subir a nota, comece por `safety`."
