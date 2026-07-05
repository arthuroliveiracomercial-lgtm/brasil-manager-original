import time

import pandas as pd
import streamlit as st

from src.finance_engine import match_revenue
from src.league_engine import summarize_round
from src.live_match_engine import SPEEDS, event_minute, match_status, simulate_round, snapshot
from src.ui import automatic_lineup, get_database, match_card, page_title, require_club, styled_table, tactic_object

db = get_database()
club = require_club(db)
next_match = db.next_user_match(club["club_id"])
page_title("Central da Rodada", "Todos os jogos, minuto a minuto")

if not next_match:
    st.success("Temporada encerrada. A classificação final já está disponível.")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/6_Classificacao.py", label="🏆 Ver Classificação", use_container_width=True)
    with col2:
        if st.button("▶️ Iniciar próxima temporada", type="primary", width="stretch"):
            new_season = db.advance_season()
            st.cache_resource.clear()
            st.success(f"Temporada {new_season} criada. Boa sorte!")
            st.rerun()
    st.stop()

round_number = next_match["rodada"]
matches = db.query(
    "SELECT c.*,m.nome mandante_nome,v.nome visitante_nome FROM calendario c "
    "JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
    "WHERE c.rodada=? AND c.jogado=0 ORDER BY c.match_id", (round_number,),
)
st.subheader(f"Rodada {round_number} · Brasileirão Série A")
left, center, right = st.columns([1, 1.3, 1])
with left:
    speed = st.radio("Velocidade", ["Instantânea", "Muito rápida", "Rápida", "Normal", "Lenta", "Manual"], index=2)
with center:
    match_card(next_match["mandante_nome"], next_match["visitante_nome"], "×", next_match["data"])
with right:
    saved = db.lineup(club["club_id"])
    st.metric("Escalação", "Pronta" if len(saved) == 11 else "Automática")
    st.caption("Escalação e tática salvas são usadas pelo motor.")

clock_box = st.empty()
scores_box = st.empty()
events_box = st.empty()


def squad(club_id):
    saved = db.lineup(club_id)
    if len(saved) == 11:
        starters, slots = saved, [row["posicao"] for row in saved]
        roles = [row.get("funcao") for row in saved]
    else:
        starters, slots = automatic_lineup(db, club_id)
        roles = [None] * len(starters)
    used = {player["player_id"] for player in starters}
    bench = db.query(
        "SELECT * FROM jogadores WHERE clube_id=? AND COALESCE(status,'Disponível')='Disponível' "
        "ORDER BY condicao_fisica DESC", (club_id,),
    )
    return starters + [player for player in bench if player["player_id"] not in used][:7], slots, roles


def load_context(match):
    home = db.query("SELECT * FROM clubes WHERE club_id=?", (match["mandante_id"],))[0]
    away = db.query("SELECT * FROM clubes WHERE club_id=?", (match["visitante_id"],))[0]
    home_players, home_slots, home_roles = squad(home["club_id"])
    away_players, away_slots, away_roles = squad(away["club_id"])
    _, home_tactic = tactic_object(db, home["club_id"])
    _, away_tactic = tactic_object(db, away["club_id"])
    return {
        "home": home, "away": away, "home_players": home_players, "away_players": away_players,
        "home_slots": home_slots, "away_slots": away_slots, "home_roles": home_roles,
        "away_roles": away_roles, "home_tactic": home_tactic, "away_tactic": away_tactic,
    }


def commit_round(simulations):
    user_result = None
    for item in simulations:
        match, home, away, result = item["match"], item["home"], item["away"], item["result"]
        db.record_match(result, result.events)
        db.add_finance(
            home["club_id"], "Bilheteria", f"Jogo em casa contra {away['nome']}",
            match_revenue(home, result.home_goals, result.away_goals), match["data"],
        )
        if club["club_id"] in (home["club_id"], away["club_id"]):
            user_result = (home, away, result)
    st.session_state["last_round"] = [
        (item["home"]["nome"], item["away"]["nome"], item["result"]) for item in simulations
    ]
    st.session_state["last_user_result"] = user_result
    st.session_state["live_round_status"] = "encerrada"


if st.button("Iniciar Rodada", type="primary", width="stretch"):
    simulations = simulate_round(matches, load_context, db.state()["temporada"])
    if speed == "Manual":
        st.session_state.update(manual_simulations=simulations, manual_minute=0,
                                live_round_status="pausada", live_round_number=round_number)
        st.rerun()
    st.session_state.update(
        live_round_status="simulando", live_round_number=round_number, live_round_minute=0
    )
    delay, step = SPEEDS[speed]
    for minute in range(0, 95, step):
        visible_minute = min(minute, 94)
        live = snapshot(simulations, visible_minute)
        st.session_state["live_round_minute"] = visible_minute
        display_minute = "45+2" if visible_minute == 45 else "90+4" if visible_minute >= 90 else f"{visible_minute:02d}"
        clock_box.markdown(f"## ⏱️ {display_minute}' · {match_status(visible_minute)}")
        rows = []
        for item in simulations:
            match, home, away = item["match"], item["home"], item["away"]
            score = live["scores"][match["match_id"]]
            rows.append({
                "Jogo": f"{home['nome']}  {score['home']} × {score['away']}  {away['nome']}",
                "Status": score["status"],
                "Seu jogo": "●" if club["club_id"] in (home["club_id"], away["club_id"]) else "",
            })
        scores_box.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        events_box.markdown("#### Eventos\n" + (
            "\n\n".join(f"- {event}" for event in live["events"][-8:]) or "_A bola está rolando..._"
        ))
        if delay:
            time.sleep(delay)

    commit_round(simulations)
    st.success("Rodada encerrada. Classificação e finanças atualizadas.")

