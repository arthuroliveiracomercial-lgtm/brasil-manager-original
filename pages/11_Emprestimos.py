from datetime import date, timedelta
import pandas as pd
import streamlit as st

from src.finance_engine import format_brl, request_financial_loan
from src.transfer_engine import create_player_loan
from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Empréstimos", "Jogadores e crédito bancário")
player_tab, bank_tab = st.tabs(["Jogadores", "Empréstimos e Dívidas"])
with player_tab:
    squad = db.query("SELECT * FROM jogadores WHERE clube_id=? ORDER BY nome", (club["club_id"],))
    clubs = db.query("SELECT club_id,nome FROM clubes WHERE club_id<>? ORDER BY nome", (club["club_id"],))
    player_options = {row["player_id"]: row for row in squad}
    club_options = {row["club_id"]: row["nome"] for row in clubs}
    player_id = st.selectbox("Jogador a emprestar", player_options, format_func=lambda key: player_options[key]["nome"])
    destination = st.selectbox("Clube de destino", club_options, format_func=lambda key: club_options[key])
    start = st.date_input("Início", date.fromisoformat(db.state().get("data_atual") or "2026-01-01"))
    end = st.date_input("Fim", start + timedelta(days=180))
    salary_percent = st.slider("Salário pago pelo destino", 0, 100, 100, format="%d%%")
    fee = st.number_input("Taxa de empréstimo", min_value=0.0, step=100_000.0)
    option = st.number_input("Opção de compra (0 = sem opção)", min_value=0.0, step=100_000.0)
    if st.button("Confirmar empréstimo de jogador", type="primary"):
        ok, message = create_player_loan(db, player_id, club["club_id"], destination, start.isoformat(),
                                         end.isoformat(), salary_percent, fee, option or None)
        (st.success if ok else st.error)(message)
    loans = db.query("SELECT * FROM player_loans WHERE clube_origem_id=? OR clube_destino_id=? ORDER BY data_fim",
                     (club["club_id"], club["club_id"]))
    if loans: styled_table(pd.DataFrame(loans))
with bank_tab:
    value = st.number_input("Valor solicitado", min_value=100_000.0, value=5_000_000.0, step=500_000.0)
    months = st.slider("Prazo em meses", 3, 36, 12)
    rate = st.number_input("Juros mensais (%)", min_value=0.0, value=2.0, step=.1)
    if st.button("Solicitar crédito", type="primary"):
        ok, message = request_financial_loan(db, club["club_id"], value, months, rate,
                                             db.state().get("data_atual") or "2026-01-01")
        (st.success if ok else st.error)(message)
    debts = db.query("SELECT * FROM financial_loans WHERE clube_id=? ORDER BY data_inicio DESC", (club["club_id"],))
    if debts: styled_table(pd.DataFrame(debts))

