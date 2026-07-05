import streamlit as st

from src.career_engine import process_training, save_training_plan
from src.ui import get_database, page_title, progress_bar, require_club

db = get_database(); club = require_club(db)
page_title("Treino", "Planejamento semanal do elenco")
players = db.query("SELECT moral,condicao_fisica FROM jogadores WHERE clube_id=?", (club["club_id"],))
morale = sum((p["moral"] or 70) for p in players) / max(1, len(players))
condition = sum((p["condicao_fisica"] or 90) for p in players) / max(1, len(players))
progress_bar("Moral do elenco", morale, "#3B82F6")
progress_bar("Condição física", condition, "#34D399")
week = st.text_input("Semana", value=(db.state().get("data_atual") or "2026-01-01")[:10])
focus = st.selectbox("Foco", ["Equilíbrio","Físico","Defesa","Criação","Finalização","Bolas paradas"])
intensity = st.segmented_control("Intensidade", ["Leve","Normal","Alta"], default="Normal")
rest = st.toggle("Incluir dia de descanso", value=True)
if st.button("Salvar Plano", type="primary", width="stretch"):
    save_training_plan(db, club["club_id"], week, focus, intensity, rest)
    st.success("Plano semanal salvo.")
if st.button("Processar Semana", width="stretch"):
    ok, message = process_training(db, club["club_id"], week)
    (st.success if ok else st.warning)(message)
plans = db.query("SELECT semana,foco,intensidade,descanso,status FROM training_plans WHERE club_id=? ORDER BY semana DESC LIMIT 8", (club["club_id"],))
for plan in plans:
    st.markdown(f"**{plan['semana']} · {plan['foco']}**  \n{plan['intensidade']} · {'com descanso' if plan['descanso'] else 'sem descanso'} · {plan['status']}")
    st.divider()

