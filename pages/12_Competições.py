import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Competições", "Estrutura nacional e continental")
rows = db.query("SELECT * FROM competitions WHERE ativa=1 ORDER BY tipo,divisao,nome")
kind = st.segmented_control("Categoria", ["Todas","liga","copa","estadual","continental"], default="Todas")
shown = rows if kind == "Todas" else [row for row in rows if row["tipo"] == kind]
frame = pd.DataFrame(shown)
styled_table(frame[["nome","tipo","divisao","formato","numero_clubes","fase_atual","promovidos","rebaixados"]].rename(
    columns={"nome":"Competição","tipo":"Tipo","divisao":"Divisão","formato":"Formato","numero_clubes":"Clubes",
             "fase_atual":"Fase","promovidos":"Acessos","rebaixados":"Rebaixados"}))
registrations = db.query(
    "SELECT c.nome,csr.status FROM club_season_registration csr JOIN competitions c "
    "ON c.competition_id=csr.competition_id WHERE csr.club_id=? AND csr.temporada=?",
    (club["club_id"], db.state()["temporada"]),
)
if registrations:
    st.subheader("Competições do seu clube")
    styled_table(pd.DataFrame(registrations))

