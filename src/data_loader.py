from io import BytesIO
from pathlib import Path
from datetime import date
from contextlib import closing
import random

import pandas as pd

from .schemas import SCHEMAS
from .league_engine import empty_standing, round_robin


def _read_csv(content: bytes) -> pd.DataFrame:
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        for separator in (None, ";", ","):
            try:
                return pd.read_csv(BytesIO(content), encoding=encoding, sep=separator, engine="python")
            except (UnicodeDecodeError, pd.errors.ParserError) as exc:
                last_error = exc
    raise ValueError(f"Não foi possível ler o CSV: {last_error}")


def load_upload(filename: str, content: bytes, dataset: str | None = None) -> dict[str, pd.DataFrame]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        name = dataset or Path(filename).stem.lower()
        if name not in SCHEMAS:
            raise ValueError(f"Nome de CSV desconhecido: {name}. Use: {', '.join(SCHEMAS)}")
        return {name: _read_csv(content)}
    if suffix in {".xlsx", ".xlsm"}:
        sheets = pd.read_excel(BytesIO(content), sheet_name=None, engine="openpyxl")
        normalized = {str(k).strip().lower(): v for k, v in sheets.items()}
        known = {k: v for k, v in normalized.items() if k in SCHEMAS}
        if not known:
            raise ValueError(f"A planilha precisa ter ao menos uma aba: {', '.join(SCHEMAS)}")
        return known
    raise ValueError("Formato não aceito. Envie CSV ou XLSX.")


def bootstrap_game(database, workbook_path: str | Path = "data/modelos/modelo_importacao_brasil_manager.xlsx") -> bool:
    """Importa a planilha inicial e prepara a base sem misturar divisões.

    A versão anterior recriava o calendário usando todos os clubes como se fossem
    uma única Série A. Agora a planilha é respeitada: Série A, B e C ficam em
    competições separadas.
    """
    if database.table_counts()["clubes"]:
        return False
    path = Path(workbook_path)
    if not path.exists():
        raise FileNotFoundError(f"Planilha inicial não encontrada: {path}")
    from .data_update import validate_upload

    result = validate_upload(path.name, path.read_bytes(), database)
    if not result.can_import:
        messages = "; ".join(issue.message for issue in result.issues if issue.severity == "erro")
        raise ValueError(f"Planilha inicial inválida: {messages}")
    database.import_frames(result.data, path.name, "atualizar")
    _complete_players(database)
    _create_season(database)
    return True


def _complete_clubs(database) -> None:
    existing = database.query("SELECT club_id FROM clubes")
    states = [("SP", "São Paulo"), ("RJ", "Rio de Janeiro"), ("MG", "Belo Horizonte"),
              ("RS", "Porto Alegre"), ("PR", "Curitiba"), ("BA", "Salvador"),
              ("PE", "Recife"), ("CE", "Fortaleza"), ("GO", "Goiânia"), ("SC", "Florianópolis")]
    names = ["Aurora", "Nacional do Vale", "União Imperial", "Ferroviário Central", "Atlético Litorâneo",
             "Estrela do Sul", "Operário Brasil", "Guarani da Serra", "Real Metropolitano",
             "Independente", "Vitória do Norte", "Portuguesa Nova", "Juventude Capital",
             "América Atlética", "São Bento Nacional", "Grêmio do Cerrado", "Rio Branco Unido",
             "Esporte Clube Pioneiro"]
    rows = []
    for index in range(len(existing) + 1, 21):
        state, city = states[(index - 1) % len(states)]
        name = names[(index - 3) % len(names)]
        reputation = 48 + ((index * 7) % 31)
        rows.append((f"BRA{index:03d}", name, name[:14], state, city, "A", f"Arena {name}",
                     18000 + index * 900, reputation, 4_000_000 + reputation * 90_000,
                     1_500_000 + reputation * 35_000, 8_000_000 + reputation * 100_000, 45 + index % 30, None, None))
    if rows:
        database.executemany(
            "INSERT INTO clubes(club_id,nome,nome_curto,estado,cidade,divisao,estadio,capacidade_estadio,"
            "reputacao,orcamento_transferencias,folha_salarial_maxima,saldo_caixa,categoria_base,rival_1,rival_2)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows,
        )


