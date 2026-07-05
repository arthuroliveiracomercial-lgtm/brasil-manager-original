import math
import random

from .models import MatchResult, Tactic
from .tactic_engine import compatibility_bonus, role_modifiers, tactic_modifiers

POSITION_GROUPS = {
    "GOL": {"GOL"}, "ZAG": {"ZAG"}, "LAT": {"LAT", "ALA"}, "ALA": {"ALA", "LAT"},
    "VOL": {"VOL", "MC"}, "MC": {"MC", "VOL", "MEI"}, "MEI": {"MEI", "MC", "PE", "PD"},
    "PE": {"PE", "PD", "MEI"}, "PD": {"PD", "PE", "MEI"}, "ATA": {"ATA", "PE", "PD"},
}


def player_rating(player: dict, slot: str | None = None) -> float:
    position = player.get("posicao_principal", "MC")
    if position == "GOL":
        keys = ("goleiro_reflexos", "goleiro_posicionamento", "goleiro_jogo_maos", "decisao")
    elif position in {"ZAG", "LAT", "ALA", "VOL"}:
        keys = ("marcacao", "desarme", "forca", "resistencia", "passe")
    else:
        keys = ("finalizacao", "passe", "tecnica", "drible", "velocidade", "decisao")
    rating = sum(float(player.get(key) or 50) for key in keys) / len(keys)
    rating += (float(player.get("moral") or 70) - 70) * 0.05
    rating += (float(player.get("condicao_fisica") or 90) - 80) * 0.04
    if slot and position not in POSITION_GROUPS.get(slot, {slot}):
        secondaries = set(str(player.get("posicoes_secundarias") or "").replace(",", ";").split(";"))
        rating -= 5 if slot in secondaries else 14
    return max(20, min(99, rating))


def team_strength(players, slots, reputation, tactic, roles=None):
    if not players:
        base = 35 + reputation * 0.3
        return base, base
    ratings = [player_rating(player, slots[i] if i < len(slots) else None) for i, player in enumerate(players[:11])]
    base = sum(ratings) / len(ratings)
    attack_mod, defense_mod, _ = tactic_modifiers(tactic)
    role_attack, role_defense = role_modifiers(roles)
    fit = compatibility_bonus(tactic, players[:11])
    goalkeeper = next((p for p in players if p.get("posicao_principal") == "GOL"), None)
    keeper_bonus = ((player_rating(goalkeeper, "GOL") - 55) / 12) if goalkeeper else 0
    return base + attack_mod + role_attack + fit + reputation * 0.05, base + defense_mod + role_defense + keeper_bonus + reputation * 0.05


def _poisson(rng, expectation):
    limit, product, count = math.exp(-expectation), 1.0, 0
    while product > limit:
        count += 1
        product *= rng.random()
    return max(0, count - 1)


def _name(player):
    return player.get("apelido") or player.get("nome") or "Jogador"


def simulate_match(match_id, home, away, home_players, away_players, home_slots, away_slots,
                   home_tactic, away_tactic, seed=None, home_roles=None, away_roles=None):
    rng = random.Random(str(seed or match_id))
    ha, hd = team_strength(home_players, home_slots, home.get("reputacao", 50), home_tactic, home_roles)
    aa, ad = team_strength(away_players, away_slots, away.get("reputacao", 50), away_tactic, away_roles)
    home_xg = max(0.2, min(3.8, 1.28 + (ha - ad) / 22 + 0.28 + rng.uniform(-0.18, 0.18)))
    away_xg = max(0.2, min(3.5, 1.12 + (aa - hd) / 22 + rng.uniform(-0.18, 0.18)))
    hg, ag = _poisson(rng, home_xg), _poisson(rng, away_xg)

    possession_home = max(34, min(66, round(50 + (ha - aa) / 4 + rng.randint(-4, 4))))
    shots_home = max(hg + 2, round(home_xg * 5 + rng.randint(3, 7)))
    shots_away = max(ag + 2, round(away_xg * 5 + rng.randint(3, 7)))
    on_home = max(hg, min(shots_home, round(shots_home * rng.uniform(.32, .55))))
    on_away = max(ag, min(shots_away, round(shots_away * rng.uniform(.32, .55))))
    cards_home, cards_away = rng.randint(0, 4), rng.randint(0, 4)
    statistics = {
        "posse_mandante": possession_home, "posse_visitante": 100 - possession_home,
        "finalizacoes_mandante": shots_home, "finalizacoes_visitante": shots_away,
        "finalizacoes_gol_mandante": on_home, "finalizacoes_gol_visitante": on_away,
        "escanteios_mandante": rng.randint(1, 9), "escanteios_visitante": rng.randint(1, 9),
        "cartoes_mandante": cards_home, "cartoes_visitante": cards_away,
        "nota_mandante": round(min(9, 6.2 + hg * .35 - ag * .18 + rng.random() * .5), 1),
        "nota_visitante": round(min(9, 6.2 + ag * .35 - hg * .18 + rng.random() * .5), 1),
    }
    events, scorers = [], []
    minute_pool = sorted(rng.sample(range(5, 90), min(hg + ag, 10)))
    goal_sides = ["home"] * hg + ["away"] * ag
    rng.shuffle(goal_sides)
    attackers = lambda players: [p for p in players if p.get("posicao_principal") != "GOL"] or players
    for minute, side in zip(minute_pool, goal_sides):
        team, players = (home, home_players) if side == "home" else (away, away_players)
        scorer = _name(rng.choice(attackers(players)))
        detail = " de pênalti" if rng.random() < .12 else ""
        events.append((minute, f"{minute}' ⚽ Gol do {team['nome']}! {scorer} marcou{detail}."))
        scorers.append(scorer)
    event_types = [
        ("🟨", "Cartão amarelo", .8), ("🟥", "Cartão vermelho", .1),
        ("🧤", "Grande defesa do goleiro", .55), ("🥅", "Bola na trave", .28),
        ("🔥", "Chance perigosa", .65), ("🩹", "Lesão e atendimento médico", .12),
    ]
    for icon, text, chance in event_types:
        if rng.random() < chance:
            minute = rng.randint(8, 88)
            team = rng.choice([home, away])
            events.append((minute, f"{minute}' {icon} {text} para o {team['nome']}."))
    for players, team in ((home_players, home), (away_players, away)):
        tired = [p for p in players[:11] if float(p.get("condicao_fisica") or 90) < 72]
        bench = [p for p in players[11:] if p.get("posicao_principal")]
        if tired and bench:
            outgoing = rng.choice(tired)
            same = [p for p in bench if p["posicao_principal"] == outgoing["posicao_principal"]] or bench
            incoming = rng.choice(same)
            minute = rng.randint(60, 82)
            events.append((minute, f"{minute}' 🔄 {team['nome']}: sai {_name(outgoing)}, entra {_name(incoming)}."))
    events.extend([(45, "45+2' ⏱️ Fim do primeiro tempo."), (46, "46' ▶️ Começa o segundo tempo."),
                   (94, f"90+4' 🏁 Fim de jogo: {home['nome']} {hg} × {ag} {away['nome']}.")])
    events.sort(key=lambda item: item[0])
    candidates = home_players[:11] + away_players[:11]
    best = _name(max(candidates, key=lambda p: player_rating(p))) if candidates else ""
    return MatchResult(match_id, home["club_id"], away["club_id"], hg, ag,
                       tuple(text for _, text in events), round(ha, 1), round(aa, 1),
                       statistics, tuple(scorers), best)
