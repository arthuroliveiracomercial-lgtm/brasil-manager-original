import re

from .match_engine import simulate_match

SPEEDS = {
    "Instantânea": (0.0, 95),
    "Muito rápida": (0.008, 5),
    "Rápida": (0.018, 3),
    "Normal": (0.045, 2),
    "Lenta": (0.075, 1),
    "Manual": (0.0, 1),
}


def event_minute(text):
    found = re.match(r"(\d+)", text)
    return int(found.group(1)) if found else 0


def match_status(minute):
    if minute < 45:
        return "1º tempo"
    if minute == 45:
        return "Intervalo"
    if minute < 90:
        return "2º tempo"
    return "Encerrado"


def simulate_round(matches, context_loader, season=2026):
    simulations = []
    for match in matches:
        context = context_loader(match)
        result = simulate_match(
            match["match_id"], context["home"], context["away"],
            context["home_players"], context["away_players"],
            context["home_slots"], context["away_slots"],
            context["home_tactic"], context["away_tactic"],
            seed=f"{season}-{match['match_id']}",
            home_roles=context["home_roles"], away_roles=context["away_roles"],
        )
        simulations.append({**context, "match": match, "result": result})
    return simulations


def snapshot(simulations, minute):
    scores, events = {}, []
    for item in simulations:
        result, home, away = item["result"], item["home"], item["away"]
        home_goals = away_goals = 0
        game_events = []
        for event in result.events:
            if event_minute(event) <= minute:
                game_events.append(event)
                events.append(event)
                if "⚽" in event:
                    if home["nome"] in event:
                        home_goals += 1
                    elif away["nome"] in event:
                        away_goals += 1
        scores[item["match"]["match_id"]] = {
            "home": home_goals, "away": away_goals, "status": match_status(minute),
            "events": game_events,
        }
    return {"minute": minute, "status": match_status(minute), "scores": scores, "events": events}
