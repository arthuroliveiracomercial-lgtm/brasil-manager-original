from datetime import date, timedelta
import random
import uuid

from .league_engine import round_robin


def competition_record(competition_id, nome, tipo, temporada, formato, numero_clubes,
                       regiao="Brasil", divisao=None, premiacao=0, promovidos=0, rebaixados=0):
    return {
        "competition_id": competition_id, "nome": nome, "tipo": tipo, "regiao": regiao,
        "temporada": temporada, "divisao": divisao, "formato": formato,
        "numero_clubes": numero_clubes, "fase_atual": "Não iniciada",
        "regras_classificacao": "Configurável", "regras_desempate": "Pontos, vitórias, saldo, gols",
        "premiacao": premiacao, "vagas": None, "promovidos": promovidos,
        "rebaixados": rebaixados, "ativa": 1,
    }


def generate_groups(club_ids, size=4, seed=2026):
    clubs = list(club_ids)
    random.Random(seed).shuffle(clubs)
    return {chr(65 + index): clubs[start:start + size] for index, start in enumerate(range(0, len(clubs), size))}


def generate_league_calendar(club_ids, competition_id, start):
    return round_robin(club_ids, competition_id, start)


def generate_knockout_pairs(club_ids, competition_id, phase_id, two_legs=True, seed=2026):
    clubs = list(club_ids)
    random.Random(seed).shuffle(clubs)
    matches = []
    for index in range(0, len(clubs) - 1, 2):
        home, away = clubs[index], clubs[index + 1]
        match_id = f"{competition_id}-{phase_id}-{index//2+1}-I"
        matches.append({"match_id": match_id, "competition_id": competition_id, "phase_id": phase_id,
                        "mandante_id": home, "visitante_id": away, "perna": 1, "status": "Pendente"})
        if two_legs:
            matches.append({"match_id": match_id[:-1] + "V", "competition_id": competition_id, "phase_id": phase_id,
                            "mandante_id": away, "visitante_id": home, "perna": 2, "status": "Pendente"})
    return matches


def resolve_aggregate(first_leg, second_leg, seed=None):
    home_total = first_leg["gols_mandante"] + second_leg["gols_visitante"]
    away_total = first_leg["gols_visitante"] + second_leg["gols_mandante"]
    if home_total != away_total:
        return first_leg["mandante_id"] if home_total > away_total else first_leg["visitante_id"], None
    rng = random.Random(seed or first_leg["match_id"])
    penalties = [rng.randint(3, 6), rng.randint(3, 6)]
    while penalties[0] == penalties[1]:
        penalties[rng.randint(0, 1)] += 1
    winner = first_leg["mandante_id"] if penalties[0] > penalties[1] else first_leg["visitante_id"]
    return winner, tuple(penalties)


def qualified_from_group(rows, count=2):
    return sorted(rows, key=lambda row: (row["pontos"], row["saldo"], row["gols_pro"]), reverse=True)[:count]


def relegated(rows, count):
    return sorted(rows, key=lambda row: (row["pontos"], row["saldo"], row["gols_pro"]))[:count]


def distribute_prize(database, competition_id, club_id, amount, description):
    database.add_finance(club_id, "Premiação", description, amount, date.today().isoformat())

