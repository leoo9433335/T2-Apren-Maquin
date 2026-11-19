## guia para apresentação

Este guia converte cada exigência do Trabalho II em: o que precisa ser
demonstrado, qual decisão foi tomada, qual evidência consultar e o que pode
ser perguntado na apresentação. Ele descreve o estado atual do projeto; não
substitui a revisão dos dados nem o relatório.

## 1. O que a professora está avaliando

O enunciado pede três etapas obrigatórias:

1. Pré-processamento: entender e limpar os dados e justificar as
   transformações.
2. Análise: duas tarefas, cada uma com dois métodos diferentes e comparação.
   - A: agrupamento.
   - B: redução de dimensionalidade.
3. Análise crítica: achados, sensibilidade a pelo menos uma decisão de
   pré-processamento e limitações.

Não é suficiente apresentar a saída dos algoritmos. Para cada resultado, o
grupo precisa ligar **decisão → evidência → interpretação → limitação**.

## 2. Mapa de requisitos e decisões

### Etapa 1 — Pré-processamento

| Exigência | Decisão implementada | Evidência e explicação para apresentar | Situação |
|---|---|---|---|
| Identificar tipos de variáveis, ausentes e distribuição | Foi feita uma tabela de ausentes e tipos; foram inspecionadas atividades e categorias. | `resultados/tabelas/exploracao_dados.tsv`; dados originais têm 506 linhas, 1 ID repetido, ausentes em características morfológicas e nas Atividades 20, 21 e 23. Há 176 células com `&`. | Parcial: complementar a descrição de distribuições e os gráficos exploratórios no relatório. |
| Corrigir problemas de qualidade | O script de limpeza renumera o ID repetido, padroniza grafias conhecidas de GRAM, troca `Muco=2` pela moda, deixa a Atividade 23 do ID 1718 ausente e separa códigos unidos por `&`. | `Limpeza.py` e `Dados_REG_transformado.tsv`. A correção do ID evita colisão; separar códigos preserva informação; imputar Muco pela moda e alterar o ID 1718 são decisões que precisam ser reconhecidas como escolhas, não fatos biológicos. | Implementado; expliquem cada correção e a possibilidade de ela afetar resultados. |
| Evitar distâncias sem sentido para categorias nominais | Códigos morfológicos foram separados em colunas e codificados por one-hot. Valores ausentes viram a categoria `Sem`. | `transformer.py` gera `Dados_REG_kmeans_onehot.tsv`. Uma variável como Cor=1/2 não é tratada como medida em que 2 seja o dobro de 1. | Implementado como representação morfológica, mas não usado para ajustar os clusters principais. |
| Tornar as atividades comparáveis em escala | Atividades categóricas 03, 04 e 16 foram codificadas Negativo=0/Positivo=1; Atividade 01 foi mantida binária; ordinais 13 e 17–22 foram divididas por 3; variáveis contínuas foram normalizadas; 02, 14, 15 e 23 receberam `log1p` antes da normalização. | `transformer.py` e `Dados_REG_atividades_transformadas.tsv`. Todos os atributos usados na análise principal ficam entre 0 e 1. | Implementado. |
| Tratar dados ausentes | Moda para atividades categóricas/ordinais e mediana para as demais; algumas colunas indicadoras de ausência foram criadas. | O arquivo transformado contém os valores imputados e indicadores como `Atividade 20_ausente`. Os indicadores não entraram nos algoritmos. | Implementado; justifiquem por que os indicadores foram excluídos: a análise pretende agrupar pelo valor da atividade, não pela ocorrência do registro ausente. |
| Explicar relações entre variáveis | Foram calculadas correlações de Pearson entre atividades e tabelas de morfologia por GRAM. | `resultados/figuras/07_correlacao_atividades.png`, `08_morfologia_gram.png` e tabelas associadas. Correlações altas indicam associação linear, não causalidade nem redundância comprovada. | Evidência disponível; incluir comentário explícito no relatório. |

### Etapa 2A — Agrupamento

