import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club, styled_table


db = get_database(); club = require_club(db)
page_title("Classificação", "Tabelas separadas por competição — sem misturar Séries A, B e C")

league_options = db.query("SELECT competition_id,nome,divisao FROM competicoes WHERE competition_id IN ('COMP001','COMP002','COMP003') ORDER BY divisao")
ids = {row["competition_id"]: row for row in league_options}
default = db.competition_for_club(club["club_id"])
selected = st.segmented_control(
    "Competição", list(ids.keys()),
    format_func=lambda cid: ids[cid]["nome"].replace("Campeonato Brasileiro ", ""),
    default=default if default in ids else list(ids)[0]
)
comp = ids[selected]
st.caption(f"Mostrando somente clubes da {comp['nome']}.")

rows = db.query(
    "SELECT c.nome Clube, cl.pontos Pts, cl.jogos J, cl.vitorias V, cl.empates E, cl.derrotas D, "
    "cl.gols_pro GP, cl.gols_contra GC, cl.saldo SG, c.divisao Série, c.club_id "
    "FROM classificacao cl JOIN clubes c ON c.club_id=cl.club_id "
    "WHERE cl.competition_id=? ORDER BY cl.pontos DESC,cl.vitorias DESC,cl.saldo DESC,cl.gols_pro DESC,c.nome",
    (selected,),
)
if not rows:
    st.warning("Ainda não há classificação para esta competição.")
    st.stop()

df = pd.DataFrame(rows)
df.insert(0, "Pos", range(1, len(df)+1))

def zona(pos):
    if selected == "COMP001":
        if pos <= 6: return "Libertadores"
        if pos <= 12: return "Sul-Americana"
        if pos >= 17: return "Rebaixamento"
    if selected == "COMP002":
        if pos <= 4: return "Acesso"
        if pos >= 17: return "Rebaixamento"
    if selected == "COMP003":
        if pos <= 8: return "2ª fase"
        if pos >= 17: return "Rebaixamento"
    return ""

df["Zona"] = df["Pos"].apply(zona)
df["Seu clube"] = df["club_id"].eq(club["club_id"]).map({True: "⭐", False: ""})
show = df[["Pos", "Seu clube", "Clube", "Série", "Zona", "Pts", "J", "V", "E", "D", "GP", "GC", "SG"]]
styled_table(show, height=620)

if selected == "COMP001":
    st.caption("🟢 Libertadores · 🔵 Sul-Americana · 🔴 Rebaixamento · ⭐ Seu clube")
elif selected == "COMP002":
    st.caption("🟢 Acesso à Série A · 🔴 Rebaixamento · ⭐ Seu clube")
else:
    st.caption("🟢 Classificação para 2ª fase · 🔴 Zona de queda · ⭐ Seu clube")
