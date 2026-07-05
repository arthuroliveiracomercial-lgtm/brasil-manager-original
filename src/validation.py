from dataclasses import dataclass
import re
import unicodedata

import pandas as pd

from .schemas import PRIMARY_KEYS, SCHEMAS

POSITION_ALIASES = {
    "GOLEIRO": "GOL",
    "ZAGUEIRO": "ZAG",
    "LATERAL ESQ.": "LAT",
    "LATERAL ESQ": "LAT",
    "LATERAL DIR.": "LAT",
    "LATERAL DIR": "LAT",
    "ALA": "ALA",
    "VOLANTE": "VOL",
    "MEIA CENTRAL": "MC",
    "MEIA OFENSIVO": "MEI",
    "PONTA ESQUERDA": "PE",
    "PONTA DIREITA": "PD",
    "CENTROAVANTE": "ATA",
    "SEG. ATACANTE": "ATA",
    "SEGUNDO ATACANTE": "ATA",
}
FOOT_ALIASES = {"DIREITO": "D", "ESQUERDO": "E", "AMBIDESTRO": "AMBOS", "AMBOS": "AMBOS"}


@dataclass
class Issue:
    dataset: str
    severity: str
    code: str
    message: str
    row: int | None = None
    column: str | None = None

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def normalize_column(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"_+", "_", re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_")).lower()


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [normalize_column(c) for c in result.columns]
    result = result.dropna(how="all")
    for column in result.select_dtypes(include="object"):
        result[column] = result[column].map(lambda x: x.strip() if isinstance(x, str) else x)
        result[column] = result[column].replace("", pd.NA)
    return result


def validate_dataset(name: str, frame: pd.DataFrame) -> tuple[pd.DataFrame, list[Issue]]:
    if name not in SCHEMAS:
        return frame, [Issue(name, "erro", "dataset_desconhecido", f"Tipo de dado desconhecido: {name}")]
    df = normalize_frame(frame)
    if name == "jogadores":
        if "posicao_principal" in df:
            df["posicao_principal"] = df["posicao_principal"].map(
                lambda value: POSITION_ALIASES.get(str(value).upper(), str(value).upper()) if pd.notna(value) else value
            )
        if "posicoes_secundarias" in df:
            def normalize_positions(value):
                if pd.isna(value):
                    return value
                tokens = re.split(r"[;,/|]", str(value))
                return ";".join(POSITION_ALIASES.get(token.strip().upper(), token.strip().upper()) for token in tokens if token.strip())
            df["posicoes_secundarias"] = df["posicoes_secundarias"].map(normalize_positions)
        if "pe_preferido" in df:
            df["pe_preferido"] = df["pe_preferido"].map(
                lambda value: FOOT_ALIASES.get(str(value).upper(), str(value).upper()) if pd.notna(value) else value
            )
        if "altura" in df:
            height = pd.to_numeric(df["altura"], errors="coerce")
            df["altura"] = height.where(height <= 3, height / 100)
    schema = SCHEMAS[name]
    issues: list[Issue] = []
    missing = [c for c, rule in schema.items() if rule.required and c not in df.columns]
    for column in missing:
        issues.append(Issue(name, "erro", "coluna_ausente", f"Coluna obrigatória ausente: {column}", column=column))
    if missing:
        return df, issues

    for column, rule in schema.items():
        if column not in df.columns:
            df[column] = rule.default
        series = df[column]
        if not rule.nullable:
            for idx in series[series.isna()].index:
                issues.append(Issue(name, "erro", "valor_ausente", f"{column} não pode ficar vazio", int(idx) + 2, column))
        converted = series
        if rule.kind in {"int", "float"}:
            converted = pd.to_numeric(series, errors="coerce")
            invalid = series.notna() & converted.isna()
            for idx in series[invalid].index:
                issues.append(Issue(name, "erro", "tipo_invalido", f"{column} deve ser numérico", int(idx) + 2, column))
            if rule.kind == "int":
                fractional = converted.notna() & (converted % 1 != 0)
                for idx in series[fractional].index:
                    issues.append(Issue(name, "erro", "inteiro_invalido", f"{column} deve ser inteiro", int(idx) + 2, column))
                converted = converted.astype("Int64")
        elif rule.kind == "date":
            converted = pd.to_datetime(series, errors="coerce", dayfirst=True)
            invalid = series.notna() & converted.isna()
            for idx in series[invalid].index:
                issues.append(Issue(name, "erro", "data_invalida", f"Data inválida em {column}", int(idx) + 2, column))
        elif rule.kind == "bool":
            mapping = {"sim": True, "nao": False, "não": False, "true": True, "false": False, "1": True, "0": False}
            converted = series.map(lambda x: mapping.get(str(x).lower(), x) if pd.notna(x) else x)
            invalid = converted.notna() & ~converted.isin([True, False])
            for idx in series[invalid].index:
                issues.append(Issue(name, "erro", "booleano_invalido", f"{column} deve ser sim/não", int(idx) + 2, column))
        if rule.minimum is not None:
            for idx in converted[converted.notna() & (converted < rule.minimum)].index:
                issues.append(Issue(name, "erro", "abaixo_minimo", f"{column} deve ser ≥ {rule.minimum}", int(idx) + 2, column))
        if rule.maximum is not None:
            for idx in converted[converted.notna() & (converted > rule.maximum)].index:
                issues.append(Issue(name, "erro", "acima_maximo", f"{column} deve ser ≤ {rule.maximum}", int(idx) + 2, column))
        if rule.choices:
            upper = series.astype("string").str.upper()
            invalid = series.notna() & ~upper.isin(rule.choices)
            for idx in series[invalid].index:
                issues.append(Issue(name, "erro", "valor_nao_permitido", f"{column}: use {', '.join(rule.choices)}", int(idx) + 2, column))
            converted = upper
        df[column] = converted

    pk = PRIMARY_KEYS[name]
    duplicates = df[pk].notna() & df[pk].duplicated(keep=False)
    for idx in df[duplicates].index:
        issues.append(Issue(name, "erro", "id_duplicado", f"{pk} duplicado: {df.at[idx, pk]}", int(idx) + 2, pk))
    if name == "calendario":
        same = df["mandante_id"].notna() & (df["mandante_id"] == df["visitante_id"])
        for idx in df[same].index:
            issues.append(Issue(name, "erro", "adversario_invalido", "Mandante e visitante não podem ser iguais", int(idx) + 2))
        partial_score = df["gols_mandante"].isna() ^ df["gols_visitante"].isna()
        for idx in df[partial_score].index:
            issues.append(Issue(name, "erro", "placar_incompleto", "Preencha os dois gols ou deixe ambos vazios", int(idx) + 2))
    if name == "jogadores" and "nascimento" in df:
        calculated = ((pd.Timestamp.today().normalize() - df["nascimento"]).dt.days / 365.2425).round()
        mismatch = df["nascimento"].notna() & df["idade"].notna() & ((calculated - df["idade"]).abs() > 1)
        for idx in df[mismatch].index:
            issues.append(Issue(name, "aviso", "idade_inconsistente", "Idade não confere com a data de nascimento", int(idx) + 2, "idade"))
    return df[list(schema)], issues


def validate_relations(data: dict[str, pd.DataFrame], existing: dict[str, set] | None = None) -> list[Issue]:
    existing = existing or {}
    ids = {
        "clubes": set(data.get("clubes", pd.DataFrame()).get("club_id", [])) | existing.get("clubes", set()),
        "jogadores": set(data.get("jogadores", pd.DataFrame()).get("player_id", [])) | existing.get("jogadores", set()),
        "competicoes": set(data.get("competicoes", pd.DataFrame()).get("competition_id", [])) | existing.get("competicoes", set()),
    }
    checks = {
        "jogadores": (("clube_id", "clubes"),),
        "calendario": (("competition_id", "competicoes"), ("mandante_id", "clubes"), ("visitante_id", "clubes")),
        "transferencias": (("player_id", "jogadores"), ("clube_origem_id", "clubes"), ("clube_destino_id", "clubes")),
    }
    issues: list[Issue] = []
    for dataset, relations in checks.items():
        if dataset not in data:
            continue
        for column, target in relations:
            if column not in data[dataset]:
                continue
            invalid = data[dataset][column].notna() & ~data[dataset][column].isin(ids[target])
            for idx in data[dataset][invalid].index:
                issues.append(Issue(dataset, "erro", "referencia_inexistente", f"{column} não existe em {target}: {data[dataset].at[idx, column]}", int(idx) + 2, column))
    return issues
