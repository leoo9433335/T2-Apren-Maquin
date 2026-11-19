import os

import numpy as np
import pandas as pd


arquivo_entrada = "Dados_REG_transformado.tsv"
arquivo_saida = "Dados_REG_kmeans_onehot.tsv"
arquivo_atividades_saida = "Dados_REG_atividades_transformadas.tsv"
arquivo_relatorio_saida = "relatorio_transformacoes_atividades.tsv"

atividades_categoricas = (
    "Atividade 03",
    "Atividade 04",
    "Atividade 16",
)
atividades_ordinais = tuple(
    "Atividade {:02d}".format(numero)
    for numero in (13, 17, 18, 19, 20, 21, 22)
)
atividades_log = (
    "Atividade 02",
    "Atividade 14",
    "Atividade 15",
    "Atividade 23",
)
atividades_binarias = ("Atividade 01",)
atividades = tuple(
    "Atividade {:02d}".format(numero) for numero in range(1, 24)
)


def transformar_atividades(df):
    resultado = df[[df.columns[0]] + list(atividades)].copy()
    relatorio = []

    for coluna in atividades:
        original = resultado[coluna].copy()
        ausente = original.isna()
        transformacoes = []

        if coluna in atividades_categoricas:
            valores = original.astype("string").str.strip().str.lower()
            mapa = {"negativo": 0.0, "positivo": 1.0}
            desconhecidos = sorted(set(valores.dropna()) - set(mapa))
            if desconhecidos:
                raise ValueError(
                    "Categorias inesperadas em {}: {}".format(
                        coluna, ", ".join(desconhecidos)
                    )
                )
            transformada = valores.map(mapa).astype(float)
            transformacoes.append("Negativo=0; Positivo=1")
        else:
            valores = pd.to_numeric(original, errors="raise").astype(float)
            observados = valores.dropna()
            if observados.empty:
                raise ValueError(
                    "A coluna {} está totalmente ausente.".format(coluna)
                )

            if coluna in atividades_ordinais:
                niveis_invalidos = sorted(set(observados) - {0, 1, 2, 3})
                if niveis_invalidos:
                    raise ValueError(
                        "Níveis inesperados em {}: {}".format(
                            coluna, niveis_invalidos
                        )
                    )
                transformada = valores / 3.0
                transformacoes.append("ordinal 0–3 dividido por 3")
            elif coluna in atividades_binarias:
                valores_invalidos = sorted(set(observados) - {0, 1})
                if valores_invalidos:
                    raise ValueError(
                        "Valores binários inesperados em {}: {}".format(
                            coluna, valores_invalidos
                        )
                    )
                transformada = valores.copy()
                transformacoes.append("binária mantida em 0/1")
            else:
                if coluna in atividades_log:
                    if observados.lt(0).any():
                        raise ValueError(
                            "log1p não pode ser aplicado a negativos em {}."
                            .format(coluna)
                        )
                    valores = np.log1p(valores)
                    transformacoes.append("log1p")

                observados = valores.dropna()
                minimo = float(observados.min())
                maximo = float(observados.max())
                if minimo == maximo:
                    transformada = valores.where(valores.isna(), 0.0)
                    transformacoes.append("constante mapeada para 0")
                else:
                    transformada = (valores - minimo) / (maximo - minimo)
                    transformacoes.append("MinMax para [0, 1]")

        if ausente.any():
            if (
                coluna in atividades_categoricas
                or coluna in atividades_ordinais
            ):
                moda = transformada.dropna().mode()
                if moda.empty:
                    raise ValueError(
                        "Não foi possível calcular a moda de {}.".format(
                            coluna
                        )
                    )
                valor_imputacao = float(moda.iloc[0])
                criterio_imputacao = "moda"
            else:
                valor_imputacao = float(transformada.median())
                criterio_imputacao = "mediana"
            transformada = transformada.fillna(valor_imputacao)
            resultado[coluna + "_ausente"] = ausente.astype(int)
            transformacoes.append(
                "ausentes imputados pela {}".format(criterio_imputacao)
            )

        if transformada.isna().any() or not np.isfinite(
            transformada.to_numpy(dtype=float)
        ).all():
            raise ValueError(
                "A transformação de {} gerou valores inválidos.".format(
                    coluna
                )
            )

        resultado[coluna] = transformada.astype(float)
        relatorio.append(
            {
                "atividade": coluna,
                "tipo": (
                    "categórica binária"
                    if coluna in atividades_categoricas
                    else "ordinal"
                    if coluna in atividades_ordinais
                    else "binária"
                    if coluna in atividades_binarias
                    else "numérica contínua"
                ),
                "ausentes_originais": int(ausente.sum()),
                "negativos_originais": (
                    int(pd.to_numeric(original, errors="coerce").lt(0).sum())
                    if coluna not in atividades_categoricas
                    else 0
                ),
                "minimo_original": (
                    float(pd.to_numeric(original, errors="coerce").min())
                    if coluna not in atividades_categoricas
                    else np.nan
                ),
                "maximo_original": (
                    float(pd.to_numeric(original, errors="coerce").max())
                    if coluna not in atividades_categoricas
                    else np.nan
                ),
                "transformacao": "; ".join(transformacoes),
                "minimo_final": float(resultado[coluna].min()),
                "maximo_final": float(resultado[coluna].max()),
            }
        )

    return resultado, pd.DataFrame(relatorio)


