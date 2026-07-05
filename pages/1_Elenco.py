import pandas as pd
import streamlit as st

from src.finance_engine import format_brl, monthly_payroll
from src.match_engine import player_rating
from src.ui import card, condition_label, get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Elenco", f"Gestão esportiva do {club['nome']}")
players = db.query("SELECT * FROM jogadores WHERE clube_id=? ORDER BY posicao_principal,nome", (club["club_id"],))
for p in players:
    p["geral"] = round(player_rating(p)); p["status"] = p.get("status") or "Disponível"
    p["valor"] = format_brl(p["valor_mercado"]); p["salário"] = format_brl(p["salario"])

metrics = st.columns(6)
values = [
    ("Jogadores", len(players)), ("Idade média", f"{sum(p['idade'] for p in players)/len(players):.1f}"),
    ("Maior valor", format_brl(max(p["valor_mercado"] for p in players))),
    ("Folha mensal", format_brl(monthly_payroll(players))),
    ("Lesionados", sum(p["status"] == "Lesionado" for p in players)),
    ("Suspensos", sum(p["status"] == "Suspenso" for p in players)),
]
for col, (label, value) in zip(metrics, values):
    with col: card(label, value)

st.subheader("Filtros")
f1, f2, f3, f4 = st.columns(4)
position = f1.selectbox("Posição", ["Todas"] + sorted({p["posicao_principal"] for p in players}))
age = f2.slider("Idade", 15, 45, (15, 45))
status = f3.selectbox("Status", ["Todos"] + sorted({p["status"] for p in players}))
minimum = f4.slider("Moral e condição mínimas", 0, 100, 0)
shown = [p for p in players if (position == "Todas" or p["posicao_principal"] == position)
         and age[0] <= p["idade"] <= age[1] and (status == "Todos" or p["status"] == status)
         and (p.get("moral") or 0) >= minimum and (p.get("condicao_fisica") or 0) >= minimum]
for p in shown:
    p["Moral"] = f"{p.get('moral') or 0} · {condition_label(p.get('moral') or 0)}"
    p["Condição"] = f"{p.get('condicao_fisica') or 0}% · {condition_label(p.get('condicao_fisica') or 0)}"
frame = pd.DataFrame(shown)
columns = ["nome","idade","posicao_principal","geral","potencial","valor","salário","Moral","Condição","status","contrato_fim"]
frame = frame[columns]; frame.columns = ["Jogador","Idade","Posição","Geral","Potencial","Valor","Salário","Moral","Condição","Status","Contrato"]
styled_table(frame, 650)

