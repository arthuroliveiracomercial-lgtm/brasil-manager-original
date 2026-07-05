from .models import Tactic

MENTALIDADE = {"Defensiva": (-5, 7), "Equilibrada": (0, 0), "Positiva": (5, -2), "Ofensiva": (9, -6)}
ESTILO = {
    "Posse de bola": (3, 2), "Contra-ataque": (4, 1), "Pressão alta": (5, -1),
    "Jogo direto": (3, -1), "Equilibrado": (0, 0),
}

PLAYER_ROLES = {
    "GOL": ["Goleiro Defensivo", "Goleiro Líbero"],
    "ZAG": ["Zagueiro Defensivo", "Zagueiro Construtor", "Zagueiro de Cobertura"],
    "LAT": ["Lateral Defensivo", "Lateral Apoio", "Ala Ofensivo"],
    "ALA": ["Lateral Apoio", "Ala Ofensivo"],
    "VOL": ["Primeiro Volante", "Cão de Guarda", "Construtor Recuado"],
    "MC": ["Meia de Ligação", "Box-to-Box", "Armador"],
    "MEI": ["Camisa 10", "Meia Atacante", "Segundo Atacante"],
    "PE": ["Extremo", "Ponta Invertido", "Atacante de Lado"],
    "PD": ["Extremo", "Ponta Invertido", "Atacante de Lado"],
    "ATA": ["Centroavante", "Atacante Móvel", "Pivô", "Finalizador"],
}

ROLE_EFFECTS = {
    "Goleiro Defensivo": (0, 1.8), "Goleiro Líbero": (0.8, 0.5),
    "Zagueiro Defensivo": (-0.2, 1.6), "Zagueiro Construtor": (1.1, 0.4),
    "Zagueiro de Cobertura": (0, 1.1), "Lateral Defensivo": (-0.5, 1.2),
    "Lateral Apoio": (0.8, 0.3), "Ala Ofensivo": (1.8, -0.9),
    "Primeiro Volante": (-0.2, 1.7), "Cão de Guarda": (0, 1.4),
    "Construtor Recuado": (1.1, 0.5), "Meia de Ligação": (0.8, 0.3),
    "Box-to-Box": (0.8, 0.8), "Armador": (1.7, 0),
    "Camisa 10": (2, -0.2), "Meia Atacante": (1.8, -0.4),
    "Segundo Atacante": (2.1, -0.7), "Extremo": (1.4, 0),
    "Ponta Invertido": (1.8, -0.2), "Atacante de Lado": (1.5, 0.2),
    "Centroavante": (2, 0), "Atacante Móvel": (1.4, 0.4),
    "Pivô": (1.2, 0.6), "Finalizador": (2.2, -0.3),
}


def role_modifiers(roles: list[str] | None) -> tuple[float, float]:
    effects = [ROLE_EFFECTS.get(role, (0, 0)) for role in (roles or [])]
    return sum(x[0] for x in effects) / 4, sum(x[1] for x in effects) / 4


def default_role(position: str) -> str:
    return PLAYER_ROLES.get(position, ["Função Padrão"])[0]


def tactical_summary(tactic: Tactic) -> str:
    parts = [
        f"Seu time jogará com mentalidade **{tactic.mentalidade.lower()}**",
        f"em estilo **{tactic.estilo.lower()}**",
        f"pressão **{tactic.pressao.lower()}** e ritmo **{tactic.ritmo.lower()}**",
        f"com foco **{tactic.foco_ataque.lower()}** e passes **{tactic.tipo_passe.lower()}**.",
    ]
    warning = ""
    if tactic.pressao == "Alta" or tactic.ritmo == "Rápido":
        warning = " A proposta aumenta a intensidade, mas exige boa condição física."
    if tactic.linha_defensiva == "Alta":
        warning += " A linha alta cria volume e deixa espaço para contra-ataques."
    if tactic.foco_ataque in {"Laterais", "Pelas laterais"}:
        warning += " Laterais e pontas terão participação ofensiva maior."
    return " ".join(parts) + warning


def tactic_modifiers(tactic: Tactic) -> tuple[float, float, float]:
    attack, defense = MENTALIDADE.get(tactic.mentalidade, (0, 0))
    style_attack, style_defense = ESTILO.get(tactic.estilo, (0, 0))
    attack += style_attack
    defense += style_defense
    fatigue = 1.0
    if tactic.pressao == "Alta" or tactic.estilo == "Pressão alta":
        attack += 2
        fatigue += 0.35
    elif tactic.pressao == "Baixa":
        defense += 2
        fatigue -= 0.1
    if tactic.linha_defensiva == "Alta":
        attack += 2
        defense -= 2
    elif tactic.linha_defensiva == "Baixa":
        attack -= 2
        defense += 3
    if tactic.ritmo == "Rápido":
        attack += 2
        fatigue += 0.2
    elif tactic.ritmo == "Lento":
        defense += 1
        fatigue -= 0.1
    return attack, defense, fatigue


def compatibility_bonus(tactic: Tactic, players: list[dict]) -> float:
    if not players:
        return 0
    avg = lambda key: sum(float(p.get(key) or 50) for p in players) / len(players)
    if tactic.estilo == "Posse de bola":
        return (avg("passe") + avg("tecnica") - 120) / 12
    if tactic.estilo == "Jogo direto":
        return (avg("forca") + avg("velocidade") - 120) / 12
    if tactic.foco_ataque in {"Pelas laterais", "Laterais"}:
        return (avg("cruzamento") + avg("velocidade") - 120) / 14
    return (avg("trabalho_equipe") - 50) / 12
