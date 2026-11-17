import pandas as pd

df = pd.read_csv("Dados_REG.csv", sep="\t")

#df_tratado.to_csv("Dados_REG_tratado.csv", sep="\t", index=False)


# pd.set_option('display.max_columns', None)

# (Opcional) Se quiser também remover o limite de largura do texto em cada coluna:
# pd.set_option('display.max_colwidth', None)

# print("Quantidade de linhas e colunas:")
# print(df.shape)


########       EXPLORAÇÃO DO DATASET       ########

# # # # Nomes das colunas
# print(df.columns.tolist())


# # # # Informações gerais do DataFrame
# print(df.info())




# # #print("Estatísticas descritivas do DataFrame:")
# print(df.describe())

# print(df.isnull().sum())

# # #print("Linhas com valores ausentes:")
# print(df[df.isna().any(axis=1)])



# # print(df)


# print("Limpeza da coluna 'n°':")
# print(df[df['n°'].duplicated(keep=False)])
# print(df['n°'].duplicated().sum())

print("Limpeza da coluna GRAM:")
permitidos = {"Positivo", "Negativo", "Levedura"}
gram = df["GRAM"].astype("string").str.strip()
fora_permitidos = gram.notna() & ~gram.isin(permitidos)

print("Valores em GRAM fora dos permitidos:", gram[fora_permitidos].unique())
print(df.loc[fora_permitidos, ["n°", "GRAM"]].to_string(index=False))


# #limpeza Cor
# tem_invalido = (~df['Cor'].isin([1, 2])).any()
# print("\nLinhas com Cor fora de [1, 2] ({}):".format(tem_invalido))
# print(tem_invalido)



# # ###Limpeza cores 
# # Aceita apenas dígitos de 1 a 7 isolados ou separados por &
# print("\nLimpeza da coluna 'Cores':")
# cores_limpas = df['Cores'].astype(str).str.replace(r'\.0$', '', regex=True)
# # Aceita espaços nas pontas e ao redor do '&' (ex: '1 & 6', ' 2 ', '1&7')
# padrao_com_espaco = cores_limpas.str.match(r'^\s*[1-7](\s*&\s*[1-7])*\s*$')
# linhas_fora_intervalo = df[~padrao_com_espaco]
# print(linhas_fora_intervalo)

# ##LImpeza da coluna "Borda"

# linhas_invalidas_borda = df.loc[
#     df["Borda"].isna() | ~df["Borda"].isin([0, 1, 2]), ["n°", "Borda"]
# ]
# print("\nLinhas com Borda ausente ou fora de [0, 1, 2] ({}):".format(len(linhas_invalidas_borda)))
# print(linhas_invalidas_borda.to_string(index=False))


# ##textura

# textura_limpas = df["Textura"].astype("string").str.replace(r"\.0$", "", regex=True)
# # Aceita espaços nas pontas e ao redor do '&' (ex: '1 & 6', ' 2 ', '1&7')
# padrao_com_espaco = textura_limpas.str.match(
# 	r"^\s*[1-2](\s*&\s*[1-2])*\s*$", na=False
# )
# linhas_fora_intervalo = df.loc[df["Textura"].notna() & ~padrao_com_espaco]
# print("\nLinhas com Textura fora de [1, 2] ({}):".format(len(linhas_fora_intervalo)))
# print(linhas_fora_intervalo)



# ##limpeza Forma
# forma_limpas = df["Forma"].astype("string").str.replace(r"\.0$", "", regex=True)
# # Aceita 1, 2, 4 ou 6, isolados ou separados por '&'.
# padrao_com_espaco = forma_limpas.str.match(
# 	r"^\s*[1246](\s*&\s*[1246])*\s*$", na=False
# )
# linhas_fora_intervalo = df.loc[df["Forma"].notna() & ~padrao_com_espaco]
# print("\nLinhas com Forma fora de [1, 2] ({}):".format(len(linhas_fora_intervalo)))
# print(linhas_fora_intervalo)


# ##limpeza brilho 
# brilho_limpas = df["Brilho"].astype("string").str.replace(r"\.0$", "", regex=True)
# # Aceita 1, 2, 4 ou 6, isolados ou separados por '&'.
# padrao_com_espaco = brilho_limpas.str.match(
# 	r"^\s*[0124](\s*&\s*[0124])*\s*$", na=False
# )
# linhas_fora_intervalo = df.loc[df["Brilho"].notna() & ~padrao_com_espaco]
# print("\nLinhas com Brilho fora de [0, 1] ({}):".format(len(linhas_fora_intervalo)))
# print(linhas_fora_intervalo)


# ###limpeza Muco
# df["Muco"] = pd.to_numeric(df["Muco"]).astype("Int64")
# muco_invalido = df["Muco"].notna() & ~df["Muco"].isin([0, 1])
# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", "Muco"]]
# print("\nLinhas com Muco fora de [0, 1] ({}):".format(len(linhas_invalidas_muco)))
# print(linhas_invalidas_muco.to_string(index=False))


# ###limpeza de Relevo
# linhas_invalidas_relevo = df.loc[~df["Relevo"].isin([0, 1]), ["n°", "Relevo"]]
# print("\nLinhas com Relevo fora de [0, 1] ({}):".format(len(linhas_invalidas_relevo)))
# print(linhas_invalidas_relevo.to_string(index=False))
# df["Relevo"] = pd.to_numeric(df["Relevo"], errors="coerce").astype("Int64")


