# Indice dos resultados

Os arquivos desta pasta foram gerados por `analise_completa.py`. O identificador
do isolado permite ligar linhas entre tabelas; ele nao e uma variavel usada
para calcular os grupos.

## Figuras

| Arquivo | Para que serve |
|---|---|
| `01_selecao_k.png` | Inercia (metodo do cotovelo) e silhueta para escolher k no K-Means. |
| `02_dbscan_parametros.png` | k-distancias para apoiar a escolha de eps e variacao dos resultados do DBSCAN. |
| `03_projecoes_pca_tsne.png` | PCA e t-SNE em duas dimensoes, coloridos pelos rótulos K-Means e DBSCAN. |
| `04_pca_variancia_erro.png` | Variancia explicada e erro de reconstrucao conforme aumenta o numero de componentes do PCA. |
| `05_contingencia_gram.png` | Quantidade de isolados de cada classe GRAM em cada grupo. |
| `06_perfis_atividades.png` | Media das 23 atividades em cada grupo K-Means. |
| `07_correlacao_atividades.png` | Correlacao de Pearson entre pares de atividades transformadas. |
| `08_morfologia_gram.png` | Proporcao das categorias morfologicas dentro de cada classe GRAM. |
| `histograma_atividade_14.png`, `histograma_atividade_15.png`, `histograma_atividade_23.png` | Histogramas exploratorios criados anteriormente. |

## Tabelas

| Arquivo | Para que serve |
|---|---|
| `exploracao_dados.tsv` | Tipo, valores ausentes e numero de categorias/valores distintos por coluna no arquivo original. |
| `correlacoes_atividades.tsv` | Correlacao de Pearson entre cada par de atividades, ordenada por magnitude. |
| `resultado_clusterizacao.tsv` | Rótulos K-Means e DBSCAN para cada isolado. No DBSCAN, `-1` significa ruído. |
| `perfis_clusters.tsv` | Quantidade de isolados e media de cada atividade em cada grupo. |
| `perfis_morfologicos_clusters.tsv` | Frequencias e proporcoes das categorias morfologicas em cada grupo. |
| `isolados_atipicos.tsv` | Isolados com distancia ao centro K-Means no percentil 95 ou maior e/ou marcados como ruido pelo DBSCAN. E um sinal exploratorio. |
| `metricas_kmeans.tsv` | Inercia, silhueta e Davies-Bouldin para k de 2 a 10. |
| `metricas_clusters.tsv` | Metricas internas e concordancia externa com GRAM para as particoes principais. |
| `sensibilidade_dbscan.tsv` | Numero de grupos e pontos de ruido para diferentes valores de eps. |
| `k_distancias_dbscan.tsv` | Distancia de cada isolado ao quinto vizinho mais proximo; apoia a escolha de eps. |
| `contingencia_particoes.tsv` | Tabela cruzada para ver quais isolados/grupos K-Means correspondem aos rótulos DBSCAN. |
| `contingencia_gram.tsv` | Contagem de cada classe GRAM dentro dos grupos de cada algoritmo. |
| `comparacao_com_sem_gram.tsv` | ARI e numero de grupos com e sem incluir GRAM nos atributos. |
| `estabilidade_clusters.tsv` | ARI em cinco subamostras de 80%, comparadas com a particao completa. |
| `sensibilidade_preprocessamento.tsv` | Compara os clusters com e sem log1p em quatro atividades. |
| `metricas_reducao_dimensionalidade.tsv` | Trustworthiness e estabilidade local do PCA/t-SNE em diferentes sementes e perplexities. |
| `pca_variancia_reconstrucao.tsv` | Variancia explicada acumulada e erro de reconstrucao PCA por componente. |
| `morfologia_gram.tsv` | Contagem e proporcao de categorias morfologicas dentro de cada classe GRAM. |
| `relatorio_transformacoes_atividades.tsv` | Transformacoes, tipos e ausentes por atividade, se presente. |

Para interpretar primeiro, comece por `relatorios\relatorio_final.html`; as
tabelas sao evidencias detalhadas e auditaveis que sustentam o texto.