| Exigência | Decisão implementada | Evidência e explicação para apresentar | Situação |
|---|---|---|---|
| Usar dois algoritmos de naturezas diferentes | K-Means (centróides) e DBSCAN (densidade). | O primeiro sempre atribui cada isolado a um grupo; o segundo pode marcar ruído. Assim, suas diferenças são metodologicamente informativas. | Implementado. |
| Escolher o número de grupos do K-Means | Foram avaliados k=2 a 10, com semente 42 e 20 inicializações. Foi escolhido k=2 por maior silhueta; o cotovelo é evidência complementar. | `01_selecao_k.png` e `metricas_kmeans.tsv`. Resultado: tamanhos 280 e 226; silhueta 0,169; Davies–Bouldin 2,058. A silhueta baixa indica grupos pouco separados, mesmo sendo k=2 o melhor entre os testados. | Implementado; não afirmar que “existem naturalmente exatamente dois grupos”. |
| Definir parâmetros do DBSCAN | Distância euclidiana, `min_samples=5`, `eps=0,90`; `eps` é comparado em vários valores e com gráfico de k-distâncias. | `02_dbscan_parametros.png`, `k_distancias_dbscan.tsv` e `sensibilidade_dbscan.tsv`. DBSCAN considera o próprio ponto na contagem de `min_samples`. O valor de `eps` não é único: aumentar `eps` altera grupos e ruído. | Implementado; reconhecer que a escolha é exploratória e que o resultado é sensível ao parâmetro. |
| Caracterizar cada grupo | Foram calculadas médias das 23 atividades e frequências/proporções das categorias morfológicas. | `perfis_clusters.tsv` e `perfis_morfologicos_clusters.tsv`; visualização em `06_perfis_atividades.png`. Os nomes dos ensaios são anônimos, então relatar os números sem inventar significado biológico. | Implementado. |
| Identificar isolados incomuns | Ruído DBSCAN e distância ao centróide K-Means no percentil 95 ou acima são usados como sinalizadores. | `isolados_atipicos.tsv`. O limiar é exploratório; “atípico” não significa erro, nova espécie ou propriedade rara comprovada. | Implementado com ressalva. |
| Comparar partições | Usa-se ARI e tabela cruzada dos rótulos. | `contingencia_particoes.tsv`; ARI K-Means/DBSCAN = 0,053, indicando pouca concordância entre as partições. O DBSCAN formou 6 grupos e marcou 195/506 (38,5%) como ruído. | Implementado. |
| Avaliar os grupos com métricas | Duas métricas internas: silhueta e Davies–Bouldin. Métricas externas: ARI/NMI comparando com GRAM. | `metricas_clusters.tsv`. DBSCAN, avaliado apenas nos não ruído, teve silhueta 0,008 e Davies–Bouldin 1,618; não comparar diretamente com K-Means sem mencionar a exclusão do ruído. ARI externo com GRAM: 0,016 no K-Means e 0,013 no DBSCAN. | Implementado. |
| Avaliar estabilidade | Cinco amostras aleatórias com 80% dos isolados foram comparadas com a partição completa por ARI. | `estabilidade_clusters.tsv`: média ARI 0,946 para K-Means e 0,705 para DBSCAN. K-Means foi mais consistente nessa checagem; cinco repetições são evidência limitada, não prova de validade biológica. | Implementado. |
| Verificar o papel do GRAM | GRAM foi primeiro usado como referência externa; também se compararam agrupamentos com e sem GRAM codificado em one-hot. | `comparacao_com_sem_gram.tsv` e `05_contingencia_gram.png`. ARI entre partições sem/com GRAM: 0,031 para K-Means e 0,368 para DBSCAN; no DBSCAN, número de grupos passou de 6 para 10 com os mesmos parâmetros. | Implementado; explique que incluir GRAM altera a definição de distância e a partição, não “melhora” automaticamente o resultado. |

### Etapa 2B — Redução de dimensionalidade

| Exigência | Decisão implementada | Evidência e explicação para apresentar | Situação |
|---|---|---|---|
| Aplicar uma técnica linear e uma não linear | PCA (linear) e t-SNE (não linear), usando as mesmas 23 atividades transformadas. | `03_projecoes_pca_tsne.png`. PCA encontra combinações lineares de maior variância; t-SNE prioriza vizinhanças locais. | Implementado. |
| Projetar em duas dimensões e colorir pelos agrupamentos | As projeções 2D foram coloridas pelos rótulos K-Means e DBSCAN. | Quatro painéis em `03_projecoes_pca_tsne.png`. A figura é uma visualização; não é novo agrupamento nem evidência de causalidade. | Implementado. |
| Avaliar a informação preservada | PCA: variância explicada, erro de reconstrução e trustworthiness. Ambos: trustworthiness. | `pca_variancia_reconstrucao.tsv` e `metricas_reducao_dimensionalidade.tsv`. As duas primeiras componentes explicam 38,4% da variância; trustworthiness@10: PCA 0,861, t-SNE 0,961. | Implementado. |
| Avaliar sensibilidade da projeção | t-SNE foi executado com perplexity 10, 30 e 50 e sementes distintas; comparam-se vizinhos por sobreposição Jaccard. | `metricas_reducao_dimensionalidade.tsv`; sobreposição média das vizinhanças alternativas com a configuração base: 0,552. A figura varia com hiperparâmetros, mesmo com trustworthiness alto. | Implementado. |
| Interpretar os eixos do PCA | Foram calculados os pesos (loadings) das atividades nas duas primeiras componentes. | PC1 é mais influenciada pelas Atividades 20, 19, 21, 17 e 18; PC2 é dominada pela Atividade 16. Os sinais dependem da orientação arbitrária dos eixos; a magnitude indica contribuição relativa. | Implementado no relatório. |