def _complete_players(database) -> None:
    rng = random.Random(2026)
    clubs = database.query("SELECT club_id,reputacao FROM clubes ORDER BY club_id")
    first_names = ["Lucas", "Gabriel", "Rafael", "Matheus", "João", "Pedro", "André", "Caio",
                   "Bruno", "Diego", "Felipe", "Gustavo", "Henrique", "Igor", "Leandro", "Marcos"]
    surnames = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira", "Almeida",
                "Ribeiro", "Carvalho", "Rocha", "Martins", "Barbosa", "Melo", "Freitas", "Nunes"]
    positions = ["GOL", "GOL", "ZAG", "ZAG", "ZAG", "ZAG", "LAT", "LAT", "LAT", "VOL", "VOL",
                 "MC", "MC", "MEI", "PE", "PD", "ATA", "ATA", "ATA", "MC", "ZAG", "ATA"]
    rows = []
    for club_index, club in enumerate(clubs, 1):
        current = database.query("SELECT COUNT(*) total FROM jogadores WHERE clube_id=?", (club["club_id"],))[0]["total"]
        for squad_index in range(current, 22):
            position = positions[squad_index]
            age = rng.randint(18, 34)
            base = max(42, min(86, int(club["reputacao"] * 0.68 + rng.randint(4, 19))))
            attrs = {key: max(25, min(92, base + rng.randint(-9, 9))) for key in (
                "ritmo finalizacao passe tecnica marcacao desarme cruzamento drible cabeceio forca "
                "resistencia velocidade aceleracao decisao trabalho_equipe lideranca".split()
            )}
            if position == "GOL":
                goalkeeping = [base + rng.randint(0, 8) for _ in range(3)]
                attrs["finalizacao"] = 25
            else:
                goalkeeping = [20, 20, 20]
            player_id = f"P{club_index:02d}{squad_index + 1:02d}"
            name = f"{rng.choice(first_names)} {rng.choice(surnames)}"
            value = int((base ** 3) * max(0.5, (34 - age) / 15) * 55)
            rows.append((
                player_id, name, None, club["club_id"], age, None, "Brasil", position, None,
                rng.choice(["D", "E"]), round(rng.uniform(1.68, 1.94), 2), rng.randint(64, 91),
                value, int(12_000 + base ** 2 * 10), None, "2028-12-31", base,
                min(95, base + max(0, 27 - age)), rng.randint(65, 90), rng.randint(82, 100),
                *(attrs[key] for key in "ritmo finalizacao passe tecnica marcacao desarme cruzamento drible cabeceio forca resistencia velocidade aceleracao decisao trabalho_equipe lideranca".split()),
                *goalkeeping,
            ))
    if rows:
        columns = (
            "player_id,nome,apelido,clube_id,idade,nascimento,nacionalidade,posicao_principal,"
            "posicoes_secundarias,pe_preferido,altura,peso,valor_mercado,salario,contrato_inicio,"
            "contrato_fim,reputacao,potencial,moral,condicao_fisica,ritmo,finalizacao,passe,tecnica,"
            "marcacao,desarme,cruzamento,drible,cabeceio,forca,resistencia,velocidade,aceleracao,"
            "decisao,trabalho_equipe,lideranca,goleiro_reflexos,goleiro_posicionamento,goleiro_jogo_maos"
        )
        database.executemany(
            f"INSERT OR IGNORE INTO jogadores({columns}) VALUES({','.join('?' for _ in range(39))})", rows,
        )


def _create_season(database) -> None:
    """Garante classificação e calendário separados para A, B e C."""
    from .league_engine import round_robin, empty_standing
    comps = [("A", "COMP001", date(2026, 4, 5)), ("B", "COMP002", date(2026, 4, 10)), ("C", "COMP003", date(2026, 4, 12))]
    with closing(database.connect()) as conn:
        conn.execute("DELETE FROM classificacao")
        # Preserva o calendário importado quando ele já está correto; se não houver, recria.
        existing = conn.execute("SELECT COUNT(*) FROM calendario").fetchone()[0]
        if existing == 0:
            for division, comp_id, start_date in comps:
                club_ids = [r[0] for r in conn.execute("SELECT club_id FROM clubes WHERE divisao=? ORDER BY club_id", (division,)).fetchall()[:20]]
                if club_ids:
                    conn.executemany(
                        "INSERT INTO calendario(match_id,competition_id,rodada,data,mandante_id,visitante_id,estadio,jogado,gols_mandante,gols_visitante) "
                        "VALUES(:match_id,:competition_id,:rodada,:data,:mandante_id,:visitante_id,:estadio,:jogado,:gols_mandante,:gols_visitante)",
                        round_robin(club_ids, competition_id=comp_id, start=start_date),
                    )
        for division, comp_id, _ in comps:
            club_ids = [r[0] for r in conn.execute("SELECT club_id FROM clubes WHERE divisao=? ORDER BY club_id", (division,)).fetchall()[:20]]
            conn.executemany(
                "INSERT OR IGNORE INTO classificacao(competition_id,club_id,jogos,vitorias,empates,derrotas,gols_pro,gols_contra,saldo,pontos) "
                "VALUES(:competition_id,:club_id,:jogos,:vitorias,:empates,:derrotas,:gols_pro,:gols_contra,:saldo,:pontos)",
                empty_standing(club_ids, competition_id=comp_id),
            )
            conn.execute("UPDATE competicoes SET numero_times=? WHERE competition_id=?", (len(club_ids), comp_id))
        conn.commit()
