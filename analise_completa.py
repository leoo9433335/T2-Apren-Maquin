"""Reproduz as tarefas de agrupamento e reducao de dimensionalidade."""

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, trustworthiness
from sklearn.metrics import (
    adjusted_rand_score,
    davies_bouldin_score,
    normalized_mutual_info_score,
    silhouette_score,
)
from sklearn.neighbors import NearestNeighbors


SEED = 42
K_VALUES = range(2, 11)
MIN_SAMPLES = 5
EPS = 0.9
EPS_VALUES = (0.8, 0.85, 0.9, 0.95, 1.0)
TSNE_PERPLEXITY = 30
ACTIVITIES_FILE = "Dados_REG_atividades_transformadas.tsv"
RAW_FILE = "Dados_REG_transformado.tsv"
ORIGINAL_FILE = "Dados_REG.csv"


def save_tsv(frame, path):
    frame.to_csv(path, sep="\t", index=False, encoding="utf-8-sig")


def internal_metrics(X, labels, ignore_noise=False):
    labels = np.asarray(labels)
    mask = labels != -1 if ignore_noise else np.ones(len(labels), dtype=bool)
    values = labels[mask]
    distinct = set(values)
    if len(distinct) < 2 or len(values) <= len(distinct):
        return float("nan"), float("nan")
    return (
        float(silhouette_score(X.loc[mask], values)),
        float(davies_bouldin_score(X.loc[mask], values)),
    )


def cluster_labels(X, algorithm, k=None):
    if algorithm == "K-Means":
        return KMeans(
            n_clusters=k, random_state=SEED, n_init=20
        ).fit_predict(X)
    return DBSCAN(eps=EPS, min_samples=MIN_SAMPLES).fit_predict(X)


def kmeans_metrics(X, labels, gram):
    silhouette, db_index = internal_metrics(X, labels)
    return {
        "algoritmo": "K-Means",
        "grupos": len(set(labels)),
        "ruido": 0,
        "silhueta": silhouette,
        "davies_bouldin": db_index,
        "ARI_vs_GRAM": float(adjusted_rand_score(gram, labels)),
        "NMI_vs_GRAM": float(normalized_mutual_info_score(gram, labels)),
    }


def dbscan_metrics(X, labels, gram):
    groups = set(labels) - {-1}
    silhouette, db_index = internal_metrics(X, labels, ignore_noise=True)
    return {
        "algoritmo": "DBSCAN",
        "grupos": len(groups),
        "ruido": int(np.sum(np.asarray(labels) == -1)),
        "silhueta_sem_ruido": silhouette,
        "davies_bouldin_sem_ruido": db_index,
        "ARI_vs_GRAM": float(adjusted_rand_score(gram, labels)),
        "NMI_vs_GRAM": float(normalized_mutual_info_score(gram, labels)),
    }


