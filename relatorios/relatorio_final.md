# Relatorio final - Trabalho II: Aprendizado Nao Supervisionado

> Preencher nomes e matriculas dos integrantes antes da entrega.

## 1. Objetivo e dados

Foram analisados 506 isolados e 23 atividades funcionais. O ID foi usado apenas para rastreabilidade. A analise principal de grupos foi feita nas atividades transformadas; morfologia foi usada para descrever os grupos e GRAM foi reservado como referencia externa. O arquivo original tem 506 linhas e 1 IDs duplicados segundo a coluna de identificacao. Valores ausentes antes do tratamento: Borda: 1, Textura: 1, Forma: 2, Brilho: 2, Muco: 2, Relevo: 3, Atividade 20: 27, Atividade 21: 17, Atividade 23: 3. Foram detectadas 176 celulas com multiplos codigos. As tabelas `../resultados/tabelas/exploracao_dados.tsv` e `../resultados/tabelas/correlacoes_atividades.tsv` documentam qualidade, cardinalidade e relacoes entre atividades.

## 2. Pre-processamento e decisoes

- Na limpeza, o ID duplicado foi substituido por um novo ID; grafias conhecidas de GRAM foram padronizadas; valores 2 em Muco foram substituidos pela moda; Atividade 23 do ID 1718 foi deixada ausente por ser um registro a revisar; e codigos unidos por '&' foram separados em colunas para preservar os componentes.
- ID nao entrou como atributo, para evitar que um codigo arbitrario influenciasse distancias.
- As 23 atividades foram representadas em escalas de 0 a 1. Variaveis ordinais 0-3 foram divididas por 3; binarias/categoricas foram codificadas 0/1; atividades continuas foram normalizadas. As quatro atividades de cauda longa (02, 14, 15, 23) receberam log1p antes da normalizacao. Ausentes foram imputados conforme o tipo e a indicacao de ausencia nao entrou no agrupamento.
- A morfologia foi resumida pelas categorias mais frequentes por grupo, sem interpretar codigos nominais como quantidades.
- Exploracao: ver `../resultados/figuras/07_correlacao_atividades.png` para correlacoes entre ensaios e `../resultados/figuras/08_morfologia_gram.png`/`../resultados/tabelas/morfologia_gram.tsv` para a distribuicao das categorias morfologicas dentro de cada classe GRAM. As cinco correlacoes de maior magnitude foram: Atividade 09 x Atividade 10: r=+0.61; Atividade 14 x Atividade 15: r=+0.58; Atividade 11 x Atividade 12: r=+0.50; Atividade 18 x Atividade 22: r=+0.48; Atividade 10 x Atividade 11: r=+0.47.
- As distancias dos metodos usam os valores transformados. Assim, escalas e imputacoes fazem parte da definicao de semelhanca.

## 3. Tarefa A - Agrupamento

### Metodos e parametros

- **K-Means:** minimiza a soma das distancias euclidianas quadradas aos centroides. Requer k; tende a grupos compactos, aproximadamente esfericos e de tamanhos semelhantes, e nao separa ruido. Foram testados k=2..10, semente 42, n_init=20; o k final foi escolhido pela maior silhueta. O grafico de inercia pelo metodo do cotovelo foi apresentado como criterio complementar, sem presumir um cotovelo unico.
- **DBSCAN:** agrupa regioes densas e marca pontos sem vizinhos suficientes como ruido. Usa distancia euclidiana e min_samples=5; este limiar local conservador inclui o proprio ponto na contagem e foi mantido fixo para estudar eps. eps=0.90 foi escolhido aproximadamente pelo cotovelo no grafico de k-distancias (k=min_samples); a tabela de sensibilidade mostra que essa escolha nao e unica e que min_samples tambem limita a conclusao.

### Resultados e avaliacao

