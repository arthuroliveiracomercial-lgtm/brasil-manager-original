from datetime import date
import streamlit as st

from src.transfer_engine import active_transfer_window
from src.ui import get_database, page_title, require_club

db = get_database(); require_club(db)
page_title("Janelas de Transferências", "Datas configuráveis da temporada")
windows = db.query("SELECT * FROM transfer_windows ORDER BY data_inicio")
today = db.state().get("data_atual") or date.today().isoformat()
if active_transfer_window(db, today):
    st.success(f"Janela aberta na data do jogo: {today}")
else:
    st.warning(f"Janela fechada na data do jogo: {today}. Você pode observar, mas não registrar atletas.")
for window in windows:
    with st.expander(window["nome"], expanded=True):
        left, right = st.columns(2)
        start = left.date_input("Início", date.fromisoformat(window["data_inicio"]), key=f"start_{window['window_id']}")
        end = right.date_input("Fim", date.fromisoformat(window["data_fim"]), key=f"end_{window['window_id']}")
        active = st.checkbox("Ativa", bool(window["ativa"]), key=f"active_{window['window_id']}")
        c1, c2, c3 = st.columns(3)
        buy = c1.checkbox("Compras", bool(window["permite_compra"]), key=f"buy_{window['window_id']}")
        sell = c2.checkbox("Vendas", bool(window["permite_venda"]), key=f"sell_{window['window_id']}")
        loan = c3.checkbox("Empréstimos", bool(window["permite_emprestimo"]), key=f"loan_{window['window_id']}")
        if st.button("Salvar janela", key=f"save_{window['window_id']}"):
            db.execute(
                "UPDATE transfer_windows SET data_inicio=?,data_fim=?,ativa=?,permite_compra=?,permite_venda=?,"
                "permite_emprestimo=? WHERE window_id=?",
                (start.isoformat(), end.isoformat(), int(active), int(buy), int(sell), int(loan), window["window_id"]),
            )
            st.success("Janela atualizada.")

