# Justificativa das métricas — Dashboard 2

## Métrica 1: Carros no nível clicado
- **Variável:** nenhuma variável isolada — é a contagem de linhas do nível escolhido ao clicar numa barra do gráfico "Carros por nível" (atributo selecionado em "Agrupar por"). Antes do clique, mostra "—" em vez de repetir o total geral.
- **O que mede:** o tamanho da amostra (N) do nível clicado, por trás das métricas 3 e 4.
- **Por que foi escolhida:** uma taxa (%) sem o N correspondente é enganosa — "100% de aceitação" soa ótimo tanto para 2 carros quanto para 2.000. Essa métrica dá contexto de confiança às métricas 3 e 4. Mostrar "—" em vez de um número antes do clique evita sugerir uma comparação que ainda não existe.
- **Público-alvo:** qualquer pessoa lendo o dashboard, especialmente quem for comparar níveis diferentes entre si.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se um nível é grande o suficiente para embasar uma conclusão, ou se é pequeno demais para generalizar.
- **O que comunica ao público-alvo:** "estes números vêm de X carros" — o tamanho da base por trás do nível escolhido.

## Métrica 2: Aceitabilidade geral
- **Variável:** `avaliacao` (Aceitável / Não Aceitável).
- **O que mede:** a proporção de carros avaliados como "Aceitável" em todo o dataset (sem filtro), em percentual.
- **Por que foi escolhida:** é o KPI de referência (baseline) — toda comparação de segmento (Métrica 3) só faz sentido contra esse número fixo.
- **Público-alvo:** gestor ou comprador sem familiaridade com o dataset, que quer uma visão geral antes de entrar em detalhes.
- **Qual decisão pode ser apoiada por essa métrica?** Avaliar se o padrão de qualidade geral da frota/amostra está alto ou baixo, antes de investigar por quê.
- **O que comunica ao público-alvo:** "de modo geral, 3 em cada 10 carros avaliados são aceitáveis."

## Métrica 3: Aceitabilidade do nível (com delta)
- **Variável:** `avaliacao`, recalculada sobre o nível clicado no gráfico "Carros por nível" (atributo escolhido em "Agrupar por"). Mostra "—" antes de qualquer clique.
- **O que mede:** a mesma taxa da Métrica 2, só que condicionada a um nível específico de um atributo do carro (ex.: `buying = vhigh`), com a diferença em pontos percentuais (p.p.) em relação à aceitabilidade geral.
- **Por que foi escolhida:** é a métrica central do dashboard — uma taxa condicional é o que de fato liga um atributo de entrada (preço, segurança etc.) a um resultado (aceitabilidade), e o delta deixa o tamanho do efeito explícito sem exigir que o público faça a conta de cabeça. Sem um nível clicado, a taxa seria idêntica à geral (delta zero) e não diria nada de novo — por isso ela só aparece depois da interação.
- **Público-alvo:** quem decide especificações do carro (ex.: comprador definindo orçamento, ou equipe de produto priorizando um atributo).
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar qual atributo (e qual nível dele) mais aproxima — ou afasta — os carros do padrão aceitável, ex.: "carros com `buying = vhigh` têm 13 p.p. a menos de aceitabilidade que a média".
- **O que comunica ao público-alvo:** se o nível escolhido torna os carros melhores ou piores que a média, e o quanto.

## Métrica 4: Carros "vgood" no nível (com delta)
- **Variável:** `avaliacao_4` (categoria `vgood`, a nota máxima entre unacc/acc/good/vgood).
- **O que mede:** a proporção de carros com a nota mais alta dentro do mesmo nível clicado da Métrica 3, também com delta em p.p. contra o percentual geral de "vgood".
- **Por que foi escolhida:** "Aceitável" (Métrica 3) já mistura good+vgood num único rótulo binário; esta métrica isola o topo da escala, útil quando o objetivo não é só "passar no mínimo" mas identificar o segmento de excelência.
- **Público-alvo:** quem busca o melhor carro dentro de uma condição (ex.: "dentre os carros baratos, quantos são realmente muito bons?"), não apenas o aceitável.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se vale a pena relaxar uma restrição (ex.: aumentar o orçamento) para alcançar o segmento de melhor nota.
- **O que comunica ao público-alvo:** o quão raro (ou comum) é o desempenho máximo dentro do nível escolhido.

## Métrica 5: Correlação com a avaliação (atributo mais associado)
- **Variável:** todas as variáveis quantitativas (`buying_cod`, `maint_cod`, `doors_cod`, `persons_cod`, `lug_boot_cod`, `safety_cod`) comparadas via |correlação de Spearman| com `avaliacao_cod`. O valor exibido é o coeficiente em si (ex.: `0.47`); o nome do atributo (`safety`) fica no rótulo do cartão, não no valor — para a métrica permanecer quantitativa.
- **O que mede:** a força da associação (um número de -1 a 1, não uma categoria) entre o atributo mais relevante e o resultado da avaliação, reaproveitando o mesmo cálculo de correlação do Dashboard 1.
- **Por que foi escolhida:** diferente das métricas 1, 3 e 4 (que dependem do nível clicado pelo usuário), esta é uma métrica de "onde olhar primeiro" — aponta automaticamente qual atributo investigar, sem que o usuário precise testar um por um nos widgets. Optamos por expor o coeficiente de correlação (quantitativo) em vez do nome do atributo (qualitativo) como valor do cartão, para que a métrica em si seja um número comparável, e não apenas um rótulo.
- **Público-alvo:** quem está decidindo em qual atributo focar a análise ou o investimento (ex.: equipe de engenharia decidindo se vale mais a pena investir em segurança ou em espaço).
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar esforço/investimento no atributo que historicamente mais influencia se um carro é bem avaliado.
- **O que comunica ao público-alvo:** "se você só puder melhorar uma coisa no carro para subir a nota, comece por `safety` — a associação dele com a avaliação (0.47) é a mais forte entre os atributos."
