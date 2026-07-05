import pandas as pd
import streamlit as st

from src.career_engine import create_scouting_report
from src.finance_engine import format_brl
from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Olheiros", "Observe antes de investir")
position = st.selectbox("Posição", ["Todas","GOL","ZAG","LAT","ALA","VOL","MC","MEI","PE","PD","ATA"])
query = "SELECT j.player_id,j.nome,j.idade,j.posicao_principal,j.valor_mercado,c.nome clube FROM jogadores j JOIN clubes c ON c.club_id=j.clube_id WHERE j.clube_id<>?"
params = [club["club_id"]]
if position != "Todas": query += " AND j.posicao_principal=?"; params.append(position)
candidates = db.query(query + " ORDER BY j.valor_mercado DESC LIMIT 80", tuple(params))
options = {p["player_id"]: p for p in candidates}
player_id = st.selectbox("Jogador", options, format_func=lambda key: f"{options[key]['nome']} · {options[key]['clube']}")
selected = options[player_id]
st.caption(f"{selected['idade']} anos · {selected['posicao_principal']} · {format_brl(selected['valor_mercado'])}")
if st.button("Solicitar Relatório", type="primary", width="stretch"):
    create_scouting_report(db, club["club_id"], player_id, db.state().get("data_atual") or "2026-01-01")
    st.success("Relatório concluído.")
reports = db.query(
    "SELECT sr.data,j.nome,j.posicao_principal,sr.conhecimento,sr.nota_estimada,sr.potencial_estimado,"
    "sr.recomendacao FROM scouting_reports sr JOIN jogadores j ON j.player_id=sr.player_id "
    "WHERE sr.club_id=? ORDER BY sr.data DESC", (club["club_id"],))
if reports: styled_table(pd.DataFrame(reports))

