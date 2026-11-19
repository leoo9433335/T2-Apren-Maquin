"""Compara agrupamentos de isolados por suas atividades transformadas."""

import os

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score


ARQUIVO_ENTRADA = "Dados_REG_atividades_transformadas.tsv"
ARQUIVO_RESULTADOS = "resultado_clusterizacao.tsv"
ARQUIVO_PERFIS = "perfis_clusters.tsv"
ARQUIVO_ATIPICOS = "isolados_atipicos.tsv"
ARQUIVO_SENSIBILIDADE = "sensibilidade_dbscan.tsv"
ARQUIVO_RELATORIO = "relatorio_clusterizacao.md"

FAIXA_K = range(2, 9)
DBSCAN_EPS = 0.9
DBSCAN_MIN_SAMPLES = 5
EPS_SENSIBILIDADE = (0.8, 0.85, 0.9, 0.95, 1.0)
SEMENTE = 42


def carregar_dados(pasta):
    caminho = os.path.join(pasta, ARQUIVO_ENTRADA)
    if not os.path.isfile(caminho):
        raise FileNotFoundError(
            "Arquivo não encontrado: {}. Execute primeiro transformer.py."
            .format(caminho)
        )

    df = pd.read_csv(caminho, sep="\t", encoding="utf-8-sig")
    coluna_id = df.columns[0]
    atividades = [
        "Atividade {:02d}".format(numero) for numero in range(1, 24)
    ]
    ausentes = [coluna for coluna in atividades if coluna not in df.columns]
    if ausentes:
        raise ValueError(
            "Atividades não encontradas no arquivo: {}".format(
                ", ".join(ausentes)
            )
        )

    X = df[atividades].apply(pd.to_numeric, errors="raise").astype(float)
    if X.isna().any().any() or not np.isfinite(X.to_numpy()).all():
        raise ValueError(
            "As atividades contêm valores ausentes ou não finitos."
        )
    return df, coluna_id, atividades, X


def avaliar_kmeans(X):
    avaliacoes = []
    modelos = []
    for k in FAIXA_K:
        modelo = KMeans(
            n_clusters=k, random_state=SEMENTE, n_init=20
        )
        rotulos = modelo.fit_predict(X)
        silhueta = silhouette_score(X, rotulos)
        avaliacoes.append(
            {
                "k": k,
                "silhueta": float(silhueta),
                "inercia": float(modelo.inertia_),
            }
        )
        modelos.append((silhueta, modelo, rotulos))

    melhor_indice = max(
        range(len(avaliacoes)),
        key=lambda indice: avaliacoes[indice]["silhueta"],
    )
    return modelos[melhor_indice][1:], pd.DataFrame(avaliacoes)


def avaliar_dbscan(X):
    sensibilidades = []
    for eps in EPS_SENSIBILIDADE:
        rotulos = DBSCAN(
            eps=eps, min_samples=DBSCAN_MIN_SAMPLES
        ).fit_predict(X)
        grupos = set(rotulos) - {-1}
        sensibilidades.append(
            {
                "eps": eps,
                "min_samples": DBSCAN_MIN_SAMPLES,
                "grupos": len(grupos),
                "isolados_ruido": int(np.sum(rotulos == -1)),
            }
        )

    rotulos = DBSCAN(
        eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES
    ).fit_predict(X)
    return rotulos, pd.DataFrame(sensibilidades)


def criar_perfis(df, atividades, rotulos_kmeans, rotulos_dbscan):
    perfis = []
    dados = df[atividades]
    for algoritmo, rotulos in (
        ("K-Means", rotulos_kmeans),
        ("DBSCAN", rotulos_dbscan),
    ):
        for grupo in sorted(set(rotulos)):
            mascara = rotulos == grupo
            perfil = dados.loc[mascara].mean()
            registro = {
                "algoritmo": algoritmo,
                "cluster": int(grupo),
                "isolados": int(mascara.sum()),
            }
            registro.update(perfil.to_dict())
            perfis.append(registro)
    return pd.DataFrame(perfis)


def formatar_perfil(perfis, algoritmo, grupo):
    perfil = perfis.loc[
        (perfis["algoritmo"] == algoritmo)
        & (perfis["cluster"] == grupo)
    ].iloc[0]
    atividades = [
        coluna
        for coluna in perfis.columns
        if coluna.startswith("Atividade ")
    ]
    ordenadas = sorted(
        atividades, key=lambda coluna: perfil[coluna], reverse=True
    )
    return ", ".join(
        "{} ({:.2f})".format(coluna, perfil[coluna])
        for coluna in ordenadas[:5]
    )


