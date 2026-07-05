from datetime import date, timedelta
import random

from .competition_engine import competition_record, generate_league_calendar


COMPETITIONS = [
    ("BRA-A", "Brasileirão Série A", "liga", "A", "Pontos corridos", 20, 4, 0),
    ("BRA-B", "Brasileirão Série B", "liga", "B", "Pontos corridos", 20, 4, 4),
    ("BRA-C", "Brasileirão Série C", "liga", "C", "Grupos + mata-mata", 20, 4, 4),
    ("CDB", "Copa do Brasil", "copa", None, "Mata-mata", 64, 0, 0),
    ("PAULISTA", "Campeonato Paulista", "estadual", None, "Fase única + mata-mata", 16, 0, 0),
    ("CARIOCA", "Campeonato Carioca", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("MINEIRO", "Campeonato Mineiro", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("GAUCHO", "Campeonato Gaúcho", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("BAIANO", "Campeonato Baiano", "estadual", None, "Fase única + mata-mata", 10, 0, 0),
    ("CEARENSE", "Campeonato Cearense", "estadual", None, "Fase única + mata-mata", 10, 0, 0),
    ("PERNAMBUCANO", "Campeonato Pernambucano", "estadual", None, "Fase única + mata-mata", 10, 0, 0),
    ("PARANAENSE", "Campeonato Paranaense", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("GOIANO", "Campeonato Goiano", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("CATARINENSE", "Campeonato Catarinense", "estadual", None, "Fase única + mata-mata", 12, 0, 0),
    ("LIB", "Libertadores", "continental", None, "Grupos + mata-mata", 32, 0, 0),
    ("SULA", "Sul-Americana", "continental", None, "Grupos + mata-mata", 32, 0, 0),
]

SERIES_B_C_CLUBS = [
    ("BRA021", "América Mineiro", "América-MG", "MG", "Belo Horizonte", "B", "Arena Independência", 23018, 74),
    ("BRA022", "Athletic Club", "Athletic", "MG", "São João del-Rei", "B", "Estádio Joaquim Portugal", 6000, 62),
    ("BRA023", "Atlético Goianiense SAF", "Atlético-GO", "GO", "Goiânia", "B", "Antônio Accioly", 12500, 72),
    ("BRA024", "Avaí FC", "Avaí", "SC", "Florianópolis", "B", "Ressacada", 17800, 68),
    ("BRA025", "Botafogo-SP", "Botafogo-SP", "SP", "Ribeirão Preto", "B", "Santa Cruz", 29292, 64),
    ("BRA026", "Ceará SC", "Ceará", "CE", "Fortaleza", "B", "Castelão", 63903, 76),
    ("BRA027", "CRB", "CRB", "AL", "Maceió", "B", "Rei Pelé", 17600, 66),
    ("BRA028", "Criciúma EC", "Criciúma", "SC", "Criciúma", "B", "Heriberto Hülse", 19300, 70),
    ("BRA029", "Cuiabá EC", "Cuiabá", "MT", "Cuiabá", "B", "Arena Pantanal", 44000, 72),
    ("BRA030", "Fortaleza SAF", "Fortaleza", "CE", "Fortaleza", "B", "Castelão", 63903, 78),
    ("BRA031", "Goiás EC", "Goiás", "GO", "Goiânia", "B", "Serrinha", 14525, 72),
    ("BRA032", "EC Juventude", "Juventude", "RS", "Caxias do Sul", "B", "Alfredo Jaconi", 19924, 70),
    ("BRA033", "Londrina SAF", "Londrina", "PR", "Londrina", "B", "Estádio do Café", 31000, 62),
    ("BRA034", "Náutico", "Náutico", "PE", "Recife", "B", "Aflitos", 22000, 66),
    ("BRA035", "Grêmio Novorizontino SAF", "Novorizontino", "SP", "Novo Horizonte", "B", "Jorge Ismael de Biasi", 16000, 70),
    ("BRA036", "Operário Ferroviário", "Operário-PR", "PR", "Ponta Grossa", "B", "Germano Krüger", 10600, 66),
    ("BRA037", "AA Ponte Preta", "Ponte Preta", "SP", "Campinas", "B", "Moisés Lucarelli", 19722, 66),
    ("BRA038", "São Bernardo FC", "São Bernardo", "SP", "São Bernardo do Campo", "B", "Primeiro de Maio", 17000, 64),
    ("BRA039", "Sport Recife", "Sport", "PE", "Recife", "B", "Ilha do Retiro", 32983, 74),
    ("BRA040", "Vila Nova FC", "Vila Nova", "GO", "Goiânia", "B", "OBA", 11788, 68),
    ("BRA041", "Amazonas SAF", "Amazonas", "AM", "Manaus", "C", "Arena da Amazônia", 44300, 60),
    ("BRA042", "Ypiranga FC", "Ypiranga-RS", "RS", "Erechim", "C", "Colosso da Lagoa", 22300, 58),
    ("BRA043", "Brusque FC", "Brusque", "SC", "Brusque", "C", "Augusto Bauer", 5000, 60),
    ("BRA044", "Maringá FC SAF", "Maringá", "PR", "Maringá", "C", "Willie Davids", 21600, 58),
    ("BRA045", "Botafogo-PB SAF", "Botafogo-PB", "PB", "João Pessoa", "C", "Almeidão", 25000, 60),
    ("BRA046", "Guarani FC", "Guarani", "SP", "Campinas", "C", "Brinco de Ouro", 29130, 64),
    ("BRA047", "Floresta EC", "Floresta", "CE", "Fortaleza", "C", "Presidente Vargas", 20000, 54),
    ("BRA048", "Paysandu SC", "Paysandu", "PA", "Belém", "C", "Curuzu", 16200, 66),
    ("BRA049", "Barra FC", "Barra", "SC", "Itajaí", "C", "Gigantão das Avenidas", 5000, 52),
    ("BRA050", "Inter de Limeira", "Inter de Limeira", "SP", "Limeira", "C", "Limeirão", 18000, 56),
    ("BRA051", "Santa Cruz", "Santa Cruz", "PE", "Recife", "C", "Arruda", 60000, 66),
    ("BRA052", "Figueirense FC", "Figueirense", "SC", "Florianópolis", "C", "Orlando Scarpelli", 19500, 62),
    ("BRA053", "Ituano FC", "Ituano", "SP", "Itu", "C", "Novelli Júnior", 18560, 60),
    ("BRA054", "SER Caxias", "Caxias", "RS", "Caxias do Sul", "C", "Centenário", 22000, 58),
    ("BRA055", "Confiança SAF", "Confiança", "SE", "Aracaju", "C", "Batistão", 15000, 58),
    ("BRA056", "Volta Redonda FC", "Volta Redonda", "RJ", "Volta Redonda", "C", "Raulino de Oliveira", 18230, 58),
    ("BRA057", "AO Itabaiana", "Itabaiana", "SE", "Itabaiana", "C", "Etelvino Mendonça", 12000, 54),
    ("BRA058", "Ferroviária", "Ferroviária", "SP", "Araraquara", "C", "Fonte Luminosa", 20287, 58),
    ("BRA059", "Maranhão AC", "Maranhão", "MA", "São Luís", "C", "Castelão", 40000, 54),
    ("BRA060", "Anápolis FC", "Anápolis", "GO", "Anápolis", "C", "Jonas Duarte", 17000, 52),
]

CONTINENTAL_CLUBS = [
    ("CON001", "Buenos Aires Azul", "BA Azul", "AR", "Buenos Aires", "INT", "Monumental del Sur", 61000, 82),
    ("CON002", "Buenos Aires Milionários", "BA Milionários", "AR", "Buenos Aires", "INT", "Estádio da Prata", 70000, 84),
    ("CON003", "Avellaneda Vermelho", "Avellaneda", "AR", "Avellaneda", "INT", "Libertadores de América", 48000, 80),
    ("CON004", "Rosário Central", "Rosário", "AR", "Rosário", "INT", "Gigante do Arroyito", 41000, 76),
    ("CON005", "Montevidéu Nacional", "Nacional-UY", "UY", "Montevidéu", "INT", "Gran Parque", 40000, 78),
    ("CON006", "Montevidéu Carbonero", "Carbonero", "UY", "Montevidéu", "INT", "Campeón del Siglo", 40000, 78),
    ("CON007", "Santiago Colo", "Santiago Colo", "CL", "Santiago", "INT", "David Arellano", 47000, 78),
    ("CON008", "Santiago Universidad", "Universidad", "CL", "Santiago", "INT", "Nacional de Chile", 48000, 76),
    ("CON009", "Medellín Rojo", "Medellín", "CO", "Medellín", "INT", "Atanasio Girardot", 44000, 76),
    ("CON010", "Bogotá Verde", "Bogotá Verde", "CO", "Bogotá", "INT", "El Campín", 36000, 74),
    ("CON011", "Quito Azul", "Quito Azul", "EC", "Quito", "INT", "Casa Blanca", 41000, 76),
    ("CON012", "Guayaquil Amarelo", "Guayaquil", "EC", "Guayaquil", "INT", "Monumental Banco", 57000, 78),
    ("CON013", "Lima Alianza", "Alianza", "PE", "Lima", "INT", "Alejandro Villanueva", 34000, 74),
    ("CON014", "Lima Cristal", "Cristal", "PE", "Lima", "INT", "Nacional do Peru", 50000, 72),
    ("CON015", "La Paz Forte", "La Paz", "BO", "La Paz", "INT", "Hernando Siles", 42000, 70),
    ("CON016", "Assunção Olímpico", "Olímpico", "PY", "Assunção", "INT", "Defensores", 42000, 76),
    ("CON017", "Assunção Cerro", "Cerro", "PY", "Assunção", "INT", "Nueva Olla", 45000, 76),
    ("CON018", "Caracas Capital", "Caracas", "VE", "Caracas", "INT", "Olímpico Caracas", 24000, 68),
    ("CON019", "Mendoza Andino", "Mendoza", "AR", "Mendoza", "INT", "Malvinas", 42000, 72),
    ("CON020", "Córdoba Taller", "Córdoba", "AR", "Córdoba", "INT", "Kempes", 57000, 74),
    ("CON021", "Cali Deportivo", "Cali", "CO", "Cali", "INT", "Palmaseca", 42000, 72),
    ("CON022", "Valparaíso Unido", "Valparaíso", "CL", "Valparaíso", "INT", "Playa Ancha", 22000, 70),
    ("CON023", "Cusco Imperial", "Cusco", "PE", "Cusco", "INT", "Inca Garcilaso", 42000, 70),
    ("CON024", "Guaraní Assunção", "Guaraní", "PY", "Assunção", "INT", "Rogelio Livieres", 8000, 70),
]

STATE_COMPETITIONS = {
    "PAULISTA": ("SP", date(2026, 1, 15), 12),
    "CARIOCA": ("RJ", date(2026, 1, 14), 8),
    "MINEIRO": ("MG", date(2026, 1, 17), 8),
    "GAUCHO": ("RS", date(2026, 1, 18), 8),
    "BAIANO": ("BA", date(2026, 1, 20), 6),
    "CEARENSE": ("CE", date(2026, 1, 20), 6),
    "PERNAMBUCANO": ("PE", date(2026, 1, 21), 6),
    "PARANAENSE": ("PR", date(2026, 1, 16), 8),
    "GOIANO": ("GO", date(2026, 1, 16), 8),
    "CATARINENSE": ("SC", date(2026, 1, 17), 8),
}


def seed_expansion(database, season=2026):
    database.run_migrations()
    _ensure_competition_records(database, season)
    _ensure_transfer_windows(database, season)
    _remove_old_generic_bc(database)
    _ensure_series_b_c(database, season)
    _ensure_continental_clubs(database)
    _ensure_all_competition_games(database, season)


def _ensure_competition_records(database, season):
    for cid, name, kind, division, form, clubs, promoted, relegated in COMPETITIONS:
        if database.query("SELECT 1 FROM competitions WHERE competition_id=? LIMIT 1", (cid,)):
            continue
        record = competition_record(
            cid, name, kind, season, form, clubs, divisao=division,
            premiacao=50_000_000 if cid in {"CDB", "LIB"} else 18_000_000 if cid == "SULA" else 8_000_000,
            promovidos=promoted, rebaixados=relegated,
        )
        columns = list(record)
        database.execute(
            f"INSERT INTO competitions({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
            tuple(record[column] for column in columns),
        )


def _ensure_transfer_windows(database, season):
    if database.query("SELECT 1 FROM transfer_windows WHERE temporada=?", (season,)):
        return
    database.executemany(
        "INSERT INTO transfer_windows(window_id,temporada,nome,data_inicio,data_fim,tipo) VALUES(?,?,?,?,?,?)",
        [(f"TW-{season}-1", season, "Janela principal", f"{season}-01-03", f"{season}-03-07", "Principal"),
         (f"TW-{season}-2", season, "Janela do meio do ano", f"{season}-07-01", f"{season}-09-02", "Meio do ano")],
    )


def _remove_old_generic_bc(database):
    # Remove os clubes fictícios criados em versões antigas, quando a base real da Série B/C ainda não existia.
    if not database.query("SELECT 1 FROM clubes WHERE club_id LIKE 'GENB%' OR club_id LIKE 'GENC%' LIMIT 1"):
        return
    database.execute("DELETE FROM competition_matches WHERE mandante_id LIKE 'GENB%' OR visitante_id LIKE 'GENB%' OR mandante_id LIKE 'GENC%' OR visitante_id LIKE 'GENC%'")
    database.execute("DELETE FROM club_season_registration WHERE club_id LIKE 'GENB%' OR club_id LIKE 'GENC%'")
    database.execute("DELETE FROM jogadores WHERE clube_id LIKE 'GENB%' OR clube_id LIKE 'GENC%'")
    database.execute("DELETE FROM clubes WHERE club_id LIKE 'GENB%' OR club_id LIKE 'GENC%'")


def _ensure_series_b_c(database, season):
    for club_id, nome, nome_curto, estado, cidade, divisao, estadio, capacidade, reputacao in SERIES_B_C_CLUBS:
        if not database.query("SELECT 1 FROM clubes WHERE club_id=?", (club_id,)):
            database.execute(
                "INSERT INTO clubes(club_id,nome,nome_curto,estado,cidade,divisao,estadio,capacidade_estadio,reputacao,"
                "orcamento_transferencias,folha_salarial_maxima,saldo_caixa,categoria_base,rival_1,rival_2) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (club_id, nome, nome_curto, estado, cidade, divisao, estadio, capacidade, reputacao,
                 reputacao * 680_000, reputacao * 62_000, reputacao * 1_250_000, 50, None, None),
            )
        _ensure_squad(database, club_id, reputacao, seed=2026 + int(club_id[-3:]), size=25)
    for division, competition_id in (("B", "BRA-B"), ("C", "BRA-C")):
        club_ids = [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao=? ORDER BY club_id", (division,))[:20]]
        database.executemany(
            "INSERT OR IGNORE INTO club_season_registration(competition_id,temporada,club_id) VALUES(?,?,?)",
            [(competition_id, season, club_id) for club_id in club_ids],
        )
        _ensure_league_matches(database, competition_id, club_ids, date(season, 4, 10))


def _ensure_continental_clubs(database):
    for club_id, nome, nome_curto, estado, cidade, divisao, estadio, capacidade, reputacao in CONTINENTAL_CLUBS:
        if not database.query("SELECT 1 FROM clubes WHERE club_id=?", (club_id,)):
            database.execute(
                "INSERT INTO clubes(club_id,nome,nome_curto,estado,cidade,divisao,estadio,capacidade_estadio,reputacao,"
                "orcamento_transferencias,folha_salarial_maxima,saldo_caixa,categoria_base,rival_1,rival_2) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (club_id, nome, nome_curto, estado, cidade, divisao, estadio, capacidade, reputacao,
                 reputacao * 900_000, reputacao * 80_000, reputacao * 1_800_000, 55, None, None),
            )
        _ensure_squad(database, club_id, reputacao, seed=3030 + int(club_id[-3:]), size=22)


def _ensure_squad(database, club_id, reputation, seed, size=25):
    current = database.query("SELECT COUNT(*) total FROM jogadores WHERE clube_id=?", (club_id,))[0]["total"]
    if current >= size:
        return
    rng = random.Random(seed)
    positions = ["GOL", "GOL", "ZAG", "ZAG", "ZAG", "LAT", "LAT", "VOL", "VOL", "MC", "MC", "MEI", "PE", "PD", "ATA", "ATA", "ATA", "ZAG", "MC", "LAT", "VOL", "MEI", "ATA", "PE", "PD"]
    first = ["Lucas", "Gabriel", "Rafael", "Matheus", "João", "Pedro", "André", "Caio", "Bruno", "Diego", "Felipe", "Gustavo", "Henrique", "Igor", "Leandro", "Marcos", "Nicolás", "Santiago", "Tomás", "Franco"]
    last = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira", "Almeida", "Ribeiro", "Carvalho", "Rocha", "Martins", "Barbosa", "Melo", "Freitas", "Nunes", "Gómez", "Pérez", "Rojas", "Fernández"]
    rows = []
    for index in range(current + 1, size + 1):
        position = positions[(index - 1) % len(positions)]
        age = rng.randint(18, 35)
        base = max(38, min(88, reputation + rng.randint(-10, 8)))
        if position == "GOL":
            goal = [max(30, min(92, base + rng.randint(-4, 10))) for _ in range(3)]
            finishing = 24
        else:
            goal = [20, 20, 20]
            finishing = max(28, min(90, base + rng.randint(-10, 10)))
        attrs = [
            max(30, min(90, base + rng.randint(-9, 9))), finishing,
            max(30, min(90, base + rng.randint(-9, 9))), max(30, min(90, base + rng.randint(-9, 9))),
            max(25, min(90, base + rng.randint(-12, 8))), max(25, min(90, base + rng.randint(-12, 8))),
            max(25, min(90, base + rng.randint(-12, 8))), max(25, min(90, base + rng.randint(-12, 8))),
            max(25, min(90, base + rng.randint(-10, 10))), max(35, min(90, base + rng.randint(-8, 10))),
            max(35, min(90, base + rng.randint(-8, 10))), max(35, min(90, base + rng.randint(-9, 9))),
            max(35, min(90, base + rng.randint(-9, 9))), max(30, min(90, base + rng.randint(-9, 9))),
            max(30, min(90, base + rng.randint(-9, 9))), max(30, min(90, base + rng.randint(-9, 9))),
        ]
        player_id = f"{club_id}-P{index:02d}"
        market = int(max(150_000, (base ** 3) * max(0.4, (36 - age) / 18) * 38))
        rows.append((
            player_id, f"{rng.choice(first)} {rng.choice(last)}", None, club_id, age, None,
            "Brasil" if not club_id.startswith("CON") else rng.choice(["Argentina", "Uruguai", "Chile", "Colômbia", "Equador", "Paraguai", "Peru"]),
            position, None, rng.choice(["D", "E"]), round(rng.uniform(1.68, 1.96), 2), rng.randint(64, 93),
            market, int(8_000 + base ** 2 * 12), None, "2028-12-31", base, min(94, base + rng.randint(4, 14)),
            rng.randint(62, 88), rng.randint(82, 100), *attrs, *goal,
        ))
    if rows:
        columns = (
            "player_id,nome,apelido,clube_id,idade,nascimento,nacionalidade,posicao_principal,posicoes_secundarias,"
            "pe_preferido,altura,peso,valor_mercado,salario,contrato_inicio,contrato_fim,reputacao,potencial,moral,"
            "condicao_fisica,ritmo,finalizacao,passe,tecnica,marcacao,desarme,cruzamento,drible,cabeceio,forca,"
            "resistencia,velocidade,aceleracao,decisao,trabalho_equipe,lideranca,goleiro_reflexos,"
            "goleiro_posicionamento,goleiro_jogo_maos"
        )
        database.executemany(f"INSERT OR IGNORE INTO jogadores({columns}) VALUES({','.join('?' for _ in range(39))})", rows)


def _ensure_all_competition_games(database, season):
    if database.query("SELECT 1 FROM competition_matches WHERE competition_id='CDB' LIMIT 1"):
        return
    _seed_copa_do_brasil(database, season)
    _seed_estaduais(database, season)
    _seed_continentais(database, season)


def _ensure_league_matches(database, competition_id, club_ids, start_date):
    if not club_ids or database.query("SELECT 1 FROM competition_matches WHERE competition_id=? LIMIT 1", (competition_id,)):
        return
    matches = generate_league_calendar(club_ids, competition_id, start_date)
    database.executemany(
        "INSERT OR IGNORE INTO competition_matches(match_id,competition_id,phase_id,group_id,data,mandante_id,visitante_id,rodada,perna,gols_mandante,gols_visitante,status)"
        " VALUES(?,?,?,?,?,?,?,?,?,?,?,'Pendente')",
        [(m["match_id"], competition_id, "Pontos corridos", None, m["data"], m["mandante_id"], m["visitante_id"], m["rodada"], 1, None, None) for m in matches],
    )


def _ordered_brazilian_clubs(database):
    return [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao IN ('A','B','C') ORDER BY divisao,reputacao DESC,club_id")]


def _seed_copa_do_brasil(database, season):
    clubs = _ordered_brazilian_clubs(database)
    rng = random.Random(601)
    rng.shuffle(clubs)
    phases = [
        ("1ª fase", clubs[:60], date(season, 2, 18), False),
        ("2ª fase", clubs[:32], date(season, 3, 11), False),
        ("Oitavas", clubs[:16], date(season, 5, 6), True),
        ("Quartas", clubs[:8], date(season, 7, 15), True),
        ("Semifinal", clubs[:4], date(season, 8, 26), True),
        ("Final", clubs[:2], date(season, 10, 21), True),
    ]
    rows = []
    for phase, participants, start, two_legs in phases:
        rng.shuffle(participants)
        for game_index in range(0, len(participants) - 1, 2):
            home, away = participants[game_index], participants[game_index + 1]
            round_no = len(rows) + 1
            slug = phase.replace("ª", "A").replace(" ", "").upper()
            rows.append((f"CDB-{slug}-{game_index//2+1:02d}-1", "CDB", phase, None, start.isoformat(), home, away, round_no, 1, None, None))
            if two_legs:
                rows.append((f"CDB-{slug}-{game_index//2+1:02d}-2", "CDB", phase, None, (start + timedelta(days=7)).isoformat(), away, home, round_no + 1, 2, None, None))
    _insert_competition_rows(database, rows)
    database.execute("UPDATE competitions SET fase_atual='1ª fase', numero_clubes=? WHERE competition_id='CDB'", (min(64, len(clubs)),))


def _seed_estaduais(database, season):
    for comp_id, (state, start, target) in STATE_COMPETITIONS.items():
        clubs = [row["club_id"] for row in database.query(
            "SELECT club_id FROM clubes WHERE estado=? AND divisao IN ('A','B','C') ORDER BY reputacao DESC,club_id", (state,)
        )]
        if len(clubs) < 4:
            fillers = [row["club_id"] for row in database.query(
                "SELECT club_id FROM clubes WHERE divisao IN ('A','B','C') AND estado<>? ORDER BY reputacao DESC,club_id LIMIT ?",
                (state, 4 - len(clubs)),
            )]
            clubs += fillers
        clubs = clubs[:target]
        if len(clubs) < 2:
            continue
        rows = []
        league_matches = generate_league_calendar(clubs, comp_id, start)
        # Fase única em turno único, para não alongar demais o estadual.
        max_round = max(1, len(clubs) - 1)
        for m in league_matches:
            if m["rodada"] > max_round:
                continue
            rows.append((m["match_id"], comp_id, "Fase única", None, m["data"], m["mandante_id"], m["visitante_id"], m["rodada"], 1, None, None))
        seeded = clubs[:4]
        semi_date = start + timedelta(days=(max_round + 1) * 7)
        final_date = semi_date + timedelta(days=10)
        if len(seeded) >= 4:
            rows.extend([
                (f"{comp_id}-SEMI-1", comp_id, "Semifinal", None, semi_date.isoformat(), seeded[0], seeded[3], max_round + 1, 1, None, None),
                (f"{comp_id}-SEMI-2", comp_id, "Semifinal", None, semi_date.isoformat(), seeded[1], seeded[2], max_round + 1, 1, None, None),
                (f"{comp_id}-FINAL", comp_id, "Final", None, final_date.isoformat(), seeded[0], seeded[1], max_round + 2, 1, None, None),
            ])
        _insert_competition_rows(database, rows)
        database.execute("UPDATE competitions SET fase_atual='Fase única', numero_clubes=? WHERE competition_id=?", (len(clubs), comp_id))


def _seed_continentais(database, season):
    brazil = [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao='A' ORDER BY reputacao DESC,club_id")]
    invited = [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao='INT' ORDER BY reputacao DESC,club_id")]
    lib = (brazil[:8] + invited[:24])[:32]
    sula = (brazil[8:16] + [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao IN ('B','C') ORDER BY reputacao DESC,club_id LIMIT 8")] + invited[8:24])[:32]
    _seed_group_stage(database, "LIB", lib, date(season, 3, 3), "Grupo", seed=710)
    _seed_group_stage(database, "SULA", sula, date(season, 3, 5), "Grupo", seed=720)
    database.execute("UPDATE competitions SET fase_atual='Fase de grupos', numero_clubes=? WHERE competition_id='LIB'", (len(lib),))
    database.execute("UPDATE competitions SET fase_atual='Fase de grupos', numero_clubes=? WHERE competition_id='SULA'", (len(sula),))


def _seed_group_stage(database, comp_id, clubs, start, group_label, seed):
    rng = random.Random(seed)
    clubs = list(clubs)
    rng.shuffle(clubs)
    rows = []
    for group_index in range(0, len(clubs), 4):
        group = clubs[group_index:group_index + 4]
        group_name = f"{group_label} {chr(65 + group_index//4)}"
        if len(group) < 4:
            continue
        fixtures = [(0, 1), (2, 3), (0, 2), (3, 1), (0, 3), (1, 2)]
        for i, (a, b) in enumerate(fixtures, 1):
            match_date = start + timedelta(days=(i - 1) * 14)
            rows.append((f"{comp_id}-{group_name[-1]}-R{i:02d}-J1", comp_id, "Fase de grupos", group_name, match_date.isoformat(), group[a], group[b], i, 1, None, None))
            rows.append((f"{comp_id}-{group_name[-1]}-R{i:02d}-J2", comp_id, "Fase de grupos", group_name, match_date.isoformat(), group[(a + 2) % 4], group[(b + 2) % 4], i, 1, None, None))
    seeded = clubs[:16]
    knockout_dates = [("Oitavas", start + timedelta(days=112)), ("Quartas", start + timedelta(days=154)), ("Semifinal", start + timedelta(days=196)), ("Final", start + timedelta(days=238))]
    counts = [16, 8, 4, 2]
    for (phase, dt), count in zip(knockout_dates, counts):
        participants = seeded[:count]
        for index in range(0, len(participants) - 1, 2):
            home, away = participants[index], participants[index + 1]
            rows.append((f"{comp_id}-{phase.upper()}-{index//2+1:02d}-1", comp_id, phase, None, dt.isoformat(), home, away, 100 + index, 1, None, None))
            if phase != "Final":
                rows.append((f"{comp_id}-{phase.upper()}-{index//2+1:02d}-2", comp_id, phase, None, (dt + timedelta(days=7)).isoformat(), away, home, 101 + index, 2, None, None))
    _insert_competition_rows(database, rows)


def _insert_competition_rows(database, rows):
    if not rows:
        return
    database.executemany(
        "INSERT OR IGNORE INTO competition_matches(match_id,competition_id,phase_id,group_id,data,mandante_id,visitante_id,rodada,perna,gols_mandante,gols_visitante,status)"
        " VALUES(?,?,?,?,?,?,?,?,?,?,?,'Pendente')",
        rows,
    )

# --- Rebuild de estrutura v2: divisões separadas e copas sem fases futuras pré-definidas ---
def rebuild_competition_structure(database, season=2026, force=False):
    """Corrige bases antigas que misturavam séries ou criavam finais antes da hora."""
    database.run_migrations()
    # Executa sempre de forma idempotente para evitar saves corrompidos por versões anteriores.
    _ensure_competition_records(database, season)
    _ensure_transfer_windows(database, season)
    _remove_old_generic_bc(database)
    _ensure_series_b_c(database, season)
    _ensure_continental_clubs(database)
    _rebuild_domestic_leagues(database, season)
    _rebuild_cups_initial_phases(database, season)


def _rebuild_domestic_leagues(database, season):
    from .league_engine import round_robin, empty_standing
    comps = [("A", "COMP001", date(season, 4, 5)), ("B", "COMP002", date(season, 4, 10)), ("C", "COMP003", date(season, 4, 12))]
    # Se qualquer competição estiver com times demais na classificação, refaz liga nacional.
    needs = False
    for _, comp_id, _ in comps:
        count = database.query("SELECT COUNT(*) n FROM classificacao WHERE competition_id=?", (comp_id,))[0]["n"]
        if count not in (0, 20):
            needs = True
    # Também refaz quando COMP001 contém clubes B/C.
    mixed = database.query("SELECT COUNT(*) n FROM classificacao cl JOIN clubes c ON c.club_id=cl.club_id WHERE cl.competition_id='COMP001' AND c.divisao<>'A'")[0]["n"]
    if mixed:
        needs = True
    if not needs and database.query("SELECT COUNT(*) n FROM calendario WHERE competition_id IN ('COMP001','COMP002','COMP003')")[0]["n"] >= 700:
        return
    with closing(database.connect()) as conn:
        conn.execute("DELETE FROM eventos_partida")
        conn.execute("DELETE FROM detalhes_partida")
        conn.execute("DELETE FROM calendario WHERE competition_id IN ('COMP001','COMP002','COMP003','BRA-A','BRA-B','BRA-C')")
        conn.execute("DELETE FROM classificacao WHERE competition_id IN ('COMP001','COMP002','COMP003','BRA-A','BRA-B','BRA-C')")
        for division, comp_id, start_dt in comps:
            club_ids = [r[0] for r in conn.execute("SELECT club_id FROM clubes WHERE divisao=? ORDER BY reputacao DESC, club_id LIMIT 20", (division,)).fetchall()]
            conn.executemany(
                "INSERT INTO calendario(match_id,competition_id,rodada,data,mandante_id,visitante_id,estadio,jogado,gols_mandante,gols_visitante) "
                "VALUES(:match_id,:competition_id,:rodada,:data,:mandante_id,:visitante_id,:estadio,:jogado,:gols_mandante,:gols_visitante)",
                round_robin(club_ids, competition_id=comp_id, start=start_dt),
            )
            conn.executemany(
                "INSERT INTO classificacao(competition_id,club_id,jogos,vitorias,empates,derrotas,gols_pro,gols_contra,saldo,pontos) "
                "VALUES(:competition_id,:club_id,:jogos,:vitorias,:empates,:derrotas,:gols_pro,:gols_contra,:saldo,:pontos)",
                empty_standing(club_ids, competition_id=comp_id),
            )
            conn.execute("UPDATE competicoes SET numero_times=?, divisao=? WHERE competition_id=?", (len(club_ids), division, comp_id))
        conn.execute("UPDATE game_state SET rodada_atual=1 WHERE id=1")
        conn.commit()


def _rebuild_cups_initial_phases(database, season):
    # Sempre remove o calendário de copas bugado que pré-criava quartas/semi/final.
    database.execute("DELETE FROM competition_matches")
    _seed_copa_do_brasil_initial(database, season)
    _seed_estaduais_initial(database, season)
    _seed_continentais_groups_only(database, season)


def _seed_copa_do_brasil_initial(database, season):
    clubs = _ordered_brazilian_clubs(database)[:60]
    rng = random.Random(1601)
    rng.shuffle(clubs)
    rows = []
    start = date(season, 2, 18)
    for idx in range(0, len(clubs)-1, 2):
        home, away = clubs[idx], clubs[idx+1]
        rows.append((f"CDB-F1-{idx//2+1:02d}", "CDB", "1ª fase", None, (start + timedelta(days=(idx//2)//10)).isoformat(), home, away, 1, 1, None, None))
    _insert_competition_rows(database, rows)
    database.execute("UPDATE competitions SET fase_atual='1ª fase', formato='Mata-mata progressivo', numero_clubes=? WHERE competition_id='CDB'", (len(clubs),))


def _seed_estaduais_initial(database, season):
    for comp_id, (state, start, target) in STATE_COMPETITIONS.items():
        clubs = [row["club_id"] for row in database.query(
            "SELECT club_id FROM clubes WHERE estado=? AND divisao IN ('A','B','C') ORDER BY reputacao DESC,club_id LIMIT ?", (state, target)
        )]
        if len(clubs) < 4:
            fillers = [row["club_id"] for row in database.query(
                "SELECT club_id FROM clubes WHERE divisao IN ('A','B','C') AND estado<>? ORDER BY reputacao DESC,club_id LIMIT ?", (state, 4-len(clubs))
            )]
            clubs += fillers
        clubs = clubs[:max(4, min(target, len(clubs)))]
        rows = []
        if len(clubs) >= 2:
            league_matches = generate_league_calendar(clubs, comp_id, start)
            max_round = max(1, len(clubs)-1)
            for m in league_matches:
                if m["rodada"] <= max_round:
                    rows.append((m["match_id"], comp_id, "Fase classificatória", None, m["data"], m["mandante_id"], m["visitante_id"], m["rodada"], 1, None, None))
            _insert_competition_rows(database, rows)
            database.execute("UPDATE competitions SET fase_atual='Fase classificatória', formato='Classificatória + mata-mata', numero_clubes=? WHERE competition_id=?", (len(clubs), comp_id))


def _seed_continentais_groups_only(database, season):
    brazil = [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao='A' ORDER BY reputacao DESC,club_id")]
    invited = [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao='INT' ORDER BY reputacao DESC,club_id")]
    lib = (brazil[:8] + invited[:24])[:32]
    sula = (brazil[8:16] + [row["club_id"] for row in database.query("SELECT club_id FROM clubes WHERE divisao IN ('B','C') ORDER BY reputacao DESC,club_id LIMIT 8")] + invited[8:24])[:32]
    _seed_group_stage_only(database, "LIB", lib, date(season, 3, 3), seed=3710)
    _seed_group_stage_only(database, "SULA", sula, date(season, 3, 5), seed=3720)
    database.execute("UPDATE competitions SET fase_atual='Fase de grupos', formato='Grupos + mata-mata progressivo', numero_clubes=? WHERE competition_id='LIB'", (len(lib),))
    database.execute("UPDATE competitions SET fase_atual='Fase de grupos', formato='Grupos + mata-mata progressivo', numero_clubes=? WHERE competition_id='SULA'", (len(sula),))


def _seed_group_stage_only(database, comp_id, clubs, start, seed):
    rng = random.Random(seed)
    clubs = list(clubs)
    rng.shuffle(clubs)
    rows = []
    for gi in range(0, len(clubs), 4):
        group = clubs[gi:gi+4]
        if len(group) < 4:
            continue
        group_name = f"Grupo {chr(65+gi//4)}"
        fixtures = [(0,1),(2,3),(0,2),(3,1),(0,3),(1,2)]
        for i, (a,b) in enumerate(fixtures, 1):
            dt = start + timedelta(days=(i-1)*14)
            rows.append((f"{comp_id}-{group_name[-1]}-R{i:02d}-J1", comp_id, "Fase de grupos", group_name, dt.isoformat(), group[a], group[b], i, 1, None, None))
            rows.append((f"{comp_id}-{group_name[-1]}-R{i:02d}-J2", comp_id, "Fase de grupos", group_name, dt.isoformat(), group[(a+2)%4], group[(b+2)%4], i, 1, None, None))
    _insert_competition_rows(database, rows)