### Etapa 3 — Análise crítica

| Exigência | Decisão/evidência | Situação |
|---|---|---|
| Resumir os achados das etapas | K-Means resume em dois grupos com separação fraca; DBSCAN identifica regiões densas e muito ruído; PCA retém 38,4% nas duas dimensões; t-SNE preserva melhor vizinhanças locais na configuração avaliada. | Evidências disponíveis no relatório. |
| Refazer uma análise alterando pré-processamento | Foi removido `log1p` das Atividades 02, 14, 15 e 23 e repetido K-Means com o mesmo k e semente. | `sensibilidade_preprocessamento.tsv`: ARI entre partições=0,885; silhueta passou de 0,169 para 0,180. Há mudança, mas a partição continua relativamente parecida. |
| Descrever limitações | Atividades anônimas, amostra de 506 isolados, códigos categóricos, imputação, dependência de parâmetros, muitas dimensões e projeções 2D que perdem informação. | Incluir no relatório e mencionar na conclusão. Não inferir espécies, mecanismo, potencial farmacológico ou anormalidade biológica apenas pelos clusters. |
| Entregar README, código, relatório e referências | README e scripts existem; o relatório está em Markdown/HTML com referências. | Antes de enviar: preencher nomes/matrículas, gerar PDF e verificar se os arquivos de dados e dependências estão incluídos. |

## 3. Decisões técnicas que você deve saber defender

### Por que separar ID dos atributos?

O identificador é um rótulo administrativo, não uma medida de semelhança. Incluí-lo nas distâncias faria números de ID próximos parecerem biologicamente parecidos sem justificativa.

### Por que fazer uma análise principal com atividades?

O objetivo foi descobrir perfis funcionais usando as 23 atividades transformadas. A morfologia foi mantida para descrever os grupos, sem misturar categorias nominais e medidas funcionais numa única distância. O arquivo `Dados_REG_kmeans_onehot.tsv` contém morfologia codificada, mas **não foi usado para treinar os clusters principais**. A análise comparativa de GRAM é uma exceção controlada, feita para medir seu efeito.

Se perguntarem se os grupos representam semelhança morfológica, a resposta correta é: **a morfologia foi descrita após a clusterização, mas não definiu os rótulos principais**. Não diga que o clustering principal combinou morfologia e atividades.

### Por que normalizar e aplicar log?

Distâncias euclidianas são afetadas pela escala; sem transformação, atividades com amplitude maior poderiam dominar. `log1p` reduz a influência de caudas longas antes da escala min-max. A análise sem log testa se essa decisão altera os resultados. Ela alterou parte da partição (ARI=0,885), o que deve ser relatado, não escondido.

### Por que K-Means e DBSCAN dão respostas tão diferentes?

K-Means escolhe centróides e atribui todos os pontos ao centróide mais próximo, favorecendo grupos compactos. DBSCAN depende da densidade local, aceita formatos diversos e pode rejeitar pontos como ruído. Além das premissas diferentes, DBSCAN é sensível a `eps`; por isso não é surpresa obter seis grupos pequenos e muitos pontos não agrupados.

### Por que usar silhueta e Davies–Bouldin?

São métricas internas, sem rótulo verdadeiro: silhueta maior geralmente indica que pontos estão mais próximos do próprio grupo do que dos vizinhos; Davies–Bouldin menor favorece grupos mais compactos e separados. Ambas favorecem certos formatos de cluster e não devem ser a única interpretação, especialmente para DBSCAN.

### O que significa usar GRAM como referência externa?

GRAM não foi o alvo que o modelo tentou prever na análise principal. Compara-se depois a partição com essa característica conhecida, usando ARI/NMI. Concordância baixa significa apenas que os grupos não reproduzem bem as categorias GRAM; não prova que os clusters estejam errados, pois podem refletir atividades.

### O que significam os gráficos PCA e t-SNE?

