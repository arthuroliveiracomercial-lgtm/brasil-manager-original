from datetime import date
import random

from .competition_engine import competition_record, generate_league_calendar


COMPETITIONS = [
    ("BRA-A", "Brasileirão Série A", "liga", "A", "Pontos corridos", 20, 4, 0),
    ("BRA-B", "Brasileirão Série B", "liga", "B", "Pontos corridos", 20, 4, 4),
    ("BRA-C", "Brasileirão Série C", "liga", "C", "Grupos + mata-mata", 20, 4, 4),
    ("CDB", "Copa do Brasil", "copa", None, "Mata-mata", 64, 0, 0),
    ("PAULISTA", "Campeonato Paulista", "estadual", None, "Grupos + mata-mata", 16, 0, 0),
    ("CARIOCA", "Campeonato Carioca", "estadual", None, "Liga curta + mata-mata", 12, 0, 0),
    ("MINEIRO", "Campeonato Mineiro", "estadual", None, "Grupos + mata-mata", 12, 0, 0),
    ("GAUCHO", "Campeonato Gaúcho", "estadual", None, "Liga curta + mata-mata", 12, 0, 0),
    ("BAIANO", "Campeonato Baiano", "estadual", None, "Liga curta + mata-mata", 10, 0, 0),
    ("CEARENSE", "Campeonato Cearense", "estadual", None, "Grupos + mata-mata", 10, 0, 0),
    ("PERNAMBUCANO", "Campeonato Pernambucano", "estadual", None, "Liga curta + mata-mata", 10, 0, 0),
    ("PARANAENSE", "Campeonato Paranaense", "estadual", None, "Liga curta + mata-mata", 12, 0, 0),
    ("GOIANO", "Campeonato Goiano", "estadual", None, "Liga curta + mata-mata", 12, 0, 0),
    ("CATARINENSE", "Campeonato Catarinense", "estadual", None, "Liga curta + mata-mata", 12, 0, 0),
    ("LIB", "Libertadores", "continental", None, "Grupos + mata-mata", 32, 0, 0),
    ("SULA", "Sul-Americana", "continental", None, "Grupos + mata-mata", 32, 0, 0),
]


def seed_expansion(database, season=2026):
    database.run_migrations()
    if not database.query("SELECT 1 FROM competitions LIMIT 1"):
        for cid, name, kind, division, form, clubs, promoted, relegated in COMPETITIONS:
            record = competition_record(cid, name, kind, season, form, clubs, divisao=division,
                                        premiacao=50_000_000 if cid in {"CDB","LIB"} else 10_000_000,
                                        promovidos=promoted, rebaixados=relegated)
            columns = list(record)
            database.execute(
                f"INSERT INTO competitions({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
                tuple(record[column] for column in columns),
            )
    if not database.query("SELECT 1 FROM transfer_windows WHERE temporada=?", (season,)):
        database.executemany(
            "INSERT INTO transfer_windows(window_id,temporada,nome,data_inicio,data_fim,tipo) VALUES(?,?,?,?,?,?)",
            [(f"TW-{season}-1", season, "Janela principal", f"{season}-01-03", f"{season}-03-07", "Principal"),
             (f"TW-{season}-2", season, "Janela do meio do ano", f"{season}-07-01", f"{season}-09-02", "Meio do ano")],
        )
    _seed_division(database, "B", 20, 58, season)
    _seed_division(database, "C", 20, 48, season)


def _seed_division(database, division, count, reputation_base, season):
    prefix = f"GEN{division}"
    if database.query("SELECT 1 FROM clubes WHERE club_id LIKE ? LIMIT 1", (prefix + "%",)):
        return
    rng = random.Random(2026 + ord(division))
    club_rows, player_rows = [], []
    positions = ["GOL","GOL","ZAG","ZAG","ZAG","LAT","LAT","VOL","VOL","MC","MC","MEI","PE","PD","ATA","ATA","ATA","ZAG"]
    for index in range(1, count + 1):
        club_id = f"{prefix}{index:02d}"
        reputation = reputation_base + rng.randint(-6, 8)
        name = f"Esporte {division} {index:02d}"
        club_rows.append((club_id, name, name, "BR", "Cidade Brasileira", division, f"Estádio {name}",
                          9000 + index * 600, reputation, reputation * 45_000, reputation * 20_000,
                          reputation * 70_000, 45, None, None))
        for number, position in enumerate(positions, 1):
            base = reputation + rng.randint(-8, 8)
            player_rows.append((
                f"{club_id}-P{number:02d}", f"Jogador {division}{index:02d}-{number:02d}", None, club_id,
                rng.randint(18, 34), None, "Brasil", position, None, rng.choice(["D","E"]),
                round(rng.uniform(1.68, 1.94), 2), rng.randint(64, 92), max(100_000, base**3*20),
                8_000 + base**2*6, None, f"{season+2}-12-31", base, min(90,base+8),
                70, 95, *[max(25,min(88,base+rng.randint(-9,9))) for _ in range(16)], 50, 50, 50,
            ))
    database.executemany(
        "INSERT INTO clubes(club_id,nome,nome_curto,estado,cidade,divisao,estadio,capacidade_estadio,reputacao,"
        "orcamento_transferencias,folha_salarial_maxima,saldo_caixa,categoria_base,rival_1,rival_2) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        club_rows,
    )
    columns = ("player_id,nome,apelido,clube_id,idade,nascimento,nacionalidade,posicao_principal,posicoes_secundarias,"
               "pe_preferido,altura,peso,valor_mercado,salario,contrato_inicio,contrato_fim,reputacao,potencial,moral,"
               "condicao_fisica,ritmo,finalizacao,passe,tecnica,marcacao,desarme,cruzamento,drible,cabeceio,forca,"
               "resistencia,velocidade,aceleracao,decisao,trabalho_equipe,lideranca,goleiro_reflexos,"
               "goleiro_posicionamento,goleiro_jogo_maos")
    database.executemany(f"INSERT INTO jogadores({columns}) VALUES({','.join('?' for _ in range(39))})", player_rows)
    competition_id = f"BRA-{division}"
    database.executemany(
        "INSERT OR IGNORE INTO club_season_registration(competition_id,temporada,club_id) VALUES(?,?,?)",
        [(competition_id, season, row[0]) for row in club_rows],
    )
    matches = generate_league_calendar([row[0] for row in club_rows], competition_id, date(season, 4, 10))
    database.executemany(
        "INSERT OR IGNORE INTO competition_matches(match_id,competition_id,data,mandante_id,visitante_id,rodada,status)"
        " VALUES(?,?,?,?,?,?,'Pendente')",
        [(match["match_id"], competition_id, match["data"], match["mandante_id"], match["visitante_id"], match["rodada"])
         for match in matches],
    )