manual = st.session_state.get("manual_simulations")
if manual and st.session_state.get("live_round_number") == round_number:
    minute = st.session_state.get("manual_minute", 0)
    live = snapshot(manual, minute)
    clock_box.markdown(f"## ⏸️ {minute:02d}' · {match_status(minute)}")
    rows = []
    for item in manual:
        score = live["scores"][item["match"]["match_id"]]
        rows.append({"Jogo": f"{item['home']['nome']} {score['home']} × {score['away']} {item['away']['nome']}",
                     "Status": score["status"]})
    scores_box.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    events_box.markdown("#### Eventos\n" + ("\n\n".join(f"- {event}" for event in live["events"][-8:]) or "_Partida pausada._"))
    st.subheader("Controle manual")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Avançar 1 minuto"): st.session_state["manual_minute"] = min(94, minute + 1); st.rerun()
    if c2.button("Próximo lance"):
        future = sorted({event_minute(event) for item in manual for event in item["result"].events
                         if event_minute(event) > minute})
        st.session_state["manual_minute"] = future[0] if future else 94; st.rerun()
    if c3.button("Até o intervalo"): st.session_state["manual_minute"] = max(minute, 45); st.rerun()
    if c4.button("Até o fim"):
        st.session_state["manual_minute"] = 94
        commit_round(manual)
        del st.session_state["manual_simulations"]
        st.success("Rodada encerrada."); st.rerun()
    user_item = next(item for item in manual if club["club_id"] in (item["home"]["club_id"], item["away"]["club_id"]))
    user_players = user_item["home_players"] if user_item["home"]["club_id"] == club["club_id"] else user_item["away_players"]
    with st.expander("Substituição manual e plano rápido"):
        starters, bench = user_players[:11], user_players[11:]
        outgoing = st.selectbox("Sai", [p["player_id"] for p in starters], format_func=lambda pid: next(p["nome"] for p in starters if p["player_id"] == pid))
        incoming = st.selectbox("Entra", [p["player_id"] for p in bench], format_func=lambda pid: next(p["nome"] for p in bench if p["player_id"] == pid))
        if st.button("Confirmar substituição", disabled=minute == 0):
            used = db.query("SELECT COUNT(*) n FROM match_substitutions WHERE match_id=? AND club_id=?",
                            (user_item["match"]["match_id"], club["club_id"]))[0]["n"]
            if used >= 5: st.error("Limite de cinco substituições atingido.")
            else:
                db.execute("INSERT INTO match_substitutions(match_id,club_id,minuto,player_out_id,player_in_id) VALUES(?,?,?,?,?)",
                           (user_item["match"]["match_id"], club["club_id"], minute, outgoing, incoming))
                st.success("Substituição registrada.")
        plan = st.segmented_control("Plano de jogo", ["Segurar resultado","Buscar gol","Contra-atacar","Controlar posse","Pressão final"])
        if st.button("Aplicar plano", disabled=not plan):
            db.execute("INSERT INTO in_match_tactical_changes(match_id,club_id,minuto,campo,valor_novo) VALUES(?,?,?,?,?)",
                       (user_item["match"]["match_id"], club["club_id"], minute, "plano_rapido", plan))
            st.success(f"Plano aplicado: {plan}.")

last_user = st.session_state.get("last_user_result")
if last_user:
    home, away, result = last_user
    st.divider()
    match_card(home["nome"], away["nome"], f"{result.home_goals} × {result.away_goals}", "Encerrado")
    stats = result.statistics
    styled_table(pd.DataFrame([
        ["Posse", f"{stats['posse_mandante']}%", f"{stats['posse_visitante']}%"],
        ["Finalizações", stats["finalizacoes_mandante"], stats["finalizacoes_visitante"]],
        ["No gol", stats["finalizacoes_gol_mandante"], stats["finalizacoes_gol_visitante"]],
        ["Escanteios", stats["escanteios_mandante"], stats["escanteios_visitante"]],
        ["Cartões", stats["cartoes_mandante"], stats["cartoes_visitante"]],
        ["Nota média", stats["nota_mandante"], stats["nota_visitante"]],
    ], columns=["Estatística", home["nome"], away["nome"]]))
    st.info(f"⭐ Melhor jogador: {result.best_player}")
    with st.expander("Eventos detalhados", expanded=True):
        for event in result.events:
            st.write(event)

last_round = st.session_state.get("last_round")
if last_round:
    st.subheader("Resumo da rodada")
    highlight = summarize_round(last_round)
    cols = st.columns(2)
    cols[0].metric("Maior goleada", highlight["maior_goleada"])
    cols[1].metric("Melhor jogador", highlight["melhor_jogador"])
    styled_table(pd.DataFrame([
        {"Jogo": f"{home} {result.home_goals} × {result.away_goals} {away}"}
        for home, away, result in last_round
    ]))
    if highlight["artilheiros"]:
        st.caption("Gols da rodada: " + " · ".join(highlight["artilheiros"]))
    buttons = st.columns(3)
    buttons[0].link_button("Ver Classificação", "/Classificacao", width="stretch")
    buttons[1].link_button("Próxima Partida", "/Partida", width="stretch")
    buttons[2].link_button("Voltar ao Início", "/", width="stretch")
