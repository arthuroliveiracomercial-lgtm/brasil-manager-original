import pandas as pd
import streamlit as st

from src.finance_engine import format_brl, monthly_payroll
from src.match_engine import player_rating
from src.transfer_engine import active_transfer_window, evaluate_offer, transfer_record
from src.ui import card, get_database, page_title, require_club, styled_table

db = get_database()
club = require_club(db)
page_title("Transferências", "Mercado nacional")
game_date = db.state().get("data_atual") or "2026-01-01"
window = active_transfer_window(db, game_date)
if window:
    st.success(f"{window['nome']} aberta até {window['data_fim']}.")
else:
    st.warning("A janela de transferências está fechada. Você pode observar jogadores, mas não registrar novos atletas.")
own_players = db.query("SELECT salario FROM jogadores WHERE clube_id=?", (club["club_id"],))
payroll = monthly_payroll(own_players)
top = st.columns(3)
with top[0]: card("Orçamento", format_brl(club["orcamento_transferencias"]), "Disponível para compras", "#34D399")
with top[1]: card("Folha atual", format_brl(payroll), "Salários mensais", "#3B82F6")
with top[2]: card("Espaço na folha", format_brl(max(0, club["folha_salarial_maxima"] - payroll)), "Para novos contratos", "#F4B942")

st.subheader("Buscar jogadores")
f1, f2, f3, f4 = st.columns(4)
position = f1.selectbox("Posição", ["Todas", "GOL", "ZAG", "LAT", "ALA", "VOL", "MC", "MEI", "PE", "PD", "ATA"])
age = f2.slider("Idade", 15, 42, (15, 35))
max_value = f3.number_input("Valor máximo", min_value=100_000, value=int(max(100_000, club["orcamento_transferencias"])), step=500_000)
max_salary = f4.number_input("Salário máximo", min_value=1_000, value=int(max(1_000, club["folha_salarial_maxima"] - payroll)), step=10_000)
where = "j.clube_id<>? AND j.valor_mercado<=? AND j.salario<=? AND j.idade BETWEEN ? AND ?"
params = [club["club_id"], max_value, max_salary, age[0], age[1]]
if position != "Todas":
    where += " AND j.posicao_principal=?"; params.append(position)
players = db.query(
    "SELECT j.*,c.nome clube_nome FROM jogadores j JOIN clubes c ON c.club_id=j.clube_id "
    f"WHERE {where} ORDER BY j.valor_mercado DESC LIMIT 100", tuple(params),
)
for player in players:
    player["geral"] = round(player_rating(player))
    player["valor_formatado"] = format_brl(player["valor_mercado"])
    player["salario_formatado"] = format_brl(player["salario"])
frame = pd.DataFrame(players)
if frame.empty:
    st.info("Nenhum jogador encontrado com esses filtros.")
    st.stop()
styled_table(frame[["nome","idade","posicao_principal","geral","clube_nome","valor_formatado","salario_formatado"]].rename(
    columns={"nome":"Jogador","idade":"Idade","posicao_principal":"Posição","geral":"Geral",
             "clube_nome":"Clube","valor_formatado":"Valor","salario_formatado":"Salário"}
))
options = {player["player_id"]: player for player in players}
selected_id = st.selectbox("Jogador", options, format_func=lambda pid: f"{options[pid]['nome']} · {options[pid]['clube_nome']}")
selected = options[selected_id]
left, right = st.columns(2)
offer = left.number_input("Valor da proposta", min_value=0.0, value=float(selected["valor_mercado"]), step=100_000.0)
salary = right.number_input("Salário mensal", min_value=0.0, value=float(selected["salario"] * 1.1), step=5_000.0)
buy, loan = st.columns(2)
if buy.button("Comprar", type="primary", width="stretch", disabled=not bool(window)):
    accepted, message = evaluate_offer(selected, club, offer, salary)
    if accepted:
        db.complete_transfer(transfer_record(selected_id, selected["clube_id"], club["club_id"], offer, salary))
        st.success("Contratação concluída."); st.rerun()
    else: st.error(message)
if loan.button("Empréstimo", width="stretch", disabled=not bool(window)):
    loan_fee = max(0, selected["valor_mercado"] * .1)
    accepted, message = evaluate_offer(selected, club, max(loan_fee, selected["valor_mercado"] * .8), salary)
    if accepted:
        db.complete_transfer(transfer_record(selected_id, selected["clube_id"], club["club_id"], loan_fee, salary, "EMPRESTIMO"))
        st.success("Empréstimo concluído para a temporada."); st.rerun()
    else: st.error(message)
