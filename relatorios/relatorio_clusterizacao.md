# Análise de agrupamento dos isolados

## Dados e preparação

- Foram analisados 506 isolados e 23 atividades (Atividades 01–23).
- As atividades foram lidas de `Dados_REG_atividades_transformadas.tsv`, já transformadas para escalas comparáveis entre 0 e 1.
- O identificador foi mantido apenas para rastrear os isolados; as colunas indicadoras de dados ausentes não entraram no cálculo.
- Ambos os métodos usam distância euclidiana. Portanto, os resultados dependem da transformação prévia e do peso semelhante atribuído a cada atividade.

## Métodos e premissas

- **K-Means:** particiona todos os isolados em `k` grupos, minimizando a soma das distâncias quadráticas aos centroides. Requer escolher `k` e favorece grupos compactos, aproximadamente esféricos e de tamanho semelhante; não identifica ruído separadamente.
- **DBSCAN:** conecta pontos que tenham pelo menos `min_samples` vizinhos dentro do raio `eps`. Não exige definir o número de grupos e marca como ruído os pontos sem densidade suficiente. Depende fortemente de `eps`/`min_samples` e tem dificuldade com densidades muito diferentes e muitos atributos.

## Resultados

- **K-Means:** `k = 2` foi selecionado pela maior silhueta entre `k=2` e `k=8` (silhueta = 0.169). Essa pontuação baixa indica separação fraca entre os grupos; o número de grupos é uma escolha útil para resumir os dados, não uma divisão natural comprovada.
- K-Means grupo 0: 280 isolados; atividades com maiores médias: Atividade 20 (0.90), Atividade 21 (0.87), Atividade 16 (0.81), Atividade 19 (0.70), Atividade 17 (0.64); exemplos de IDs: 1413, 1414, 1415, 1418, 1422, 1427, 1430, 1431, 1447, 1448.
- K-Means grupo 1: 226 isolados; atividades com maiores médias: Atividade 08 (0.59), Atividade 16 (0.54), Atividade 09 (0.50), Atividade 13 (0.50), Atividade 10 (0.45); exemplos de IDs: 1417, 1419, 1423, 1424, 1425, 1426, 1429, 1446, 1449, 1454.

- **DBSCAN:** com `eps = 0.90` e `min_samples = 5`, foram encontrados 6 grupos (0 (203 isolados), 1 (10 isolados), 2 (76 isolados), 3 (10 isolados), 4 (7 isolados), 5 (5 isolados)) e 195 isolados classificados como ruído (38.537549407114625%). A silhueta calculada apenas nos pontos agrupados é 0.008; ela não inclui o ruído e não é diretamente comparável à silhueta do K-Means.
- DBSCAN grupo 0: atividades com maiores médias: Atividade 16 (1.00), Atividade 21 (0.79), Atividade 20 (0.69), Atividade 13 (0.61), Atividade 08 (0.60); exemplos de IDs: 1413, 1415, 1417, 1422, 1426, 1430, 1431, 1448, 1449, 1450.
- DBSCAN grupo 1: atividades com maiores médias: Atividade 16 (1.00), Atividade 19 (0.90), Atividade 13 (0.60), Atividade 09 (0.59), Atividade 23 (0.59); exemplos de IDs: 1424, 1429, 1446, 1489, 1495, 1660, 1671, 1765, 1869, 1935.
- DBSCAN grupo 2: atividades com maiores médias: Atividade 08 (0.60), Atividade 21 (0.60), Atividade 20 (0.50), Atividade 13 (0.48), Atividade 09 (0.47); exemplos de IDs: 1456, 1457, 1466, 1473, 1483, 1486, 1487, 1491, 1493, 1505.
- DBSCAN grupo 3: atividades com maiores médias: Atividade 01 (1.00), Atividade 16 (1.00), Atividade 21 (0.87), Atividade 20 (0.80), Atividade 13 (0.67); exemplos de IDs: 1571, 1581, 1582, 1584, 1649, 1691, 1692, 1738, 1782, 1783.
- DBSCAN grupo 4: atividades com maiores médias: Atividade 20 (0.95), Atividade 21 (0.86), Atividade 23 (0.75), Atividade 13 (0.67), Atividade 17 (0.67); exemplos de IDs: 1583, 1704, 1770, 1800, 1803, 1846, 1899.
- DBSCAN grupo 5: atividades com maiores médias: Atividade 03 (1.00), Atividade 16 (1.00), Atividade 17 (1.00), Atividade 18 (1.00), Atividade 19 (1.00); exemplos de IDs: 1523, 1732, 1822, 1959, 1963.
- Exemplos classificados como ruído pelo DBSCAN: 1414, 1418, 1419, 1423, 1425, 1427, 1447, 1452, 1458, 1459.
- A análise de sensibilidade em `sensibilidade_dbscan.tsv` mostra que o número de grupos e de pontos de ruído muda com `eps`; portanto, não há um número único de grupos definido pelos dados.

## Resposta à pergunta

Há padrões de semelhança, mas a evidência de grupos bem separados é fraca. O K-Means resume os 506 isolados em 2 grupos; o DBSCAN com os parâmetros avaliados forma grupos menores e deixa muitos isolados sem densidade suficiente. Os perfis de atividades e os IDs completos por método estão em `perfis_clusters.tsv` e `resultado_clusterizacao.tsv`.

Os isolados marcados como ruído pelo DBSCAN são candidatos a investigação por serem pouco semelhantes às vizinhanças locais, mas isso não prova que sejam biologicamente anormais. Para complementar, `isolados_atipicos.tsv` também sinaliza os isolados cuja distância ao centro K-Means mais próximo está no percentil 95 ou acima (limiar = 1.541; 26 isolados). Esse limiar é exploratório, não diagnóstico.
