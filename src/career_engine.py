from datetime import datetime
from pathlib import Path
import json
import random
import sqlite3
import uuid

from .match_engine import player_rating


def save_training_plan(database, club_id, week, focus, intensity, rest):
    plan_id = f"TR-{club_id}-{week}"
    database.execute(
        "INSERT OR REPLACE INTO training_plans(plan_id,club_id,semana,foco,intensidade,descanso,status)"
        " VALUES(?,?,?,?,?,?,'Planejado')",
        (plan_id, club_id, week, focus, intensity, int(rest)),
    )


def process_training(database, club_id, week):
    plans = database.query("SELECT * FROM training_plans WHERE club_id=? AND semana=?", (club_id, week))
    if not plans:
        return False, "Defina um plano para esta semana."
    plan = plans[0]
    physical_cost = {"Leve": 1, "Normal": 4, "Alta": 8}[plan["intensidade"]]
    morale = 2 if plan["descanso"] else 0
    database.execute(
        "UPDATE jogadores SET condicao_fisica=MAX(35,MIN(100,COALESCE(condicao_fisica,90)-?+?)),"
        "moral=MIN(100,COALESCE(moral,70)+?) WHERE clube_id=?",
        (physical_cost, 6 if plan["descanso"] else 0, morale, club_id),
    )
    database.execute("UPDATE training_plans SET status='Concluído' WHERE plan_id=?", (plan["plan_id"],))
    return True, "Semana de treino processada."


def generate_news(database, club_id, game_date):
    existing = database.query("SELECT 1 FROM news_items WHERE club_id=? AND data=? LIMIT 1", (club_id, game_date))
    if existing:
        return 0
    club = database.query("SELECT nome FROM clubes WHERE club_id=?", (club_id,))[0]["nome"]
    headlines = [
        ("Clube", f"Semana decisiva no {club}", "A comissão prepara o elenco para os próximos compromissos."),
        ("Mercado", "Mercado nacional segue movimentado", "Clubes monitoram oportunidades antes do fechamento da janela."),
        ("Treino", "Preparação física ganha atenção", "A sequência de jogos exige equilíbrio entre intensidade e descanso."),
    ]
    for category, title, content in headlines:
        database.execute(
            "INSERT INTO news_items(news_id,data,categoria,titulo,conteudo,club_id) VALUES(?,?,?,?,?,?)",
            (f"NW-{uuid.uuid4().hex[:10]}", game_date, category, title, content, club_id),
        )
    return len(headlines)


def create_scouting_report(database, club_id, player_id, game_date):
    player = database.query("SELECT * FROM jogadores WHERE player_id=?", (player_id,))[0]
    rng = random.Random(f"{club_id}-{player_id}")
    knowledge = rng.randint(35, 70)
    general = player_rating(player)
    report_id = f"SC-{club_id}-{player_id}"
    recommendation = "Contratar" if general >= 70 else "Acompanhar" if general >= 58 else "Descartar"
    database.execute(
        "INSERT OR REPLACE INTO scouting_reports(report_id,club_id,player_id,data,conhecimento,"
        "nota_estimada,potencial_estimado,recomendacao,status) VALUES(?,?,?,?,?,?,?,?,?)",
        (report_id, club_id, player_id, game_date, knowledge, round(general + rng.uniform(-4,4),1),
         round(float(player.get("potencial") or general) + rng.uniform(-5,5),1), recommendation, "Concluído"),
    )


def create_save_version(database, project_root, name, note=""):
    state = database.state()
    folder = Path(project_root) / "database" / "save_versions"
    folder.mkdir(parents=True, exist_ok=True)
    version_id = f"SV-{datetime.now():%Y%m%d-%H%M%S}"
    destination = folder / f"{version_id}.db"
    with sqlite3.connect(database.path) as source, sqlite3.connect(destination) as target:
        source.backup(target)
    database.execute(
        "INSERT INTO save_versions(version_id,criado_em,nome,temporada,rodada,arquivo,observacao)"
        " VALUES(?,?,?,?,?,?,?)",
        (version_id, datetime.now().isoformat(timespec="seconds"), name, state["temporada"],
         state["rodada_atual"], str(destination), note),
    )
    return destination


def save_rule_preset(database, name, kind, config):
    database.execute(
        "INSERT INTO competition_rule_presets(preset_id,nome,tipo,configuracao,criado_em) VALUES(?,?,?,?,?)",
        (f"RP-{uuid.uuid4().hex[:10]}", name, kind, json.dumps(config, ensure_ascii=False),
         datetime.now().isoformat(timespec="seconds")),
    )
