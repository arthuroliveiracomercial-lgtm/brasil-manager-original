import json
import streamlit as st

from src.ui import get_database, page_title, require_club

db = get_database(); club = require_club(db)
page_title("Replays", "Reviva partidas já disputadas")
matches = db.query(
    "SELECT c.match_id,c.rodada,c.data,m.nome mandante,v.nome visitante,c.gols_mandante,c.gols_visitante "
    "FROM calendario c JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
    "WHERE c.jogado=1 AND (c.mandante_id=? OR c.visitante_id=?) ORDER BY c.rodada DESC",
    (club["club_id"], club["club_id"]),
)
if not matches:
    st.info("Os replays aparecerão depois da primeira partida.")
    st.stop()
options = {m["match_id"]: m for m in matches}
match_id = st.selectbox("Partida", options, format_func=lambda key: f"R{options[key]['rodada']} · {options[key]['mandante']} {options[key]['gols_mandante']}×{options[key]['gols_visitante']} {options[key]['visitante']}")
match = options[match_id]
st.markdown(f"## {match['mandante']} {match['gols_mandante']} × {match['gols_visitante']} {match['visitante']}")
events = db.query("SELECT evento FROM eventos_partida WHERE match_id=? ORDER BY ordem", (match_id,))
for event in events: st.write(event["evento"])
details = db.query("SELECT * FROM detalhes_partida WHERE match_id=?", (match_id,))
if details:
    with st.expander("Estatísticas"):
        st.json(json.loads(details[0]["estatisticas"]))

