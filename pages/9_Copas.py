import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table


db = get_database(); club = require_club(db)
page_title("Copas", "Copa do Brasil, Estaduais, Libertadores e Sul-Americana com fases progressivas")

competitions = db.query("SELECT * FROM competitions WHERE tipo IN ('copa','estadual','continental') ORDER BY CASE tipo WHEN 'estadual' THEN 1 WHEN 'copa' THEN 2 ELSE 3 END,nome")
options = {row["competition_id"]: row for row in competitions}
selected_id = st.selectbox("Competição", list(options), format_func=lambda key: options[key]["nome"])
competition = options[selected_id]
cols = st.columns(4)
cols[0].metric("Formato", competition["formato"])
cols[1].metric("Fase atual", competition["fase_atual"])
cols[2].metric("Clubes", competition["numero_clubes"])
cols[3].metric("Premiação", f"R$ {competition['premiacao']:,.0f}".replace(",", "."))

if selected_id in {"LIB", "SULA"}:
    st.info("Nesta versão, o calendário começa na fase de grupos. Mata-mata será sorteado apenas depois que a fase de grupos for concluída.")
elif selected_id == "CDB":
    st.info("A Copa do Brasil começa pela 1ª fase. As fases seguintes são geradas conforme os classificados avançarem.")
elif competition["tipo"] == "estadual":
    st.info("O estadual começa pela fase classificatória. Semifinal e final só aparecem depois da classificação.")

matches = db.query(
    "SELECT cm.*,h.nome mandante,a.nome visitante FROM competition_matches cm "
    "LEFT JOIN clubes h ON h.club_id=cm.mandante_id LEFT JOIN clubes a ON a.club_id=cm.visitante_id "
    "WHERE cm.competition_id=? ORDER BY cm.data,cm.rodada,cm.group_id,cm.match_id", (selected_id,),
)
if matches:
    frame = pd.DataFrame(matches)
    frame["Placar"] = frame.apply(lambda r: "×" if pd.isna(r.get("gols_mandante")) else f"{int(r['gols_mandante'])}×{int(r['gols_visitante'])}", axis=1)
    show = frame[["data","phase_id","group_id","rodada","mandante","Placar","visitante","status"]].rename(
        columns={"data":"Data","phase_id":"Fase","group_id":"Grupo","rodada":"Rodada","mandante":"Mandante","visitante":"Visitante","status":"Status"}
    )
    styled_table(show, height=600)
else:
    st.warning("Nenhum jogo gerado para esta competição.")
