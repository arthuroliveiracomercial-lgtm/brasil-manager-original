import time
import pandas as pd
import streamlit as st

from src.finance_engine import match_revenue
from src.live_match_engine import SPEEDS, event_minute, match_status, simulate_round, snapshot
from src.match_engine import player_rating
from src.tactic_engine import automatic_lineup, tactic_object
from src.ui import get_database, match_card, mobile_nav, page_title, require_club, styled_table


db = get_database(); club = require_club(db); mobile_nav()
state = db.state()
league_comp = db.competition_for_club(club["club_id"])
next_match = db.next_user_match(club["club_id"])
if not next_match:
    page_title("Central da Rodada", "Temporada encerrada")
    st.success("A temporada da sua divisão terminou. Confira a classificação ou inicie a próxima temporada na tela inicial.")
    st.page_link("pages/6_Classificacao.py", label="Ver classificação", icon="🏆")
    st.stop()
round_number = next_match["rodada"]
comp_name = next_match.get("competition_nome") or db.query("SELECT nome FROM competicoes WHERE competition_id=?", (league_comp,))[0]["nome"]
page_title("Central da Rodada", f"{comp_name} · rodada {round_number} · estilo manager clássico")

matches = db.query(
    "SELECT c.*,co.nome competition_nome,m.nome mandante_nome,v.nome visitante_nome FROM calendario c "
    "JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
    "LEFT JOIN competicoes co ON co.competition_id=c.competition_id "
    "WHERE c.competition_id=? AND c.rodada=? AND c.jogado=0 ORDER BY c.match_id",
    (league_comp, round_number),
)
if not matches:
    st.info("Não há jogos pendentes nesta rodada.")
    st.stop()

SLOTS_LABELS = {"GOL":"Goleiro", "ZAG":"Zagueiro", "LAT":"Lateral", "VOL":"Volante", "MC":"Meia", "MEI":"Meia of.", "PE":"Ponta", "PD":"Ponta", "ATA":"Atacante"}

def squad(club_id):
    saved = db.lineup(club_id)
    if len(saved) == 11:
        starters, slots = saved, [row["posicao"] for row in saved]
        roles = [row.get("funcao") or "Padrão" for row in saved]
    else:
        starters, slots = automatic_lineup(db, club_id)
        roles = ["Padrão"] * len(starters)
    used = {player["player_id"] for player in starters}
    bench = db.query(
        "SELECT * FROM jogadores WHERE clube_id=? AND COALESCE(status,'Disponível')='Disponível' ORDER BY condicao_fisica DESC,reputacao DESC",
        (club_id,),
    )
    return starters + [player for player in bench if player["player_id"] not in used][:9], slots, roles


def load_context(match):
    home = db.query("SELECT * FROM clubes WHERE club_id=?", (match["mandante_id"],))[0]
    away = db.query("SELECT * FROM clubes WHERE club_id=?", (match["visitante_id"],))[0]
    home_players, home_slots, home_roles = squad(home["club_id"])
    away_players, away_slots, away_roles = squad(away["club_id"])
    _, home_tactic = tactic_object(db, home["club_id"])
    _, away_tactic = tactic_object(db, away["club_id"])
    return {"home": home, "away": away, "home_players": home_players, "away_players": away_players,
            "home_slots": home_slots, "away_slots": away_slots, "home_roles": home_roles,
            "away_roles": away_roles, "home_tactic": home_tactic, "away_tactic": away_tactic}


def commit_round(simulations):
    user_result = None
    for item in simulations:
        match, home, away, result = item["match"], item["home"], item["away"], item["result"]
        try:
            db.record_match(result, result.events)
            db.add_finance(home["club_id"], "Bilheteria", f"{match['competition_nome']}: {away['nome']}",
                           match_revenue(home, result.home_goals, result.away_goals), match["data"])
        except Exception:
            pass
        if club["club_id"] in (home["club_id"], away["club_id"]):
            user_result = (home, away, result)
    st.session_state["last_round"] = [(item["home"]["nome"], item["away"]["nome"], item["result"]) for item in simulations]
    st.session_state["last_user_result"] = user_result
    st.session_state.pop("manual_simulations", None)


def live_rows(simulations, minute):
    live = snapshot(simulations, minute)
    rows = []
    for item in simulations:
        score = live["scores"][item["match"]["match_id"]]
        rows.append({
            "Campeonato": item["match"].get("competition_nome") or comp_name,
            "Jogo": f"{item['home']['nome']} {score['home']} × {score['away']} {item['away']['nome']}",
            "Status": score["status"],
            "Seu jogo": "⭐" if club["club_id"] in (item["home"]["club_id"], item["away"]["club_id"]) else "",
        })
    return live, rows

main_match = next(m for m in matches if club["club_id"] in (m["mandante_id"], m["visitante_id"]))
left, center, right = st.columns([.85, 1.4, 1.1])
with left:
    st.markdown('<div class="retro-panel"><div class="retro-title">Controle</div>', unsafe_allow_html=True)
    speed = st.radio("Velocidade", ["Manual", "Lenta", "Normal", "Rápida", "Muito rápida", "Instantânea"], index=2)
    st.caption("Use Manual para mexer no time durante o jogo.")
    st.markdown('</div>', unsafe_allow_html=True)
with center:
    match_card(main_match["mandante_nome"], main_match["visitante_nome"], "×", f"{comp_name} · rodada {round_number}")
