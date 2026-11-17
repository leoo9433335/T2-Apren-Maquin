import pandas as pd

df = pd.read_csv("Dados_REG.csv", sep="\t")

coluna_id = df.columns[0]
ids_repetidos = df[coluna_id].duplicated(keep="first")
id_repetido = df.loc[ids_repetidos, coluna_id]

if not id_repetido.empty:
    proximo_id = int(pd.to_numeric(df[coluna_id], errors="raise").max()) + 1
    for indice in df.index[ids_repetidos]:
        print(
            "ID duplicado {} na linha {} substituído por {}".format(
                df.at[indice, coluna_id], indice + 2, proximo_id
            )
        )
        df.at[indice, coluna_id] = proximo_id
        proximo_id += 1

coluna_muco = "Muco"
muco_numerico = pd.to_numeric(df[coluna_muco], errors="coerce")
moda_muco = muco_numerico.mode()
if moda_muco.empty:
    raise ValueError("Não foi possível calcular a moda da coluna Muco.")

muco_igual_a_dois = muco_numerico.eq(2)
df.loc[muco_igual_a_dois, coluna_muco] = moda_muco.iloc[0]
print(
    "Valores 2 em Muco substituídos pela moda: {}".format(moda_muco.iloc[0])
)

coluna_gram = "GRAM"
gram = df[coluna_gram].astype("string").str.strip()
gram_corrigido = {
    "POSITIVO": "Positivo",
    "Positiva": "Positivo",
    "Variável": "Positivo",
    "Levedura? não": "Levedura",
}
df[coluna_gram] = gram.replace(gram_corrigido)
print("Valores da coluna GRAM padronizados.")

coluna_atividade23 = "Atividade 23"
linha_id_1718 = df[coluna_id].eq(1718)
if linha_id_1718.sum() != 1:
    raise ValueError(
        "Esperada exatamente uma linha com ID 1718; encontradas: {}".format(
            int(linha_id_1718.sum())
        )
    )
df.loc[linha_id_1718, coluna_atividade23] = ""
print("Atividade 23 deixada vazia para o ID 1718.")



colunas_combinadas = [
    coluna
    for coluna in df.columns
    if df[coluna]
    .astype("string")
    .str.contains("&", regex=False, na=False)
    .any()
]

for coluna in colunas_combinadas:
    partes = df[coluna].astype("string").str.split("&", expand=True)

    for posicao in range(partes.shape[1]):
        nome_novo = "{}_parte_{}".format(coluna, posicao + 1)
        if nome_novo in df.columns:
            raise ValueError(
                "A coluna derivada {} já existe; verifique antes de sobrescrevê-la.".format(
                    nome_novo
                )
            )

        valores = partes[posicao].str.strip().astype(object)
        valores = valores.where(pd.notna(valores), float("nan"))
        valores = valores.replace("", float("nan"))
        df[nome_novo] = pd.to_numeric(valores, errors="raise").astype("Int64")

print("Colunas separadas:", colunas_combinadas)

arquivo_saida = "Dados_REG_transformado.tsv"
df.to_csv(arquivo_saida, sep="\t", index=False)
print("Dataset transformado salvo em: {}".format(arquivo_saida))