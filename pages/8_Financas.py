import pandas as pd
import streamlit as st

from src.finance_engine import format_brl, monthly_payroll, processar_fechamento_mensal
from src.ui import finance_card, get_database, page_title, require_club, styled_table

db = get_database(); club = require_club(db)
page_title("Finanças", f"Saúde financeira do {club['nome']}")
players = db.query("SELECT salario FROM jogadores WHERE clube_id=?", (club["club_id"],))
payroll = monthly_payroll(players)
movements = db.query("SELECT data,tipo,descricao,valor FROM movimentos_financeiros WHERE club_id=? ORDER BY id DESC", (club["club_id"],))
revenue = sum(m["valor"] for m in movements if m["valor"] > 0)
expenses = abs(sum(m["valor"] for m in movements if m["valor"] < 0))
projection = club["saldo_caixa"] + revenue - expenses - payroll
cols = st.columns(4)
with cols[0]: finance_card("Saldo", format_brl(club["saldo_caixa"]), "Disponível em caixa")
with cols[1]: finance_card("Transferências", format_brl(club["orcamento_transferencias"]), "Orçamento disponível")
with cols[2]: finance_card("Folha salarial", format_brl(payroll), f"Limite {format_brl(club['folha_salarial_maxima'])}")
with cols[3]: finance_card("Projeção mensal", format_brl(projection), "Após folha e movimentos")
ratio = payroll / max(1, club["folha_salarial_maxima"])
st.progress(min(1.0, ratio), text=f"Uso do limite salarial: {ratio:.0%}")
if ratio > 1: st.error("A folha salarial ultrapassou o limite. Reduza salários antes de contratar.")
elif ratio > .85: st.warning("A folha está acima de 85% do limite. Há pouco espaço para reforços.")
summary = st.columns(2)
summary[0].metric("Receitas acumuladas", format_brl(revenue))
summary[1].metric("Despesas acumuladas", format_brl(expenses))
st.subheader("Fechamento mensal")
game_date = db.state().get("data_atual") or "2026-01-01"
st.caption(f"Data atual do save: {game_date}")
if st.button("Processar Fechamento Mensal", type="primary"):
    report = processar_fechamento_mensal(db, club["club_id"], game_date)
    if report["processado"]:
        st.success(f"Fechamento concluído. Saldo: {format_brl(report['saldo'])}")
        st.rerun()
    else:
        st.warning(report["mensagem"])
debts = db.query("SELECT financial_loan_id,valor_principal,parcela_mensal,saldo_devedor,parcelas_pagas,status "
                 "FROM financial_loans WHERE clube_id=? ORDER BY data_inicio DESC", (club["club_id"],))
if debts:
    st.subheader("Empréstimos e Dívidas")
    debt_frame = pd.DataFrame(debts)
    for column in ("valor_principal","parcela_mensal","saldo_devedor"):
        debt_frame[column] = debt_frame[column].map(format_brl)
    styled_table(debt_frame)
if movements:
    frame = pd.DataFrame(movements); frame["valor"] = frame["valor"].map(format_brl)
    frame.columns = ["Data","Tipo","Descrição","Valor"]; styled_table(frame)
else: st.info("Movimentos aparecerão após partidas em casa e transferências.")