with right:
    saved = db.lineup(club["club_id"])
    tactic = db.get_tactic(club["club_id"])
    st.markdown('<div class="retro-panel"><div class="retro-title">Seu banco</div>', unsafe_allow_html=True)
    st.write(f"**Escalação:** {'salva' if len(saved)==11 else 'automática'}")
    st.write(f"**Tática:** {tactic['formacao']} · {tactic['mentalidade']} · {tactic['ritmo']}")
    st.page_link("pages/2_Escalacao.py", label="Editar escalação antes do jogo", icon="📋")
    st.markdown('</div>', unsafe_allow_html=True)

clock_box = st.empty()
scores_box = st.empty()
events_box = st.empty()
controls_box = st.empty()

if st.button("▶️ Iniciar rodada", type="primary", width="stretch"):
    simulations = simulate_round(matches, load_context, state["temporada"])
    if speed == "Manual":
        st.session_state.update(manual_simulations=simulations, manual_minute=0, live_round_number=round_number)
        st.rerun()
    delay, step = SPEEDS[speed]
    for minute in range(0, 95, step):
        visible = min(minute, 94)
        live, rows = live_rows(simulations, visible)
        clock_box.markdown(f"## ⏱️ {visible:02d}' · {match_status(visible)}")
        scores_box.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=340)
        events_box.markdown("#### Lances da rodada\n" + ("\n\n".join(f"- {e}" for e in live["events"][-12:]) or "_A bola está rolando..._"))
        if delay:
            time.sleep(delay)
    commit_round(simulations)
    st.success("Rodada encerrada. Classificação atualizada na competição correta.")
    st.rerun()

manual = st.session_state.get("manual_simulations")
if manual and st.session_state.get("live_round_number") == round_number:
    minute = st.session_state.get("manual_minute", 0)
    live, rows = live_rows(manual, minute)
    clock_box.markdown(f"## {'⏸️' if minute < 94 else '🏁'} {minute:02d}' · {match_status(minute)}")
    scores_box.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=330)
    events_box.markdown("#### Lances\n" + ("\n\n".join(f"- {event}" for event in live["events"][-12:]) or "_Partida pausada._"))
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("+1 min"):
        st.session_state["manual_minute"] = min(94, minute + 1); st.rerun()
    if c2.button("Próximo lance"):
        future = sorted({event_minute(event) for item in manual for event in item["result"].events if event_minute(event) > minute})
        st.session_state["manual_minute"] = future[0] if future else 94; st.rerun()
    if c3.button("Intervalo"):
        st.session_state["manual_minute"] = max(minute, 45); st.rerun()
    if c4.button("Fim"):
        st.session_state["manual_minute"] = 94; st.rerun()
    if c5.button("Encerrar e salvar", type="primary", disabled=minute < 90):
        commit_round(manual); st.success("Rodada salva."); st.rerun()

    user_item = next(item for item in manual if club["club_id"] in (item["home"]["club_id"], item["away"]["club_id"]))
    user_players = user_item["home_players"] if user_item["home"]["club_id"] == club["club_id"] else user_item["away_players"]
    starters, bench = user_players[:11], user_players[11:]
    st.subheader("Mexer no time durante o jogo")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Substituições**")
        out = st.selectbox("Sai", [p["player_id"] for p in starters], format_func=lambda pid: next(f"{p['nome']} · {p['posicao_principal']} · {player_rating(p):.0f}" for p in starters if p["player_id"]==pid))
        inc = st.selectbox("Entra", [p["player_id"] for p in bench], format_func=lambda pid: next(f"{p['nome']} · {p['posicao_principal']} · {player_rating(p):.0f}" for p in bench if p["player_id"]==pid))
        if st.button("Confirmar substituição", disabled=minute == 0):
            used = db.query("SELECT COUNT(*) n FROM match_substitutions WHERE match_id=? AND club_id=?", (user_item["match"]["match_id"], club["club_id"]))[0]["n"]
            if used >= 5:
                st.error("Limite de cinco substituições atingido.")
            else:
                db.execute("INSERT INTO match_substitutions(match_id,club_id,minuto,player_out_id,player_in_id) VALUES(?,?,?,?,?)", (user_item["match"]["match_id"], club["club_id"], minute, out, inc))
                st.success("Substituição registrada no replay da partida.")
    with t2:
        st.markdown("**Plano rápido**")
        plan = st.radio("Plano", ["Segurar resultado", "Buscar gol", "Contra-atacar", "Controlar posse", "Pressão final"], horizontal=False)
        if st.button("Aplicar plano", disabled=minute == 0):
            db.execute("INSERT INTO in_match_tactical_changes(match_id,club_id,minuto,campo,valor_novo) VALUES(?,?,?,?,?)", (user_item["match"]["match_id"], club["club_id"], minute, "plano_rapido", plan))
            st.success(f"Plano aplicado aos {minute}'.")

last_user = st.session_state.get("last_user_result")
if last_user:
    home, away, result = last_user
    st.divider(); match_card(home["nome"], away["nome"], f"{result.home_goals} × {result.away_goals}", "Encerrado")
    stats = result.statistics
    styled_table(pd.DataFrame([
        ["Posse", f"{stats['posse_mandante']}%", f"{stats['posse_visitante']}%"],
        ["Finalizações", stats["finalizacoes_mandante"], stats["finalizacoes_visitante"]],
        ["No gol", stats["finalizacoes_gol_mandante"], stats["finalizacoes_gol_visitante"]],
        ["Escanteios", stats["escanteios_mandante"], stats["escanteios_visitante"]],
        ["Cartões", stats["cartoes_mandante"], stats["cartoes_visitante"]],
    ], columns=["Estatística", home["nome"], away["nome"]]))
