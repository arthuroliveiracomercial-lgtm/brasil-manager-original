import streamlit as st

from src.match_engine import player_rating
from src.models import FORMATIONS
from src.tactic_engine import PLAYER_ROLES, default_role
from src.ui import automatic_lineup, get_database, page_title, render_pitch, require_club

db = get_database()
club = require_club(db)
page_title("Escalação", f"{club['nome']} · monte o time e distribua funções")

tactic = db.get_tactic(club["club_id"])
formations = list(FORMATIONS)
formation = st.segmented_control("Formação", formations, default=tactic["formacao"]) or tactic["formacao"]
slots = FORMATIONS[formation]
players = db.query("SELECT * FROM jogadores WHERE clube_id=? ORDER BY posicao_principal,nome", (club["club_id"],))
by_id = {p["player_id"]: p for p in players}
saved = db.lineup(club["club_id"])
saved_ids = [row["player_id"] for row in saved] if len(saved) == 11 and formation == tactic["formacao"] else []
saved_roles = [row.get("funcao") for row in saved] if saved_ids else []
if not saved_ids:
    auto, _ = automatic_lineup(db, club["club_id"], formation)
    saved_ids = [p["player_id"] for p in auto]

chosen, roles = [], []
st.subheader("Escolha dos titulares")
left, right = st.columns(2)
for index, slot in enumerate(slots):
    column = left if index % 2 == 0 else right
    available = [p for p in players if p["player_id"] not in chosen]
    default_id = saved_ids[index] if index < len(saved_ids) and saved_ids[index] not in chosen else available[0]["player_id"]
    options = [p["player_id"] for p in available]
    with column:
        selection = st.selectbox(
            f"{index + 1}. {slot}", options, index=options.index(default_id) if default_id in options else 0,
            format_func=lambda pid, s=slot: f"{by_id[pid]['nome']} · {by_id[pid]['posicao_principal']} · {player_rating(by_id[pid], s):.0f}",
            key=f"player_{formation}_{index}",
        )
        role_options = PLAYER_ROLES.get(slot, [default_role(slot)])
        prior = saved_roles[index] if index < len(saved_roles) and saved_roles[index] in role_options else default_role(slot)
        role = st.selectbox("Função", role_options, index=role_options.index(prior), key=f"role_{formation}_{index}")
    chosen.append(selection); roles.append(role)

selected_players = [by_id[player_id] for player_id in chosen]
st.subheader("Campo")
render_pitch(formation, slots, selected_players, roles)
average = sum(player_rating(by_id[pid], slots[i]) for i, pid in enumerate(chosen)) / 11
off_position = sum(by_id[pid]["posicao_principal"] not in {slots[i]} and slots[i] not in str(by_id[pid].get("posicoes_secundarias") or "") for i, pid in enumerate(chosen))
cols = st.columns(3)
cols[0].metric("Nota estimada", f"{average:.1f}")
cols[1].metric("Fora de posição", off_position)
cols[2].metric("Condição média", f"{sum((p.get('condicao_fisica') or 90) for p in selected_players)/11:.0f}%")
if st.button("Salvar Escalação", type="primary", width="stretch"):
    db.save_lineup(club["club_id"], formation, slots, chosen, roles)
    st.success("Escalação e funções salvas.")

