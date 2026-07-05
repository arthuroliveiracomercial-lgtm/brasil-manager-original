from .competition_engine import generate_groups, generate_knockout_pairs

COUNTRIES = ["Argentina", "Uruguai", "Chile", "Colômbia", "Equador", "Paraguai", "Peru", "Bolívia"]


def foreign_clubs(prefix, count=24):
    clubs = []
    for index in range(1, count + 1):
        country = COUNTRIES[(index - 1) % len(COUNTRIES)]
        clubs.append({
            "club_id": f"{prefix}{index:03d}", "nome": f"Atlético {country[:3]} {index}",
            "pais": country, "reputacao": 52 + (index * 7) % 28,
            "forca_ofensiva": 50 + (index * 5) % 30, "forca_defensiva": 49 + (index * 6) % 30,
        })
    return clubs


def continental_structure(club_ids, competition_id):
    groups = generate_groups(club_ids, 4)
    knockout = generate_knockout_pairs([clubs[0] for clubs in groups.values() if clubs], competition_id, "OITAVAS")
    return {"grupos": groups, "mata_mata_inicial": knockout}
