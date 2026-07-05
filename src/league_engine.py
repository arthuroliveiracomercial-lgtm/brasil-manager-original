from datetime import date, timedelta


def round_robin(club_ids: list[str], competition_id: str = "COMP001", start: date | None = None) -> list[dict]:
    teams = list(club_ids)
    if len(teams) % 2:
        teams.append(None)
    start = start or date.today() + timedelta(days=7)
    first_leg = []
    rotation = teams[:]
    rounds = len(teams) - 1
    half = len(teams) // 2
    for round_index in range(rounds):
        pairs = list(zip(rotation[:half], reversed(rotation[half:])))
        for game_index, (home, away) in enumerate(pairs):
            if home and away:
                if round_index % 2 and game_index == 0:
                    home, away = away, home
                first_leg.append({
                    "match_id": f"{competition_id}-R{round_index + 1:02d}-J{game_index + 1:02d}",
                    "competition_id": competition_id, "rodada": round_index + 1,
                    "data": (start + timedelta(days=7 * round_index)).isoformat(),
                    "mandante_id": home, "visitante_id": away, "estadio": None,
                    "jogado": 0, "gols_mandante": None, "gols_visitante": None,
                })
        rotation = [rotation[0], rotation[-1], *rotation[1:-1]]
    second_leg = []
    for match in first_leg:
        clone = match.copy()
        clone["rodada"] += rounds
        clone["match_id"] = clone["match_id"].replace(
            f"R{match['rodada']:02d}", f"R{clone['rodada']:02d}"
        )
        clone["data"] = (date.fromisoformat(match["data"]) + timedelta(days=7 * rounds)).isoformat()
        clone["mandante_id"], clone["visitante_id"] = match["visitante_id"], match["mandante_id"]
        second_leg.append(clone)
    return first_leg + second_leg


def empty_standing(club_ids: list[str], competition_id: str = "COMP001") -> list[dict]:
    return [{"competition_id": competition_id, "club_id": club_id, "jogos": 0, "vitorias": 0,
             "empates": 0, "derrotas": 0, "gols_pro": 0, "gols_contra": 0, "saldo": 0, "pontos": 0}
            for club_id in club_ids]


def summarize_round(results: list[tuple[str, str, object]]) -> dict:
    """Cria destaques compactos sem depender da interface."""
    if not results:
        return {"maior_goleada": "—", "melhor_jogador": "—", "artilheiros": []}
    biggest = max(results, key=lambda item: abs(item[2].home_goals - item[2].away_goals))
    home, away, result = biggest
    scorers = [name for _, _, match in results for name in match.scorers]
    return {
        "maior_goleada": f"{home} {result.home_goals} × {result.away_goals} {away}",
        "melhor_jogador": next((match.best_player for _, _, match in results if match.best_player), "—"),
        "artilheiros": scorers[:5],
    }