def criar_relatorio(
    caminho,
    n_isolados,
    atividades,
    kmeans_rotulos,
    melhor_k,
    silhueta_kmeans,
    perfis,
    rotulos_dbscan,
    silhueta_dbscan,
    sensibilidades,
    ids,
    limiar_atipico,
    quantidade_atipicos_kmeans,
):
    grupos_kmeans = sorted(set(kmeans_rotulos))
    grupos_dbscan = sorted(set(rotulos_dbscan) - {-1})
    ruido_dbscan = int(np.sum(rotulos_dbscan == -1))
    linhas = [
        "# Análise de agrupamento dos isolados",
        "",
        "## Dados e preparação",
        "",
        "- Foram analisados {} isolados e {} atividades (Atividades 01–23)."
        .format(n_isolados, len(atividades)),
        "- As atividades foram lidas de `Dados_REG_atividades_transformadas.tsv`, "
        "já transformadas para escalas comparáveis entre 0 e 1.",
        "- O identificador foi mantido apenas para rastrear os isolados; as "
        "colunas indicadoras de dados ausentes não entraram no cálculo.",
        "- Ambos os métodos usam distância euclidiana. Portanto, os resultados "
        "dependem da transformação prévia e do peso semelhante atribuído a "
        "cada atividade.",
        "",
        "## Métodos e premissas",
        "",
        "- **K-Means:** particiona todos os isolados em `k` grupos, minimizando "
        "a soma das distâncias quadráticas aos centroides. Requer escolher "
        "`k` e favorece grupos compactos, aproximadamente esféricos e de "
        "tamanho semelhante; não identifica ruído separadamente.",
        "- **DBSCAN:** conecta pontos que tenham pelo menos `min_samples` "
        "vizinhos dentro do raio `eps`. Não exige definir o número de grupos "
        "e marca como ruído os pontos sem densidade suficiente. Depende "
        "fortemente de `eps`/`min_samples` e tem dificuldade com densidades "
        "muito diferentes e muitos atributos.",
        "",
        "## Resultados",
        "",
        "- **K-Means:** `k = {}` foi selecionado pela maior silhueta entre "
        "`k=2` e `k=8` (silhueta = {:.3f}). Essa pontuação baixa indica "
        "separação fraca entre os grupos; o número de grupos é uma escolha "
        "útil para resumir os dados, não uma divisão natural comprovada."
        .format(melhor_k, silhueta_kmeans),
    ]

    for grupo in grupos_kmeans:
        tamanho = int(np.sum(kmeans_rotulos == grupo))
        amostras = ids[kmeans_rotulos == grupo][:10]
        linhas.append(
            "- K-Means grupo {}: {} isolados; atividades com maiores médias: "
            "{}; exemplos de IDs: {}."
            .format(
                grupo,
                tamanho,
                formatar_perfil(perfis, "K-Means", grupo),
                ", ".join(str(valor) for valor in amostras),
            )
        )

    grupos_dbscan_texto = ", ".join(
        "{} ({} isolados)".format(
            grupo, int(np.sum(rotulos_dbscan == grupo))
        )
        for grupo in grupos_dbscan
    )
    linhas.extend(
        [
            "",
            "- **DBSCAN:** com `eps = {:.2f}` e `min_samples = {}`, foram "
            "encontrados {} grupos ({}) e {} isolados classificados como "
            "ruído ({}%). A silhueta calculada apenas nos pontos agrupados é "
            "{:.3f}; ela não inclui o ruído e não é diretamente comparável à "
            "silhueta do K-Means."
            .format(
                DBSCAN_EPS,
                DBSCAN_MIN_SAMPLES,
                len(grupos_dbscan),
                grupos_dbscan_texto or "nenhum grupo",
                ruido_dbscan,
                100.0 * ruido_dbscan / n_isolados,
                silhueta_dbscan,
            ),
        ]
    )
    for grupo in grupos_dbscan:
        amostras = ids[rotulos_dbscan == grupo][:10]
        linhas.append(
            "- DBSCAN grupo {}: atividades com maiores médias: {}; "
            "exemplos de IDs: {}."
            .format(
                grupo,
                formatar_perfil(perfis, "DBSCAN", grupo),
                ", ".join(str(valor) for valor in amostras),
            )
        )
    exemplos_ruido = ids[rotulos_dbscan == -1][:10]
    linhas.extend(
        [
            "- Exemplos classificados como ruído pelo DBSCAN: {}."
            .format(", ".join(str(valor) for valor in exemplos_ruido)),
            "- A análise de sensibilidade em `sensibilidade_dbscan.tsv` mostra "
            "que o número de grupos e de pontos de ruído muda com `eps`; "
            "portanto, não há um número único de grupos definido pelos dados.",
            "",
            "## Resposta à pergunta",
            "",
            "Há padrões de semelhança, mas a evidência de grupos bem separados "
            "é fraca. O K-Means resume os 506 isolados em {} grupos; o DBSCAN "
            "com os parâmetros avaliados forma grupos menores e deixa muitos "
            "isolados sem densidade suficiente. Os perfis de atividades e os "
            "IDs completos por método estão em `perfis_clusters.tsv` e "
            "`resultado_clusterizacao.tsv`."
            .format(melhor_k),
            "",
            "Os isolados marcados como ruído pelo DBSCAN são candidatos a "
            "investigação por serem pouco semelhantes às vizinhanças locais, "
            "mas isso não prova que sejam biologicamente anormais. Para "
            "complementar, `isolados_atipicos.tsv` também sinaliza os "
            "isolados cuja distância ao centro K-Means mais próximo está no "
            "percentil 95 ou acima (limiar = {:.3f}; {} isolados). Esse "
            "limiar é exploratório, não diagnóstico."
            .format(limiar_atipico, quantidade_atipicos_kmeans),
            "",
        ]
    )
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))