PCA é linear e seus eixos podem ser interpretados pelos pesos, mas as duas primeiras componentes retêm apenas 38,4% da variância. t-SNE obteve trustworthiness maior nessa configuração, mas prioriza vizinhos locais: distância entre “nuvens”, tamanho de um grupo e separação visual global não são medidas biológicas confiáveis. As duas projeções devem ser lidas como complementares.

## 4. Perguntas prováveis da professora — com respostas curtas

### Sobre os dados e pré-processamento

1. **Quantos dados e atributos foram analisados?**  
   506 isolados e 23 atividades na análise principal; o ID não foi usado como atributo.

2. **Por que existe um ID duplicado e o que vocês fizeram?**  
   O arquivo original tinha um ID repetido. A limpeza atribuiu um novo identificador ao repetido para preservar as duas linhas e permitir rastreamento.

3. **Como trataram os códigos com `&`?**  
   Foram separados em colunas derivadas para não descartar os componentes. Na morfologia, categorias foram one-hot; isso mantém informação categórica sem atribuir ordem numérica fictícia.

4. **Por que substituiram `Muco=2` pela moda?**  
   Foi considerado um valor inválido segundo a codificação adotada; substituímo-lo pela moda para manter o registro. É uma decisão de limpeza, pode alterar esse perfil e deve ser reconhecida como limitação.

5. **Por que a Atividade 23 do ID 1718 foi deixada vazia?**  
   Foi tratada como registro suspeito para revisão, em vez de assumir um valor. Depois a lacuna foi imputada pela regra documentada. Não afirmamos conhecer o valor correto.

6. **Como foram imputados os ausentes?**  
   Moda para categorias/ordinais e mediana para as demais atividades; o indicador de ausência não foi incluído na matriz de agrupamento.

7. **Por que transformar para 0–1?**  
   Para reduzir diferenças de escala na distância euclidiana. Isso não significa que todas as respostas sejam biologicamente equivalentes.

8. **Os códigos de Cor/Forma são quantidades?**  
   Não. São categorias nominais. Por isso se usa codificação categórica, não interpretação de que código 4 seja “maior” que código 1.

### Sobre agrupamento

9. **Por que escolheram K-Means e DBSCAN?**  
   São métodos de naturezas diferentes: centróides versus densidade, com comportamento distinto sobre o número de grupos e pontos atípicos.

10. **Como escolheram k?**  
    Testamos k=2 a 10, observando inércia/cotovelo e silhueta. k=2 teve a maior silhueta no intervalo testado, mas o valor 0,169 é baixo; portanto é a melhor divisão testada, não uma verdade natural.

11. **Como escolheram `eps=0,90`?**  
    Inspecionamos o gráfico de distâncias ao quinto vizinho (incluindo o próprio ponto, como faz a contagem do DBSCAN) e avaliamos a sensibilidade. Diferentes `eps` mudam bastante o número de grupos/ruído; a escolha é aproximada.

12. **Quantos grupos encontrou cada método?**  
    K-Means: 2 grupos (280 e 226 isolados). DBSCAN: 6 grupos, mais 195 isolados como ruído.

13. **Qual algoritmo foi melhor?**  
    Não há um vencedor universal. K-Means tem uma divisão mais estável e completa neste experimento, mas separação fraca. DBSCAN identifica regiões densas, mas deixa 38,5% como ruído e sua qualidade depende dos parâmetros.

14. **O que significa a silhueta DBSCAN de 0,008?**  
    Nos isolados não marcados como ruído, há pouca separação média entre grupos. O cálculo excluiu o ruído; portanto não é uma comparação perfeitamente equivalente à silhueta K-Means.

15. **Por que ARI K-Means versus DBSCAN é baixo?**  
    ARI=0,053 indica pouca concordância nas partições. K-Means força todos a um grupo; DBSCAN só agrupa pontos com densidade local suficiente e deixa os demais como ruído.

16. **Os isolados de ruído são anormais?**  
    Não podemos afirmar isso. Eles não têm densidade suficiente sob os parâmetros adotados e são candidatos a revisão.

17. **Como avaliaram estabilidade?**  
    Ajustamos os métodos em cinco subamostras de 80% e comparamos com a partição completa via ARI. K-Means teve ARI médio 0,946; DBSCAN, 0,705. É uma verificação limitada, não prova de validade biológica.

18. **Por que incluíram e removeram GRAM?**  
    Sem GRAM, avaliamos agrupamento funcional sem usar o tipo celular como atributo. Depois incluímos GRAM one-hot para ver o efeito: K-Means teve ARI 0,031 entre partições; DBSCAN 0,368 e passou de 6 para 10 grupos. A mudança mostra influência da variável, não melhoria garantida.

