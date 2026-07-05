import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
next_match = db.next_user_match(club["club_id"])
current_round = next_match["rodada"] if next_match else 38
page_title("Calendário", f"Temporada 2026 · rodada atual {current_round}")
scope = st.segmented_control("Exibir", ["Meu clube", "Todos os jogos"], default="Meu clube")
where, params = ("WHERE c.mandante_id=? OR c.visitante_id=?", (club["club_id"], club["club_id"])) if scope == "Meu clube" else ("", ())
rows = db.query(
    "SELECT c.rodada,c.data,m.nome mandante,v.nome visitante,c.mandante_id,c.visitante_id,c.jogado,c.gols_mandante,c.gols_visitante "
    "FROM calendario c JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
    f"{where} ORDER BY c.rodada,m.nome", params)
rounds = sorted({row["rodada"] for row in rows})
selected = st.selectbox("Rodada", rounds, index=rounds.index(current_round) if current_round in rounds else 0)
shown = [r for r in rows if r["rodada"] == selected]
for row in shown:
    row["Placar"] = f"{row['gols_mandante']} × {row['gols_visitante']}" if row["jogado"] else "—"
    row["Status"] = "Encerrado" if row["jogado"] else "Próximo" if selected == current_round else "Pendente"
    row["Destaque"] = "★ Seu jogo" if club["club_id"] in (row["mandante_id"], row["visitante_id"]) else ""
frame = pd.DataFrame(shown)[["data","mandante","Placar","visitante","Status","Destaque"]]
frame.columns = ["Data","Mandante","Placar","Visitante","Status",""]
styled_table(frame)
if selected == current_round:
    st.link_button("▶️ Ir para esta Partida", "/5_Partida", width="stretch")
