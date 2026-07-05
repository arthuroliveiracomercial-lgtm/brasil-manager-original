import pandas as pd
import streamlit as st

from src.ui import get_database, page_title, require_club

db = get_database(); club = require_club(db)
page_title("Classificação", "Brasileirão Série A · pontos corridos")
rows = db.query(
    "SELECT cl.club_id,cl.nome,c.jogos,c.vitorias,c.empates,c.derrotas,c.gols_pro,c.gols_contra,c.saldo,c.pontos "
    "FROM classificacao c JOIN clubes cl ON cl.club_id=c.club_id "
    "ORDER BY c.pontos DESC,c.vitorias DESC,c.saldo DESC,c.gols_pro DESC,cl.nome")
for i, row in enumerate(rows, 1):
    row["Pos"] = i
    row["Zona"] = "Libertadores" if i <= 6 else "Sul-Americana" if i <= 12 else "Rebaixamento" if i >= 17 else ""
    row["Aproveitamento"] = f"{(row['pontos']/(row['jogos']*3)*100 if row['jogos'] else 0):.0f}%"
    row["Clube"] = ("★ " if row["club_id"] == club["club_id"] else "") + row["nome"]
frame = pd.DataFrame(rows)[["Pos","Clube","Zona","pontos","jogos","vitorias","empates","derrotas","gols_pro","gols_contra","saldo","Aproveitamento"]]
frame.columns = ["Pos","Clube","Zona","Pts","J","V","E","D","GP","GC","SG","Aprov."]
def color_zone(row):
    if row["Zona"] == "Libertadores": color = "background-color:#DDF7EF"
    elif row["Zona"] == "Sul-Americana": color = "background-color:#E8F1FF"
    elif row["Zona"] == "Rebaixamento": color = "background-color:#FFE7E7"
    else: color = ""
    if row["Clube"].startswith("★"): color = "background-color:#FFF3C4;font-weight:bold"
    return [color] * len(row)
st.dataframe(frame.style.apply(color_zone, axis=1), width="stretch", hide_index=True, height=720)
st.caption("🟢 Libertadores · 🔵 Sul-Americana · 🔴 Rebaixamento · ⭐ Seu clube")