19. **Vocês usaram a morfologia no treinamento dos grupos?**  
    Não na análise principal. O arquivo one-hot de morfologia foi gerado, mas os clusters principais foram calculados com as 23 atividades. A morfologia serviu para descrever perfis depois. Se quiséssemos clusters combinados, seria outra análise e exigiria justificar pesos relativos.

### Sobre redução de dimensionalidade

20. **Por que PCA e t-SNE?**  
    PCA é linear, com eixos interpretáveis e variância explicada; t-SNE é não linear e foca nas vizinhanças locais. O contraste atende à exigência de comparar uma técnica linear com uma não linear.

21. **Quanto da informação o PCA preservou em 2D?**  
    As duas primeiras componentes explicaram 38,4% da variância. A projeção é útil para visualizar, mas perde parte substancial da informação.

22. **Por que confiar mais no t-SNE se trustworthiness é maior?**  
    Não significa confiar mais em toda a geometria. O índice indica preservação das vizinhanças locais; não valida distâncias globais ou separação biológica.

23. **Os grupos separados no t-SNE provam que existem grupos reais?**  
    Não. t-SNE pode mudar com perplexity/semente e foi escolhido para preservar relações locais. As métricas de estabilidade mostram que a vizinhança também varia entre configurações.

24. **O que representam os eixos do t-SNE?**  
    Não têm unidade nem interpretação direta; rotação, escala e posição global não devem receber significado.

### Sobre crítica e limites

25. **Qual decisão de pré-processamento alterou os resultados?**  
    Remover `log1p` das Atividades 02, 14, 15 e 23 resultou em ARI=0,885 com a partição original. Houve mudança mensurável, embora as partições ainda fossem relativamente semelhantes.

26. **Podem dizer que um grupo tem potencial farmacológico?**  
    Não. Os nomes dos ensaios estão anonimizados e clustering não substitui caracterização química nem validação laboratorial.

27. **Podem dizer que um isolado de ruído é uma nova espécie?**  
    Não. Ruído é uma classificação matemática dependente das variáveis e parâmetros usados.

28. **Quais são as maiores limitações?**  
    Ensaios anônimos, tamanho/representatividade da amostra, imputações e códigos categóricos, sensibilidade dos algoritmos, separação fraca, alta dimensionalidade e perda de informação nas projeções 2D.

## 5. Roteiro de apresentação (5–7 minutos)

1. **Objetivo (30 s):** investigar semelhanças nos 506 isolados, sem rótulos-alvo.
2. **Dados e limpeza (1 min):** tipos, ausentes, ID repetido, `&`, imputação e escalas.
3. **Agrupamento (2 min):** explicar K-Means/DBSCAN e parâmetros; mostrar `01_selecao_k.png`, `02_dbscan_parametros.png`, `06_perfis_atividades.png`.
4. **Comparação e validação (1 min):** silhueta, Davies–Bouldin, ARI entre partições, GRAM e estabilidade.
5. **Redução (1 min):** mostrar PCA versus t-SNE, variância explicada e trustworthiness; alertar sobre interpretação de gráficos.
6. **Sensibilidade e conclusão (1 min):** resultado sem log, limitações, e recomendação de validação laboratorial posterior.

## 6. Checklist antes da entrega

- [ ] Preencher nomes e matrículas dos 2–5 integrantes no README/relatório.
- [ ] Confirmar que os arquivos de entrada, código e resultados estão incluídos.
- [ ] Ler o relatório como HTML e verificar que gráficos aparecem.
- [ ] Exportar o relatório para PDF e conferir páginas/captions.
- [ ] Comentar explicitamente cada figura usada no texto.
- [ ] Declarar a morfologia como descritiva nos clusters principais, não como atributo do treinamento.
- [ ] Distinguir resultados estatísticos de conclusões biológicas.
- [ ] Conferir que `README.md` descreve o fluxo executável atual.

## 7. Observação sobre a organização dos arquivos

No estado atual, tabelas e figuras existentes estão em `resultados/tabelas/` e
`resultados/figuras/`, e relatórios em `relatorios/`. Porém, o script
`analise_completa.py` atualmente grava alguns resultados diretamente na raiz.
Antes de executar novamente, confira as instruções do README e não misture
saídas novas com as pastas existentes sem reorganizá-las. O arquivo
`algorit.py` é uma análise anterior, apenas de agrupamento; a análise PCA/t-SNE
está em `analise_completa.py`.
