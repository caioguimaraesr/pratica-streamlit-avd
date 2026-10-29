# Declaração de Uso de IA

**Nome:** Caio A. Rocha <!-- confirme/ajuste se necessário -->
**Data:** 2026-10-29

## Ferramenta

Claude Code (modelo Claude Sonnet 5), via extensão nativa no VS Code.

## Prompt usado

Sessão de continuação da Aula 22, com os seguintes pedidos (em sequência):

1. "Siga o próximo passo do roteiro." — pedi para identificar e executar o próximo passo pendente do `ROTEIRO.md`.
2. Ao perguntar sobre a identidade visual (passo 3 da Aula 22: cor de destaque, fundo e fonte em `.streamlit/config.toml`), respondi "escolha" — deleguei a escolha da paleta e da fonte à IA.
3. "quais métricas voce sugere?" — pedi sugestões de métricas/KPIs para o Dashboard 2 a partir do dataset Car Evaluation.
4. "aplique de 3 a 5 méticas que voce sugeriu" — pedi para implementar as métricas sugeridas no `app.py`.
5. "me mande um prompt para que eu possa mandar para outra IA criar o rascunho." — pedi um prompt pronto para gerar, em outra ferramenta de IA (gerador de imagem), o rascunho visual do Dashboard 2.
6. "o rascunho2 foi criado. termine para mim o roteiro." — pedi para concluir os passos restantes da Aula 22 (rascunho, implementação dos gráficos Altair com crossfilter, justificativa das métricas e esta declaração).

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - A correção de um bug real encontrado ao testar os cenários de borda do Dashboard 1: quando os filtros resultavam em 0 carros, a correlação virava uma matriz de `null` e a distribuição ficava vazia sem aviso. Corrigido com `st.warning` nas duas seções quando `df_filtrado` está vazio.
  - A paleta de identidade visual sugerida pela IA (azul-aço `#2f6690`/`#5fa8d3` como cor de destaque, fonte Inter), por não competir visualmente com o laranja/vermelho já usados nos gráficos de avaliação.
  - As 5 métricas sugeridas para o Dashboard 2 (carros selecionados, aceitabilidade geral, aceitabilidade segmentada, % "vgood" segmentado, atributo mais associado à avaliação) e os widgets de segmentação (`selectbox` + `multiselect`).
  - A implementação dos gráficos Altair com seleção por clique (crossfilter) ligando o gráfico de contagem por nível à distribuição da avaliação e às métricas, usando o padrão do `ALTAIR-CROSSFILTER.md` (Exemplo 3, `on_select="rerun"`).
  - O prompt de rascunho gerado pela IA para outra ferramenta de geração de imagem, usado para criar `entregas/rascunho-dashboard2.png`.

- **Modificado:**
  - Os nomes dos arquivos de rascunho (`rascunho-caio.png`/`rascunho-caio2.png`) foram renomeados para `rascunho-dashboard1.png`/`rascunho-dashboard2.png`, para bater com o checklist de `entregas/README.md`.

- **Rejeitado:**
  - Nenhuma sugestão da IA foi rejeitada nesta sessão; todas as decisões de design (cores, métricas, layout do crossfilter) foram revisadas e aprovadas antes de seguir para o próximo passo.
