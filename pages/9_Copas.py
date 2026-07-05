import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Copas", "Mata-matas nacionais, estaduais e continentais")
competitions = db.query(
    "SELECT * FROM competitions WHERE tipo IN ('copa','estadual','continental') ORDER BY tipo,nome"
)
options = {row["competition_id"]: row for row in competitions}
selected_id = st.selectbox("Competição", options, format_func=lambda key: options[key]["nome"])
competition = options[selected_id]
cols = st.columns(4)
cols[0].metric("Formato", competition["formato"])
cols[1].metric("Fase", competition["fase_atual"])
cols[2].metric("Clubes", competition["numero_clubes"])
cols[3].metric("Premiação", f"R$ {competition['premiacao']:,.0f}".replace(",", "."))
matches = db.query(
    "SELECT cm.*,h.nome mandante,a.nome visitante FROM competition_matches cm "
    "LEFT JOIN clubes h ON h.club_id=cm.mandante_id LEFT JOIN clubes a ON a.club_id=cm.visitante_id "
    "WHERE cm.competition_id=? ORDER BY cm.data,cm.phase_id,cm.match_id", (selected_id,),
)
if matches:
    frame = pd.DataFrame(matches)
    styled_table(frame[["data","phase_id","mandante","gols_mandante","gols_visitante","visitante","perna","status"]].rename(
        columns={"data":"Data","phase_id":"Fase","mandante":"Mandante","gols_mandante":"GM",
                 "gols_visitante":"GV","visitante":"Visitante","perna":"Jogo","status":"Status"}))
else:
    st.info("O sorteio e o calendário desta competição serão gerados quando a fase começar.")

