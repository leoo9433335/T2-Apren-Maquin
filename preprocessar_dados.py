import argparse
from pathlib import Path

import numpy as np
import pandas as pd


MULTIVALUED_COLUMNS = ("Cores", "Textura", "Forma", "Brilho")
BINARY_TEXT_ACTIVITIES = {"Atividade 03", "Atividade 04", "Atividade 16"}
BINARY_ACTIVITY_COLUMNS = {
    "Atividade 01",
    "Atividade 03",
    "Atividade 04",
    "Atividade 16",
}
ORDINAL_ACTIVITY_COLUMNS = {
    "Atividade 13",
    "Atividade 17",
    "Atividade 18",
    "Atividade 19",
    "Atividade 20",
    "Atividade 21",
    "Atividade 22",
}
LOG_ACTIVITY_COLUMNS = {
    "Atividade 02",
    "Atividade 14",
    "Atividade 15",
    "Atividade 23",
}
ACTIVITY_COLUMNS = [f"Atividade {number:02d}" for number in range(1, 24)]


def normalize_text(df):
    for column in df.select_dtypes(include="object").columns:
        values = df[column].astype("string").str.strip().str.lower()
        df[column] = values.mask(values.eq(""), pd.NA)

    return df


def encode_multivalued_column(df, column):
    raw = df[column].astype("string").str.strip()
    parts = raw.str.split("&", n=2, regex=False)

    if parts.dropna().map(len).gt(2).any():
        raise ValueError(f"Mais de dois códigos encontrados em {column}.")

    first = parts.str[0].str.strip()
    second = parts.str[1].str.strip()
    first = first.mask(first.eq(""), pd.NA)
    second = second.mask(second.eq(""), pd.NA)

    if (raw.notna() & first.isna()).any():
        raise ValueError(f"Código vazio na primeira posição de {column}.")
    if (raw.str.contains("&", regex=False, na=False) & second.isna()).any():
        raise ValueError(f"Segundo código vazio após '&' em {column}.")

    generated = []
    for position, values in ((1, first), (2, second)):
        codes = values.dropna().unique().tolist()
        if any(not str(code).isdigit() for code in codes):
            raise ValueError(f"Código não inteiro encontrado em {column}: {codes}")

        for code in sorted(codes, key=int):
            name = f"{column}_{position}_{code}"
            if name in df.columns:
                raise ValueError(f"A coluna de saída já existe: {name}")

            indicator = values.eq(code).fillna(False).astype("Int64")
            df[name] = indicator.mask(raw.isna(), pd.NA)
            generated.append(name)

        if generated:
            indicator_columns = [name for name in generated if name.startswith(f"{column}_{position}_")]
            sums = df[indicator_columns].sum(axis=1) if indicator_columns else pd.Series(0, index=df.index)
            observed = raw.notna()

            if position == 1:
                expected = pd.Series(1, index=df.index[observed])
            else:
                expected = second.notna().astype("int64").loc[observed]

            if not (
                sums.loc[observed].to_numpy(dtype="int64")
                == expected.to_numpy(dtype="int64")
            ).all():
                raise AssertionError(f"Falha na validação one-hot de {column}, posição {position}.")
            if not df.loc[~observed, indicator_columns].isna().all().all():
                raise AssertionError(f"Ausentes não foram preservados em {column}, posição {position}.")

    return generated


def transform_activities(df):
    normalized = []
    for column in ACTIVITY_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")

    for column in BINARY_ACTIVITY_COLUMNS:
        if not df[column].dropna().isin([0, 1]).all():
            raise ValueError(f"Resultado binário inesperado em {column}.")
        if column in BINARY_TEXT_ACTIVITIES:
            df[column] = df[column].astype("Int64")

    for column in LOG_ACTIVITY_COLUMNS:
        values = df[column].dropna()
        if values.lt(0).any():
            raise ValueError(f"log1p não pode ser aplicado a valores negativos em {column}.")
        df[column] = np.log1p(df[column])

    for column in ORDINAL_ACTIVITY_COLUMNS:
        values = df[column].dropna()
        if not values.isin([0, 1, 2, 3]).all():
            raise ValueError(f"Nível ordinal fora de 0–3 em {column}.")
        df[column] = df[column] / 3

    for column in ACTIVITY_COLUMNS:
        if column in BINARY_ACTIVITY_COLUMNS or column in ORDINAL_ACTIVITY_COLUMNS:
            continue

        values = df[column].dropna()
        if values.empty or (values.min() >= 0 and values.max() <= 1):
            continue

        minimum, maximum = values.min(), values.max()
        if minimum == maximum:
            df[column] = df[column].where(df[column].isna(), 0.0)
        else:
            df[column] = (df[column] - minimum) / (maximum - minimum)

        scaled = df[column].dropna()
        if ((scaled < -1e-12) | (scaled > 1 + 1e-12)).any():
            raise AssertionError(f"Normalização fora de [0,1] em {column}.")
        normalized.append(column)

    return normalized


def preprocess(input_path, output_path):
    df = pd.read_csv(
        input_path,
        sep="\t",
        decimal=".",
        encoding="utf-8-sig",
        na_values=["#NÚM!"],
        keep_default_na=True,
    )

    missing = [column for column in (*MULTIVALUED_COLUMNS, *ACTIVITY_COLUMNS) if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas esperadas não encontradas no TSV: {missing}")

    normalize_text(df)

    for column in df.select_dtypes(include="string").columns:
        df[column] = df[column].astype(object).replace({"positivo": 1, "negativo": 0})

    normalized = transform_activities(df)

    for column in MULTIVALUED_COLUMNS:
        encode_multivalued_column(df, column)

    df = df.drop(columns=list(MULTIVALUED_COLUMNS))
    df.to_csv(output_path, sep="\t", index=False, encoding="utf-8-sig", na_rep="")
    return len(df), len(df.columns), normalized


def main():
    parser = argparse.ArgumentParser(
        description="Limpa o TSV e cria one-hot posicional para códigos múltiplos de morfologia."
    )
    parser.add_argument("entrada", nargs="?", type=Path, help="TSV de origem (tabulado).")
    parser.add_argument("-o", "--saida", type=Path, help="Arquivo TSV de saída.")
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent
    if args.entrada is None:
        candidates = [repo_dir / "Dados_REG.tsv", repo_dir / "Dados_REG.csv"]
        input_path = next((path for path in candidates if path.exists()), None)
        if input_path is None:
            parser.error("Não encontrei Dados_REG.tsv nem Dados_REG.csv no repositório.")
    else:
        input_path = args.entrada.resolve()

    output_path = args.saida or input_path.with_name(f"{input_path.stem}_tratado.tsv")
    output_path = output_path.resolve()
    if output_path == input_path:
        parser.error("O arquivo de saída não pode sobrescrever o arquivo de entrada.")
    if output_path.exists():
        parser.error(f"O arquivo de saída já existe; escolha outro caminho: {output_path}")

    rows, columns, normalized = preprocess(input_path, output_path)
    print(f"Arquivo salvo: {output_path}")
    print(f"Instâncias: {rows}; colunas finais: {columns}")
    print(f"log1p aplicado em: {', '.join(sorted(LOG_ACTIVITY_COLUMNS))}")
    print(f"Normalização MinMax aplicada em: {', '.join(normalized)}")
    print("Níveis ordinais 0–3 foram divididos por 3; binários e one-hot permaneceram em 0/1.")
    print("Negativos foram mapeados para [0,1] sem corte; ausentes e #NÚM! permaneceram nulos.")


if __name__ == "__main__":
    main()