def make_plots(
    out,
    k_table,
    kdistances,
    eps_table,
    pca,
    pca_2d,
    tsne_2d,
    labels_kmeans,
    labels_dbscan,
    pca_mse,
    gram_table,
    profile_table,
):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(k_table["k"], k_table["inercia"], marker="o")
    axes[0].set(title="Metodo do cotovelo - K-Means", xlabel="k", ylabel="Inercia")
    axes[0].set_xticks(k_table["k"])
    axes[1].plot(k_table["k"], k_table["silhueta"], marker="o", color="darkorange")
    axes[1].set(title="Silhueta media - K-Means", xlabel="k", ylabel="Silhueta")
    axes[1].set_xticks(k_table["k"])
    fig.tight_layout()
    fig.savefig(os.path.join(out, "01_selecao_k.png"), dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(np.arange(1, len(kdistances) + 1), kdistances, color="navy")
    axes[0].axhline(EPS, color="crimson", linestyle="--", label="eps = {:.2f}".format(EPS))
    axes[0].set(
        title="Grafico de k-distancias (k = {})".format(MIN_SAMPLES),
        xlabel="Isolados ordenados",
        ylabel="Distancia ao k-esimo vizinho",
    )
    axes[0].legend()
    axes[1].plot(eps_table["eps"], eps_table["grupos"], marker="o", label="Grupos")
    axes[1].plot(
        eps_table["eps"], eps_table["ruido"], marker="s", label="Ruido"
    )
    axes[1].set(title="Sensibilidade do DBSCAN", xlabel="eps", ylabel="Quantidade")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out, "02_dbscan_parametros.png"), dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    panels = [
        (axes[0, 0], pca_2d, labels_kmeans, "PCA colorido por K-Means"),
        (axes[0, 1], pca_2d, labels_dbscan, "PCA colorido por DBSCAN"),
        (axes[1, 0], tsne_2d, labels_kmeans, "t-SNE colorido por K-Means"),
        (axes[1, 1], tsne_2d, labels_dbscan, "t-SNE colorido por DBSCAN"),
    ]
    for axis, coordinates, labels, title in panels:
        scatter = axis.scatter(
            coordinates[:, 0],
            coordinates[:, 1],
            c=labels,
            cmap="tab20",
            s=20,
            alpha=0.8,
        )
        axis.set_title(title)
        axis.set_xlabel("Dimensao 1")
        axis.set_ylabel("Dimensao 2")
        fig.colorbar(scatter, ax=axis, label="Cluster (-1 = ruido)")
    fig.suptitle("Projecoes das 23 atividades (semente = {})".format(SEED))
    fig.tight_layout()
    fig.savefig(os.path.join(out, "03_projecoes_pca_tsne.png"), dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].bar(
        ["PC1", "PC2"],
        pca.explained_variance_ratio_[:2],
        color=["steelblue", "darkorange"],
    )
    axes[0].set(
        title="Variancia explicada pelo PCA",
        ylabel="Proporcao da variancia",
    )
    axes[1].plot(
        np.arange(1, len(pca_mse) + 1), pca_mse, marker="o", markersize=3
    )
    axes[1].set(
        title="Reconstrucao PCA",
        xlabel="Numero de componentes",
        ylabel="Erro quadratico medio",
    )
    fig.tight_layout()
    fig.savefig(os.path.join(out, "04_pca_variancia_erro.png"), dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for axis, algorithm, title in (
        (axes[0], "K-Means", "K-Means vs GRAM"),
        (axes[1], "DBSCAN", "DBSCAN vs GRAM"),
    ):
        matrix = gram_table.loc[
            gram_table["algoritmo"] == algorithm
        ].pivot(
            index="cluster", columns="GRAM", values="isolados"
        ).fillna(0)
        image = axis.imshow(matrix.values, aspect="auto", cmap="Blues")
        axis.set_xticks(np.arange(len(matrix.columns)))
        axis.set_xticklabels(matrix.columns, rotation=30, ha="right")
        axis.set_yticks(np.arange(len(matrix.index)))
        axis.set_yticklabels(matrix.index)
        axis.set_title(title)
        axis.set_xlabel("Classe GRAM")
        axis.set_ylabel("Cluster")
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, int(matrix.iloc[row, col]), ha="center", va="center")
        fig.colorbar(image, ax=axis, label="Isolados")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "05_contingencia_gram.png"), dpi=160)
    plt.close(fig)

    activities = [
        col for col in profile_table.columns if col.startswith("Atividade ")
    ]
    means = profile_table.loc[
        profile_table["algoritmo"] == "K-Means",
        ["cluster"] + activities,
    ].set_index("cluster")
    fig, axis = plt.subplots(figsize=(13, 5))
    image = axis.imshow(means.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    axis.set_xticks(np.arange(len(activities)))
    axis.set_xticklabels(activities, rotation=90)
    axis.set_yticks(np.arange(len(means.index)))
    axis.set_yticklabels(["K-Means {}".format(i) for i in means.index])
    axis.set_title("Perfil medio das atividades por grupo K-Means")
    fig.colorbar(image, ax=axis, label="Media transformada (0-1)")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "06_perfis_atividades.png"), dpi=160)
    plt.close(fig)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    activity_path = os.path.join(root, ACTIVITIES_FILE)
    raw_path = os.path.join(root, RAW_FILE)
    original_path = os.path.join(root, ORIGINAL_FILE)
    for path in (activity_path, raw_path, original_path):
        if not os.path.isfile(path):
            raise FileNotFoundError("Arquivo necessario nao encontrado: {}".format(path))

    transformed = pd.read_csv(activity_path, sep="\t", encoding="utf-8-sig")
    original_clean = pd.read_csv(raw_path, sep="\t", encoding="utf-8-sig")
    original_data = pd.read_csv(original_path, sep="\t", encoding="utf-8-sig")
    id_column = transformed.columns[0]
    activities = [
        "Atividade {:02d}".format(i) for i in range(1, 24)
    ]
    missing_activities = [c for c in activities if c not in transformed.columns]
    if missing_activities:
        raise ValueError("Atividades ausentes: {}".format(missing_activities))
    if len(transformed) != len(original_clean):
        raise ValueError("Arquivos transformados tem quantidades de linhas diferentes.")
    if not transformed[id_column].equals(original_clean[id_column]):
        raise ValueError("IDs/ordem dos arquivos de atividades e dados limpos divergem.")
    X = transformed[activities].astype(float)
    if X.isna().any().any() or not np.isfinite(X.values).all():
        raise ValueError("A matriz de atividades contem valores ausentes ou infinitos.")
    gram = original_clean["GRAM"].fillna("Ausente").astype(str).values
    ids = transformed[id_column].values

    # Auditoria simples do arquivo original, antes das transformacoes.
    missing_counts = original_data.isna().sum()
    exploration = pd.DataFrame(
        {
            "coluna": original_data.columns,
            "tipo_pandas": [str(t) for t in original_data.dtypes],
            "ausentes": [int(missing_counts[c]) for c in original_data.columns],
            "percentual_ausente": [
                float(100 * missing_counts[c] / len(original_data))
                for c in original_data.columns
            ],
            "valores_distintos": [
                int(original_data[c].nunique(dropna=True))
                for c in original_data.columns
            ],
        }
    )
    save_tsv(exploration, os.path.join(root, "exploracao_dados.tsv"))
    id_duplicates = int(original_data.iloc[:, 0].duplicated().sum())

    # K-Means: varre k=2..10; escolhe a maior silhueta e registra o cotovelo.
    k_rows = []
    k_labels = {}
    k_models = {}
    for k in K_VALUES:
        model = KMeans(n_clusters=k, random_state=SEED, n_init=20)
        labels = model.fit_predict(X)
        sil, db = internal_metrics(X, labels)
        k_labels[k] = labels
        k_models[k] = model
        k_rows.append(
            {
                "k": k,
                "inercia": float(model.inertia_),
                "silhueta": sil,
                "davies_bouldin": db,
            }
        )
    k_table = pd.DataFrame(k_rows)
    best_k = int(
        k_table.sort_values(
            ["silhueta", "k"], ascending=[False, True]
        ).iloc[0]["k"]
    )
    labels_kmeans = k_labels[best_k]

    # DBSCAN: eps e min_samples sao explicitados e avaliados por sensibilidade.
    neighbor_model = NearestNeighbors(n_neighbors=MIN_SAMPLES)
    neighbor_model.fit(X)
    distances = np.sort(neighbor_model.kneighbors(X)[0][:, -1])
    labels_dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES).fit_predict(X)
    eps_rows = []
    for eps_value in EPS_VALUES:
        trial = DBSCAN(
            eps=eps_value, min_samples=MIN_SAMPLES
        ).fit_predict(X)
        eps_rows.append(
            {
                "eps": eps_value,
                "min_samples": MIN_SAMPLES,
                "grupos": len(set(trial) - {-1}),
                "ruido": int(np.sum(trial == -1)),
            }
        )
    eps_table = pd.DataFrame(eps_rows)

    # Particoes, perfis funcionais e perfis morfologicos dos grupos.
    results = pd.DataFrame(
        {
            id_column: ids,
            "KMeans_cluster": labels_kmeans,
            "DBSCAN_cluster": labels_dbscan,
        }
    )
    save_tsv(results, os.path.join(root, "resultado_clusterizacao.tsv"))
    profile_rows = []
    morphology_rows = []
    morphology = [
        c
        for c in (
            "GRAM", "Cor", "Cores", "Borda", "Textura",
            "Forma", "Brilho", "Muco", "Relevo",
        )
        if c in original_clean.columns
    ]
    for algorithm, labels in (
        ("K-Means", labels_kmeans),
        ("DBSCAN", labels_dbscan),
    ):
        for cluster in sorted(set(labels)):
            mask = labels == cluster
            row = {
                "algoritmo": algorithm,
                "cluster": int(cluster),
                "isolados": int(mask.sum()),
            }
            row.update(X.loc[mask].mean().to_dict())
            profile_rows.append(row)
            for column in morphology:
                values = original_clean.loc[mask, column].fillna("Ausente").astype(str)
                counts = values.value_counts()
                for value, count in counts.items():
                    morphology_rows.append(
                        {
                            "algoritmo": algorithm,
                            "cluster": int(cluster),
                            "isolados": int(mask.sum()),
                            "caracteristica": column,
                            "categoria": value,
                            "frequencia": int(count),
                            "proporcao": float(count / mask.sum()),
                        }
                    )
    profiles = pd.DataFrame(profile_rows)
    morphology_profiles = pd.DataFrame(morphology_rows)
    save_tsv(profiles, os.path.join(root, "perfis_clusters.tsv"))
    save_tsv(
        morphology_profiles,
        os.path.join(root, "perfis_morfologicos_clusters.tsv"),
    )
    save_tsv(k_table, os.path.join(root, "metricas_kmeans.tsv"))
    save_tsv(eps_table, os.path.join(root, "sensibilidade_dbscan.tsv"))
    save_tsv(
        pd.DataFrame({"ordem": np.arange(1, len(distances) + 1), "distancia_k": distances}),
        os.path.join(root, "k_distancias_dbscan.tsv"),
    )

    # Duas metricas internas e referencia externa GRAM para as duas particoes.
    metric_rows = [
        kmeans_metrics(X, labels_kmeans, gram),
        dbscan_metrics(X, labels_dbscan, gram),
    ]
    save_tsv(
        pd.DataFrame(metric_rows),
        os.path.join(root, "metricas_clusters.tsv"),
    )
    partition_ari = float(adjusted_rand_score(labels_kmeans, labels_dbscan))
    contingency = pd.crosstab(
        pd.Series(labels_kmeans, name="KMeans_cluster"),
        pd.Series(labels_dbscan, name="DBSCAN_cluster"),
        margins=True,
    )
    contingency.to_csv(
        os.path.join(root, "contingencia_particoes.tsv"),
        sep="\t",
        encoding="utf-8-sig",
    )

    gram_table = pd.concat(
        [
            pd.DataFrame(
                {"algoritmo": "K-Means", "cluster": labels_kmeans, "GRAM": gram}
            ),
            pd.DataFrame(
                {"algoritmo": "DBSCAN", "cluster": labels_dbscan, "GRAM": gram}
            ),
        ],
        ignore_index=True,
    )
    gram_counts = (
        gram_table.groupby(["algoritmo", "cluster", "GRAM"])
        .size()
        .rename("isolados")
        .reset_index()
    )
    save_tsv(gram_counts, os.path.join(root, "contingencia_gram.tsv"))

    # Com e sem GRAM: somente a coluna GRAM e adicionada, codificada em one-hot.
    gram_features = pd.get_dummies(
        original_clean["GRAM"].fillna("Ausente").astype(str),
        prefix="GRAM",
        dtype=float,
    )
    X_with_gram = pd.concat(
        [X.reset_index(drop=True), gram_features.reset_index(drop=True)], axis=1
    )
    labels_kmeans_gram = KMeans(
        n_clusters=best_k, random_state=SEED, n_init=20
    ).fit_predict(X_with_gram)
    labels_dbscan_gram = DBSCAN(
        eps=EPS, min_samples=MIN_SAMPLES
    ).fit_predict(X_with_gram)
    gram_comparison = pd.DataFrame(
        [
            {
                "algoritmo": "K-Means",
                "grupos_sem_gram": len(set(labels_kmeans)),
                "grupos_com_gram": len(set(labels_kmeans_gram)),
                "ARI_particoes": float(
                    adjusted_rand_score(labels_kmeans, labels_kmeans_gram)
                ),
            },
            {
                "algoritmo": "DBSCAN",
                "grupos_sem_gram": len(set(labels_dbscan) - {-1}),
                "grupos_com_gram": len(set(labels_dbscan_gram) - {-1}),
                "ARI_particoes": float(
                    adjusted_rand_score(labels_dbscan, labels_dbscan_gram)
                ),
            },
        ]
    )
    save_tsv(
        gram_comparison,
        os.path.join(root, "comparacao_com_sem_gram.tsv"),
    )

    # Estabilidade: ARI entre particao completa e cinco ajustes em subamostras 80%.
    rng = np.random.RandomState(SEED)
    stability_rows = []
    for algorithm, baseline, k in (
        ("K-Means", labels_kmeans, best_k),
        ("DBSCAN", labels_dbscan, None),
    ):
        for run in range(5):
            selected = np.sort(
                rng.choice(len(X), size=int(0.8 * len(X)), replace=False)
            )
            sample_X = X.iloc[selected]
            if algorithm == "K-Means":
                sample_labels = KMeans(
                    n_clusters=k, random_state=SEED + run + 1, n_init=20
                ).fit_predict(sample_X)
            else:
                sample_labels = DBSCAN(
                    eps=EPS, min_samples=MIN_SAMPLES
                ).fit_predict(sample_X)
            stability_rows.append(
                {
                    "algoritmo": algorithm,
                    "repeticao": run + 1,
                    "proporcao_amostra": 0.8,
                    "ARI_vs_particao_completa": float(
                        adjusted_rand_score(baseline[selected], sample_labels)
                    ),
                }
            )
    stability = pd.DataFrame(stability_rows)
    save_tsv(stability, os.path.join(root, "estabilidade_clusters.tsv"))
    stability_summary = stability.groupby("algoritmo")[
        "ARI_vs_particao_completa"
    ].agg(["mean", "std"])

    # Sensibilidade a uma decisao: transformar as 4 atividades sem log1p.
    no_log = X.copy()
    log_activities = [
        "Atividade 02", "Atividade 14", "Atividade 15", "Atividade 23"
    ]
    for column in log_activities:
        raw_values = pd.to_numeric(original_clean[column], errors="coerce")
        observed = raw_values.dropna()
        minimum, maximum = float(observed.min()), float(observed.max())
        if maximum == minimum:
            no_log[column] = 0.0
        else:
            scaled = (raw_values - minimum) / (maximum - minimum)
            no_log[column] = scaled.fillna(float(scaled.median()))
    no_log_labels = KMeans(
        n_clusters=best_k, random_state=SEED, n_init=20
    ).fit_predict(no_log)
    no_log_silhouette, no_log_db = internal_metrics(no_log, no_log_labels)
    baseline_silhouette, baseline_db = internal_metrics(X, labels_kmeans)
    preprocessing_sensitivity = pd.DataFrame(
        [
            {
                "cenario": "Original: log1p nas atividades 02,14,15,23",
                "k": best_k,
                "silhueta": baseline_silhouette,
                "davies_bouldin": baseline_db,
                "ARI_vs_original": 1.0,
            },
            {
                "cenario": "Alternativo: sem log1p nas atividades 02,14,15,23",
                "k": best_k,
                "silhueta": no_log_silhouette,
                "davies_bouldin": no_log_db,
                "ARI_vs_original": float(
                    adjusted_rand_score(labels_kmeans, no_log_labels)
                ),
            },
        ]
    )
    save_tsv(
        preprocessing_sensitivity,
        os.path.join(root, "sensibilidade_preprocessamento.tsv"),
    )

    # Tarefa B: PCA linear e t-SNE nao linear sobre as mesmas 23 atividades.
    pca = PCA(n_components=len(activities), random_state=SEED)
    pca_coordinates = pca.fit_transform(X)
    pca_2d = pca_coordinates[:, :2]
    pca_mse = []
    for dimensions in range(1, len(activities) + 1):
        reconstructed = (
            pca_coordinates[:, :dimensions]
            @ pca.components_[:dimensions, :]
            + pca.mean_
        )
        pca_mse.append(float(np.mean((X.values - reconstructed) ** 2)))
    pca_trust = float(trustworthiness(X, pca_2d, n_neighbors=10))

    tsne_configs = [(10, 42), (30, 7), (30, 42), (30, 99), (50, 42)]
    embeddings = {}
    for perplexity, seed in tsne_configs:
        embedding = TSNE(
            n_components=2,
            perplexity=perplexity,
            random_state=seed,
            init="pca",
            learning_rate=200.0,
            n_iter=1000,
        ).fit_transform(X)
        embeddings[(perplexity, seed)] = embedding
    tsne_2d = embeddings[(TSNE_PERPLEXITY, SEED)]

    def neighbor_sets(coordinates, count=10):
        indices = NearestNeighbors(n_neighbors=count + 1).fit(coordinates)
        return indices.kneighbors(coordinates, return_distance=False)[:, 1:]

    baseline_neighbors = neighbor_sets(tsne_2d)
    projection_rows = [
        {
            "metodo": "PCA",
            "perplexity": "",
            "semente": SEED,
            "trustworthiness_k10": pca_trust,
            "sobreposicao_vizinhos_vs_base": 1.0,
        }
    ]
    for (perplexity, seed), embedding in embeddings.items():
        current_neighbors = neighbor_sets(embedding)
        overlap = np.mean(
            [
                len(set(left).intersection(set(right)))
                / float(len(set(left).union(set(right))))
                for left, right in zip(baseline_neighbors, current_neighbors)
            ]
        )
        projection_rows.append(
            {
                "metodo": "t-SNE",
                "perplexity": perplexity,
                "semente": seed,
                "trustworthiness_k10": float(
                    trustworthiness(X, embedding, n_neighbors=10)
                ),
                "sobreposicao_vizinhos_vs_base": float(overlap),
            }
        )
    projections = pd.DataFrame(projection_rows)
    save_tsv(
        projections,
        os.path.join(root, "metricas_reducao_dimensionalidade.tsv"),
    )
    save_tsv(
        pd.DataFrame(
            {
                "componente": np.arange(1, len(activities) + 1),
                "variancia_explicada": pca.explained_variance_ratio_,
                "variancia_acumulada": np.cumsum(
                    pca.explained_variance_ratio_
                ),
                "erro_reconstrucao_mse": pca_mse,
            }
        ),
        os.path.join(root, "pca_variancia_reconstrucao.tsv"),
    )

    distances_table = pd.DataFrame(
        {"ordem": np.arange(1, len(distances) + 1), "distancia_k": distances}
    )
    # Relatorio de reproducao e interpretacao.
    db_sil, db_index = internal_metrics(X, labels_dbscan, ignore_noise=True)
    noise = int(np.sum(labels_dbscan == -1))
    gram_kmeans_ari = float(adjusted_rand_score(gram, labels_kmeans))
    gram_dbscan_ari = float(adjusted_rand_score(gram, labels_dbscan))
    best_sil = float(k_table.loc[k_table["k"] == best_k, "silhueta"].iloc[0])
    best_db = float(
        k_table.loc[k_table["k"] == best_k, "davies_bouldin"].iloc[0]
    )
    cluster_sizes = pd.Series(labels_kmeans).value_counts().sort_index()
    db_sizes = pd.Series(labels_dbscan).value_counts().sort_index()
    profile_lines = []
    for cluster in sorted(set(labels_kmeans)):
        row = profiles.loc[
            (profiles["algoritmo"] == "K-Means")
            & (profiles["cluster"] == cluster)
        ].iloc[0]
        top = sorted(activities, key=lambda col: row[col], reverse=True)[:5]
        profile_lines.append(
            "- K-Means {} (n={}): {}.".format(
                cluster,
                int(cluster_sizes.loc[cluster]),
                ", ".join("{}={:.2f}".format(col, row[col]) for col in top),
            )
        )
    morphology_notes = []
    for cluster in sorted(set(labels_kmeans)):
        top_features = morphology_profiles.loc[
            (morphology_profiles["algoritmo"] == "K-Means")
            & (morphology_profiles["cluster"] == cluster)
        ]
        top_notes = []
        for column in morphology:
            part = top_features.loc[top_features["caracteristica"] == column]
            if not part.empty:
                best = part.sort_values("proporcao", ascending=False).iloc[0]
                top_notes.append(
                    "{}={} ({:.0%})".format(
                        column, best["categoria"], best["proporcao"]
                    )
                )
        morphology_notes.append(
            "- K-Means {}: {}.".format(cluster, "; ".join(top_notes))
        )
    stability_text = "\n".join(
        "- {}: ARI medio {:.3f} (DP {:.3f}).".format(
            name, row["mean"], row["std"]
        )
        for name, row in stability_summary.iterrows()
    )
    db_counts = ", ".join(
        "{}: {}".format(int(group), int(count))
        for group, count in db_sizes.items()
    )
    tsne_base_trust = float(
        projections.loc[
            (projections["metodo"] == "t-SNE")
            & (projections["perplexity"] == TSNE_PERPLEXITY)
            & (projections["semente"] == SEED),
            "trustworthiness_k10",
        ].iloc[0]
    )
    report = [
        "# Relatorio final - Trabalho II: Aprendizado Nao Supervisionado",
        "",
        "> Preencher nomes e matriculas dos integrantes antes da entrega.",
        "",
        "## 1. Objetivo e dados",
        "",
        "Foram analisados {} isolados e 23 atividades funcionais. O ID foi "
        "usado apenas para rastreabilidade. A analise principal de grupos foi "
        "feita nas atividades transformadas; morfologia foi usada para "
        "descrever os grupos e GRAM foi reservado como referencia externa. "
        "O arquivo original tem {} linhas e {} IDs duplicados segundo a "
        "coluna de identificacao. A tabela `exploracao_dados.tsv` documenta "
        "tipos, ausencias e cardinalidade por coluna."
        .format(len(X), len(original_data), id_duplicates),
        "",
        "## 2. Pre-processamento e decisoes",
        "",
        "- ID nao entrou como atributo, para evitar que um codigo arbitrario "
        "influenciasse distancias.",
        "- As 23 atividades foram representadas em escalas de 0 a 1. Variaveis "
        "ordinais 0-3 foram divididas por 3; binarias/categoricas foram "
        "codificadas 0/1; atividades continuas foram normalizadas. As quatro "
        "atividades de cauda longa (02, 14, 15, 23) receberam log1p antes da "
        "normalizacao. Ausentes foram imputados conforme o tipo e a indicacao "
        "de ausencia nao entrou no agrupamento.",
        "- A morfologia foi resumida pelas categorias mais frequentes por "
        "grupo, sem interpretar codigos nominais como quantidades.",
        "- As distancias dos metodos usam os valores transformados. Assim, "
        "escalas e imputacoes fazem parte da definicao de semelhanca.",
        "",
        "## 3. Tarefa A - Agrupamento",
        "",
        "### Metodos e parametros",
        "",
        "- **K-Means:** minimiza a soma das distancias euclidianas quadradas "
        "aos centroides. Requer k; tende a grupos compactos, aproximadamente "
        "esfericos e de tamanhos semelhantes, e nao separa ruido. Foram "
        "testados k=2..10, semente {}, n_init=20; o k final foi escolhido pela "
        "maior silhueta, conferindo tambem o cotovelo da inercia."
        .format(SEED),
        "- **DBSCAN:** agrupa regioes densas e marca pontos sem vizinhos "
        "suficientes como ruido. Usa distancia euclidiana, min_samples={} e "
        "eps={:.2f}. eps foi escolhido aproximadamente pelo cotovelo no "
        "grafico de k-distancias (k=min_samples); a tabela de sensibilidade "
        "mostra que essa escolha nao e unica."
        .format(MIN_SAMPLES, EPS),
        "",
        "### Resultados e avaliacao",
        "",
        "- K-Means selecionou k={} (silhueta={:.3f}; Davies-Bouldin={:.3f}). "
        "Silhueta maior e melhor; Davies-Bouldin menor e melhor. A silhueta "
        "baixa aponta separacao fraca, nao evidencia grupos naturais bem "
        "delimitados."
        .format(best_k, best_sil, best_db),
    ]
    report.extend(profile_lines)
    report.extend(
        [
            "",
            "Caracteristicas morfologicas mais frequentes nos grupos K-Means "
            "(categorias sao codigos nominais):",
        ]
    )
    report.extend(morphology_notes)
    report.extend(
        [
            "",
            "- DBSCAN produziu {} grupos e {} isolados de ruido ({:.1f}%). "
            "Contagens por rotulo (inclui -1 = ruido): {}. Nos pontos nao "
            "ruido, silhueta={:.3f} e Davies-Bouldin={:.3f}; essas metricas "
            "nao incluem ruido e nao sao diretamente comparaveis com a "
            "particao completa do K-Means."
            .format(
                len(set(labels_dbscan) - {-1}),
                noise,
                100.0 * noise / len(X),
                db_counts,
                db_sil,
                db_index,
            ),
            "- A concordancia entre K-Means e DBSCAN foi ARI={:.3f}. ARI=1 "
            "seria particao identica; perto de 0 indica pouca concordancia. "
            "As premissas diferentes (centroides versus densidade/ruido) "
            "explicam parte da discordancia."
            .format(partition_ari),
            "- Referencia externa GRAM: ARI K-Means={:.3f}, DBSCAN={:.3f}; "
            "NMI K-Means={:.3f}, DBSCAN={:.3f}. GRAM nao e uma verdade "
            "biologica dos grupos, apenas uma referencia de concordancia."
            .format(
                gram_kmeans_ari,
                gram_dbscan_ari,
                normalized_mutual_info_score(gram, labels_kmeans),
                normalized_mutual_info_score(gram, labels_dbscan),
            ),
            "- Com e sem GRAM: ver `comparacao_com_sem_gram.tsv`. A coluna "
            "foi adicionada como one-hot, mantendo os mesmos k/eps; essa "
            "comparacao mede o efeito de incluir essa informacao, nao uma "
            "melhora causal.",
            "- Estabilidade por cinco subamostras de 80% (ARI contra a "
            "particao completa):",
            stability_text,
            "",
            "### Conclusao da Tarefa A",
            "",
            "Ha semelhancas nos perfis funcionais, mas as metricas e a "
            "quantidade de ruido mostram que os grupos nao estao fortemente "
            "separados. K-Means oferece uma divisao completa e resumida; "
            "DBSCAN identifica zonas densas e muitos isolados sem densidade "
            "local. Os isolados de ruido sao candidatos a revisao, nao "
            "anomalias biologicas confirmadas.",
            "",
            "## 4. Tarefa B - Reducao de dimensionalidade",
            "",
            "- **PCA (linear):** projeta combinacoes lineares que maximizam "
            "variancia explicada; eixos sao interpretaveis por seus pesos, "
            "mas a tecnica nao captura estrutura nao linear. As duas primeiras "
            "componentes explicam {:.1%} e {:.1%} da variancia "
            "(acumulada {:.1%}); trustworthiness@10={:.3f}."
            .format(
                pca.explained_variance_ratio_[0],
                pca.explained_variance_ratio_[1],
                sum(pca.explained_variance_ratio_[:2]),
                pca_trust,
            ),
            "- **t-SNE (nao linear):** prioriza preservar vizinhancas locais "
            "em 2D. Foi usada perplexity={}, semente={}, init=PCA e 1000 "
            "iteracoes; trustworthiness@10={:.3f}. Eixos, distancias entre "
            "nuvens e tamanhos aparentes nao tem interpretacao direta."
            .format(TSNE_PERPLEXITY, SEED, tsne_base_trust),
            "- Variancia explicada e erro de reconstrucao PCA por dimensao "
            "estao em `pca_variancia_reconstrucao.tsv`. Trustworthiness e "
            "estabilidade do t-SNE com perplexities 10/30/50 e sementes "
            "diferentes estao em `metricas_reducao_dimensionalidade.tsv`. "
            "A sobreposicao mede Jaccard medio dos 10 vizinhos no espaco "
            "projetado relativamente ao t-SNE base (perplexity 30, semente 42).",
            "- As quatro projecoes em `03_projecoes_pca_tsne.png` usam as "
            "mesmas atividades e sao coloridas pelas particoes principais "
            "K-Means e DBSCAN. Elas servem para visualizar, nao para provar "
            "separacao biologica.",
            "",
            "## 5. Sensibilidade ao pre-processamento",
            "",
            "Foi alterada uma decisao: remover log1p das atividades 02, 14, "
            "15 e 23, mantendo normalizacao min-max, k e semente. A silhueta "
            "K-Means mudou de {:.3f} para {:.3f}, Davies-Bouldin de {:.3f} "
            "para {:.3f}, e ARI entre particoes foi {:.3f}. Isso mostra "
            "quanto a representacao da cauda longa influencia os grupos; a "
            "comparacao completa esta em `sensibilidade_preprocessamento.tsv`."
            .format(
                baseline_silhouette,
                no_log_silhouette,
                baseline_db,
                no_log_db,
                adjusted_rand_score(labels_kmeans, no_log_labels),
            ),
            "",
            "## 6. Limitacoes",
            "",
            "- Os nomes dos ensaios estao anonimizados; medias altas nao podem "
            "ser traduzidas em mecanismos ou aplicacoes especificas.",
            "- Codigos morfologicos representam categorias, nao magnitudes; "
            "multiplos codigos em uma celula podem afetar a representacao.",
            "- K-Means depende de k e e sensivel a valores extremos; DBSCAN "
            "depende de eps/min_samples e sofre em dimensoes altas/densidades "
            "diferentes.",
            "- PCA e linear; t-SNE e sensivel a hiperparametros e preserva "
            "principalmente vizinhancas locais. As figuras nao sao prova de "
            "grupos biologicos.",
            "- A estabilidade foi avaliada em cinco subamostras de 80%, uma "
            "checagem limitada. A colecao de 506 isolados pode nao representar "
            "toda a biodiversidade marinha.",
            "- Nenhum cluster prova especie, potencial farmacologico ou "
            "propriedade biologica; isso requer validacao laboratorial.",
            "",
            "## 7. Arquivos e figuras",
            "",
            "Figuras: `01_selecao_k.png`, `02_dbscan_parametros.png`, "
            "`03_projecoes_pca_tsne.png`, `04_pca_variancia_erro.png`, "
            "`05_contingencia_gram.png`, `06_perfis_atividades.png`.",
            "Tabelas: metricas, perfis funcionais/morfologicos, estabilidade, "
            "sensibilidade, contingencias e resultados por ID foram salvos "
            "em TSV nesta pasta.",
            "",
            "## Referencias",
            "",
            "- MacQueen, J. (1967). Some methods for classification and analysis "
            "of multivariate observations. *Proceedings of the Fifth Berkeley "
            "Symposium on Mathematical Statistics and Probability*.",
            "- Ester, M. et al. (1996). A density-based algorithm for discovering "
            "clusters in large spatial databases with noise. *KDD*.",
            "- Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the "
            "interpretation and validation of cluster analysis. *Journal of "
            "Computational and Applied Mathematics*, 20, 53-65.",
            "- Davies, D. L., & Bouldin, D. W. (1979). A cluster separation "
            "measure. *IEEE Transactions on Pattern Analysis and Machine "
            "Intelligence*, PAMI-1(2), 224-227.",
            "- Hubert, L., & Arabie, P. (1985). Comparing partitions. *Journal "
            "of Classification*, 2, 193-218.",
            "- Jolliffe, I. T., & Cadima, J. (2016). Principal component "
            "analysis: a review and recent developments. *Philosophical "
            "Transactions of the Royal Society A*, 374.",
            "- van der Maaten, L., & Hinton, G. (2008). Visualizing data using "
            "t-SNE. *Journal of Machine Learning Research*, 9, 2579-2605.",
            "",
        ]
    )
    with open(
        os.path.join(root, "relatorio_final.md"), "w", encoding="utf-8"
    ) as report_file:
        report_file.write("\n".join(report))

    make_plots(
        root,
        k_table,
        distances,
        eps_table,
        pca,
        pca_2d,
        tsne_2d,
        labels_kmeans,
        labels_dbscan,
        pca_mse,
        gram_counts,
        profiles,
    )
    print("Analise concluida para {} isolados.".format(len(X)))
    print("K-Means: k={}, silhueta={:.3f}; DBSCAN: {} grupos, {} ruido.".format(
        best_k, best_sil, len(set(labels_dbscan) - {-1}), noise
    ))
    print("ARI K-Means vs DBSCAN: {:.3f}".format(partition_ari))
    print("Relatorio: relatorio_final.md")
    print("Preencha nomes e matriculas dos integrantes antes de entregar.")


if __name__ == "__main__":
    main()