def main():
    pasta = os.path.dirname(os.path.abspath(__file__))
    df, coluna_id, atividades, X = carregar_dados(pasta)

    (modelo_kmeans, rotulos_kmeans), avaliacoes_kmeans = avaliar_kmeans(X)
    melhor_k = int(modelo_kmeans.n_clusters)
    silhueta_kmeans = float(
        avaliacoes_kmeans.loc[
            avaliacoes_kmeans["k"] == melhor_k, "silhueta"
        ].iloc[0]
    )
    rotulos_dbscan, sensibilidades = avaliar_dbscan(X)

    resultados = df[[coluna_id]].copy()
    resultados["KMeans_cluster"] = rotulos_kmeans
    resultados["DBSCAN_cluster"] = rotulos_dbscan

    perfis = criar_perfis(
        df, atividades, rotulos_kmeans, rotulos_dbscan
    )
    distancias = modelo_kmeans.transform(X).min(axis=1)
    limiar_atipico = float(np.quantile(distancias, 0.95))
    atipicos = resultados.copy()
    atipicos["distancia_centroide_kmeans"] = distancias
    atipicos["kmeans_distancia_p95_ou_maior"] = distancias >= limiar_atipico
    atipicos["dbscan_ruido"] = rotulos_dbscan == -1
    atipicos = atipicos.loc[
        atipicos["kmeans_distancia_p95_ou_maior"] | atipicos["dbscan_ruido"]
    ]

    mascara_agrupados = rotulos_dbscan != -1
    grupos_dbscan = set(rotulos_dbscan[mascara_agrupados])
    silhueta_dbscan = (
        float(
            silhouette_score(
                X.loc[mascara_agrupados],
                rotulos_dbscan[mascara_agrupados],
            )
        )
        if len(grupos_dbscan) > 1
        else float("nan")
    )

    resultados.to_csv(
        os.path.join(pasta, ARQUIVO_RESULTADOS),
        sep="\t",
        index=False,
        encoding="utf-8-sig",
    )
    perfis.to_csv(
        os.path.join(pasta, ARQUIVO_PERFIS),
        sep="\t",
        index=False,
        encoding="utf-8-sig",
    )
    atipicos.to_csv(
        os.path.join(pasta, ARQUIVO_ATIPICOS),
        sep="\t",
        index=False,
        encoding="utf-8-sig",
    )
    sensibilidades.to_csv(
        os.path.join(pasta, ARQUIVO_SENSIBILIDADE),
        sep="\t",
        index=False,
        encoding="utf-8-sig",
    )
    criar_relatorio(
        os.path.join(pasta, ARQUIVO_RELATORIO),
        len(df),
        atividades,
        rotulos_kmeans,
        melhor_k,
        silhueta_kmeans,
        perfis,
        rotulos_dbscan,
        silhueta_dbscan,
        sensibilidades,
        df[coluna_id].to_numpy(),
        limiar_atipico,
        int(np.sum(distancias >= limiar_atipico)),
    )

    print("Isolados analisados: {}".format(len(df)))
    print(
        "K-Means: {} grupos; silhueta = {:.3f}".format(
            melhor_k, silhueta_kmeans
        )
    )
    print(
        "DBSCAN: {} grupos; {} isolados classificados como ruído "
        "(eps={}, min_samples={})".format(
            len(grupos_dbscan),
            int(np.sum(rotulos_dbscan == -1)),
            DBSCAN_EPS,
            DBSCAN_MIN_SAMPLES,
        )
    )
    for arquivo in (
        ARQUIVO_RESULTADOS,
        ARQUIVO_PERFIS,
        ARQUIVO_ATIPICOS,
        ARQUIVO_SENSIBILIDADE,
        ARQUIVO_RELATORIO,
    ):
        print("Arquivo gerado: {}".format(arquivo))


if __name__ == "__main__":
    main()