# ##Atividade 2
# atividade02_original = df["Atividade 02"].copy()
# atividade02_numerica = pd.to_numeric(atividade02_original, errors="coerce")
# atividade02_invalida = atividade02_original.notna() & (
#     atividade02_numerica.isna()
#     | (atividade02_numerica < 0)
#     | (atividade02_numerica > 6)
# )
# linhas_invalidas_atividade02 = df.loc[
#     atividade02_invalida, ["n°", "Atividade 02"]
# ]
# print("\nLinhas com Atividade 02 fora do intervalo [0, 6] ou não numéricas ({}):".format(
#     len(linhas_invalidas_atividade02)
# ))
# print(linhas_invalidas_atividade02.to_string(index=False))
# df["Atividade 02"] = atividade02_numerica.astype("Float64")


# ##Atividade 5
# coluna = "Atividade 05"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 3)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 4] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))
# # ##validaçao de 0 para ->0.0(6,7,8,11,12,)



# # # Atividade 9
# # muco_invalido = df["Atividade 09"].notna() & (
# #     (df["Atividade 09"] < 0) | (df["Atividade 09"] > 2)
# # )df["Atividade 09"] = pd.to_numeric(df["Atividade 09"], errors="coerce").astype("Float64")
# # linhas_invalidas_muco = df.loc[muco_invalido, ["n°", "Atividade 09"]]
# # print("\nLinhas com Atividade 09 fora de [0, 2] ({}):".format(len(linhas_invalidas_muco)))
# # print(linhas_invalidas_muco.to_string(index=False))

# coluna = "Atividade 09"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 2)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 4] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))
# # ##validaçao de 0 para ->0.0(6,7,8,11,12,)






# ##Atividade 10
# # df["Atividade 10"] = pd.to_numeric(df["Atividade 10"], errors="coerce").astype("Float64")
# # muco_invalido = df["Atividade 10"].notna() & ~df["Atividade 10"].isin([0,1])
# # linhas_invalidas_muco = df.loc[muco_invalido, ["n°", "Atividade 10"]]
# # print("\nLinhas com Atividade 10  fora de [0, 2] ({}):".format(len(linhas_invalidas_muco)))
# # print(linhas_invalidas_muco.to_string(index=False)) 


# coluna = "Atividade 10"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 1)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 1] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))

# # ##validaçao de 0 para ->0.0(6,7,8,11,12,)





# ###atividade 14
# coluna = "Atividade 14"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 13)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 13] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))


# ##Atividade 15
# coluna = "Atividade 15"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 10)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 10] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))



# ##Atividade 23
# atividade23_numerica = pd.to_numeric(df["Atividade 23"], errors="coerce")
# atividade23_invalida = df["Atividade 23"].notna() & atividade23_numerica.isna()
# linhas_invalidas_atividade23 = df.loc[
# 	atividade23_invalida, ["n°", "Atividade 23"]
# ]
# print("\nLinhas com Atividade 23 não numérica :".format(len(linhas_invalidas_atividade23)))
# print(linhas_invalidas_atividade23.to_string(index=False))



# #Atividade 15
# coluna = "Atividade 23"
# df[coluna] = pd.to_numeric(df[coluna], errors="coerce").astype("Float64")

# muco_invalido = df[coluna].notna() & (
#     (df[coluna] < 0) | (df[coluna] > 400)
# )

# linhas_invalidas_muco = df.loc[muco_invalido, ["n°", coluna]]
# print(f"\nLinhas com {coluna} fora do intervalo [0, 400] ({len(linhas_invalidas_muco)}):")
# print(linhas_invalidas_muco.to_string(index=False))

# # # Histograma da coluna Atividade 23
# import matplotlib.pyplot as plt

# # serie_atividade23 = atividade23_numerica.dropna()
# # plt.figure(figsize=(10, 6))
# # plt.hist(serie_atividade23, bins=20, color="steelblue", edgecolor="black")
# # plt.title("Histograma da coluna Atividade 23")
# # plt.xlabel("Atividade 23")
# # plt.ylabel("Frequência")
# # plt.grid(axis="y", linestyle="--", alpha=0.6)
# # plt.tight_layout()
# # plt.savefig("histograma_atividade_23.png", dpi=200, bbox_inches="tight")
# # print("\nHistograma salvo em: histograma_atividade_23.png")



# serie_atividade14 = atividade23_numerica.dropna()
# plt.figure(figsize=(10, 6))
# plt.hist(serie_atividade14, bins=20, color="steelblue", edgecolor="black")
# plt.title("Histograma da coluna Atividade 14")
# plt.xlabel("Atividade 14")
# plt.ylabel("Frequência")
# plt.grid(axis="y", linestyle="--", alpha=0.6)
# plt.tight_layout()
# plt.savefig("histograma_atividade_14.png", dpi=200, bbox_inches="tight")
# print("\nHistograma salvo em: histograma_atividade_14.png")



# serie_atividade15 = atividade23_numerica.dropna()
# plt.figure(figsize=(10, 6))
# plt.hist(serie_atividade15, bins=20, color="steelblue", edgecolor="black")
# plt.title("Histograma da coluna Atividade 15")
# plt.xlabel("Atividade 15")
# plt.ylabel("Frequência")
# plt.grid(axis="y", linestyle="--", alpha=0.6)
# plt.tight_layout()
# plt.savefig("histograma_atividade_15.png", dpi=200, bbox_inches="tight")
# print("\nHistograma salvo em: histograma_atividade_15.png")

# print(df.info())




####LIMPEZA FINAL DO DATASET



