- K-Means selecionou k=2 (silhueta=0.169; Davies-Bouldin=2.058). Silhueta maior e melhor; Davies-Bouldin menor e melhor. A silhueta baixa aponta separacao fraca, nao evidencia grupos naturais bem delimitados.
- K-Means 0 (n=280): Atividade 20=0.90, Atividade 21=0.87, Atividade 16=0.81, Atividade 19=0.70, Atividade 17=0.64.
- K-Means 1 (n=226): Atividade 08=0.59, Atividade 16=0.54, Atividade 09=0.50, Atividade 13=0.50, Atividade 10=0.45.

Caracteristicas morfologicas mais frequentes nos grupos K-Means (categorias sao codigos nominais):
- K-Means 0: Cor=1 (88%); Cores=3 (39%); Borda=0.0 (75%); Textura=1 (62%); Forma=1 (70%); Brilho=2 (70%); Muco=0.0 (71%); Relevo=0.0 (62%).
- K-Means 1: Cor=1 (84%); Cores=3 (40%); Borda=0.0 (81%); Textura=1 (68%); Forma=1 (70%); Brilho=2 (78%); Muco=0.0 (76%); Relevo=0.0 (60%).

- DBSCAN produziu 6 grupos e 195 isolados de ruido (38.5%). Contagens por rotulo (inclui -1 = ruido): -1: 195, 0: 203, 1: 10, 2: 76, 3: 10, 4: 7, 5: 5. Nos pontos nao ruido, silhueta=0.008 e Davies-Bouldin=1.618; essas metricas nao incluem ruido e nao sao diretamente comparaveis com a particao completa do K-Means.
- A concordancia entre K-Means e DBSCAN foi ARI=0.053. ARI=1 seria particao identica; perto de 0 indica pouca concordancia. As premissas diferentes (centroides versus densidade/ruido) explicam parte da discordancia.
- Referencia externa GRAM: ARI K-Means=0.016, DBSCAN=0.013; NMI K-Means=0.021, DBSCAN=0.059. GRAM nao e uma verdade biologica dos grupos, apenas uma referencia de concordancia.
- Com e sem GRAM: ver `../resultados/tabelas/comparacao_com_sem_gram.tsv`. A coluna foi adicionada como one-hot, mantendo os mesmos k/eps; essa comparacao mede o efeito de incluir essa informacao, nao uma melhora causal.
- Estabilidade por cinco subamostras de 80% (ARI contra a particao completa):
- DBSCAN: ARI medio 0.705 (DP 0.040).
- K-Means: ARI medio 0.946 (DP 0.052).

### Conclusao da Tarefa A

Ha semelhancas nos perfis funcionais, mas as metricas e a quantidade de ruido mostram que os grupos nao estao fortemente separados. K-Means oferece uma divisao completa e resumida; DBSCAN identifica zonas densas e muitos isolados sem densidade local. Os isolados de ruido sao candidatos a revisao, nao anomalias biologicas confirmadas.
- Tambem foram sinalizados 26 isolados no percentil 95 ou acima da distancia ao centro K-Means mais proximo; exemplos: 1414, 1418, 1419, 1423, 1425, 1427, 1447, 1452, 1458, 1459. O corte e exploratorio.

## 4. Tarefa B - Reducao de dimensionalidade