df = pd.read_csv(
    arquivo_entrada,
    sep="\t",
    encoding="utf-8-sig",
    na_values=["#NÚM!", "#N�M!"],
    keep_default_na=True,
)
coluna_id = df.columns[0]

colunas_features = [
    "GRAM",
    "Cor",
    "Borda",
    "Muco",
    "Relevo",
    "Cores_parte_1",
    "Cores_parte_2",
    "Textura_parte_1",
    "Textura_parte_2",
    "Forma_parte_1",
    "Forma_parte_2",
    "Brilho_parte_1",
    "Brilho_parte_2",
]

colunas_ausentes = [
    coluna for coluna in colunas_features if coluna not in df.columns
]
if colunas_ausentes:
    raise ValueError(
        "Colunas necessárias não encontradas em {}: {}".format(
            arquivo_entrada, ", ".join(colunas_ausentes)
        )
    )

features = df[colunas_features].copy()
for coluna in colunas_features:
    valores = features[coluna].astype(object)
    valores = valores.where(pd.notna(valores), "Sem")
    valores = valores.astype(str).str.strip().replace("", "Sem")
    features[coluna] = valores

matriz_kmeans = pd.get_dummies(
    features,
    columns=colunas_features,
    prefix=colunas_features,
    prefix_sep="=",
    dtype=int,
)

if matriz_kmeans.isnull().any().any():
    raise ValueError("A matriz codificada ainda contém valores ausentes.")

colunas_atividade_ausentes = [
    coluna for coluna in atividades if coluna not in df.columns
]
if colunas_atividade_ausentes:
    raise ValueError(
        "Colunas de atividade não encontradas em {}: {}".format(
            arquivo_entrada, ", ".join(colunas_atividade_ausentes)
        )
    )

atividades_transformadas, relatorio = transformar_atividades(df)

resultado = matriz_kmeans.copy()
resultado.insert(0, coluna_id, df[coluna_id])
pasta_saida = os.path.dirname(os.path.abspath(__file__))
resultado.to_csv(
    os.path.join(pasta_saida, arquivo_saida),
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)
atividades_transformadas.to_csv(
    os.path.join(pasta_saida, arquivo_atividades_saida),
    sep="\t",
    index=False,
    encoding="utf-8-sig",
    na_rep="",
)
relatorio.to_csv(
    os.path.join(pasta_saida, arquivo_relatorio_saida),
    sep="\t",
    index=False,
    encoding="utf-8-sig",
)

print("Atributos usados:", ", ".join(colunas_features))
print("Matriz one-hot:", matriz_kmeans.shape)
print("ID mantido apenas para rastreabilidade:", coluna_id)
print("Arquivo morfológico salvo em:", arquivo_saida)
print("Atividades transformadas salvas em:", arquivo_atividades_saida)
print("Relatório das transformações salvo em:", arquivo_relatorio_saida)
