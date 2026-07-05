import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Histórico", f"Trajetória do {club['nome']}")
rows = db.query(
    "SELECT sh.temporada,c.nome competicao,sh.posicao,sh.resultado,sh.premio FROM season_history sh "
    "LEFT JOIN competitions c ON c.competition_id=sh.competition_id WHERE sh.club_id=? ORDER BY sh.temporada DESC",
    (club["club_id"],),
)
if rows:
    styled_table(pd.DataFrame(rows))
else:
    st.info("O histórico será preenchido ao encerrar a primeira temporada.")