- **PCA (linear):** projeta combinacoes lineares que maximizam variancia explicada; eixos sao interpretaveis por seus pesos, mas a tecnica nao captura estrutura nao linear. As duas primeiras componentes explicam 26.9% e 11.5% da variancia (acumulada 38.4%); trustworthiness@10=0.861.
- Maiores pesos absolutos nas duas primeiras componentes (o sinal indica a direcao): PC1: Atividade 20 (-0.48), Atividade 19 (-0.37), Atividade 21 (-0.36), Atividade 17 (-0.36), Atividade 18 (-0.32). PC2: Atividade 16 (-0.87), Atividade 20 (+0.21), Atividade 15 (-0.19), Atividade 18 (+0.17), Atividade 14 (-0.15).
- **t-SNE (nao linear):** prioriza preservar vizinhancas locais em 2D. Foi usada perplexity=30, semente=42, init=PCA e 1000 iteracoes; trustworthiness@10=0.961. Eixos, distancias entre nuvens e tamanhos aparentes nao tem interpretacao direta.
- Variancia explicada e erro de reconstrucao PCA por dimensao estao em `../resultados/tabelas/pca_variancia_reconstrucao.tsv`. Trustworthiness e estabilidade do t-SNE com perplexities 10/30/50 e sementes diferentes estao em `../resultados/tabelas/metricas_reducao_dimensionalidade.tsv`. A sobreposicao mede Jaccard medio dos 10 vizinhos no espaco projetado relativamente ao t-SNE base (perplexity 30, semente 42).
- A sobreposicao Jaccard media dos vizinhos entre configuracoes alternativas de t-SNE e a configuracao base foi 0.552; valores mais baixos indicam que a vizinhanca visual muda com semente ou perplexity.
- As quatro projecoes em `../resultados/figuras/03_projecoes_pca_tsne.png` usam as mesmas atividades e sao coloridas pelas particoes principais K-Means e DBSCAN. Elas servem para visualizar, nao para provar separacao biologica.

## 5. Sensibilidade ao pre-processamento

Foi alterada uma decisao: remover log1p das atividades 02, 14, 15 e 23, mantendo normalizacao min-max, k e semente. A silhueta K-Means mudou de 0.169 para 0.180, Davies-Bouldin de 2.058 para 1.975, e ARI entre particoes foi 0.885. Isso mostra quanto a representacao da cauda longa influencia os grupos; a comparacao completa esta em `../resultados/tabelas/sensibilidade_preprocessamento.tsv`.

## 6. Limitacoes

- Os nomes dos ensaios estao anonimizados; medias altas nao podem ser traduzidas em mecanismos ou aplicacoes especificas.
- Codigos morfologicos representam categorias, nao magnitudes; multiplos codigos em uma celula podem afetar a representacao.
- K-Means depende de k e e sensivel a valores extremos; DBSCAN depende de eps/min_samples e sofre em dimensoes altas/densidades diferentes.
- PCA e linear; t-SNE e sensivel a hiperparametros e preserva principalmente vizinhancas locais. As figuras nao sao prova de grupos biologicos.
- A estabilidade foi avaliada em cinco subamostras de 80%, uma checagem limitada. A colecao de 506 isolados pode nao representar toda a biodiversidade marinha.
- Nenhum cluster prova especie, potencial farmacologico ou propriedade biologica; isso requer validacao laboratorial.

## 7. Arquivos e figuras

Figuras: `../resultados/figuras/01_selecao_k.png`, `../resultados/figuras/02_dbscan_parametros.png`, `../resultados/figuras/03_projecoes_pca_tsne.png`, `../resultados/figuras/04_pca_variancia_erro.png`, `../resultados/figuras/05_contingencia_gram.png`, `../resultados/figuras/06_perfis_atividades.png`, `../resultados/figuras/07_correlacao_atividades.png`, `../resultados/figuras/08_morfologia_gram.png`.
Tabelas: metricas, perfis funcionais/morfologicos, estabilidade, sensibilidade, contingencias e resultados por ID estao em `../resultados/tabelas/`.

## Referencias

- MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability*.
- Ester, M. et al. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *KDD*.
- Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53-65.
- Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, PAMI-1(2), 224-227.
- Hubert, L., & Arabie, P. (1985). Comparing partitions. *Journal of Classification*, 2, 193-218.
- Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: a review and recent developments. *Philosophical Transactions of the Royal Society A*, 374.
- van der Maaten, L., & Hinton, G. (2008). Visualizing data using t-SNE. *Journal of Machine Learning Research*, 9, 2579-2605.
