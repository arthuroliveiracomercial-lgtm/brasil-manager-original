import streamlit as st

from src.models import Tactic
from src.tactic_engine import tactic_modifiers, tactical_summary
from src.ui import card, get_database, page_title, require_club

db = get_database()
club = require_club(db)
page_title("Tática", f"Identidade de jogo do {club['nome']}")
current = db.get_tactic(club["club_id"])

def pick(label, options, key):
    value = current[key]
    return st.selectbox(label, options, index=options.index(value) if value in options else 0, key=key)

left, right = st.columns(2)
with left:
    st.subheader("Com a bola")
    mentalidade = pick("Mentalidade", ["Defensiva", "Equilibrada", "Positiva", "Ofensiva"], "mentalidade")
    estilo = pick("Estilo de jogo", ["Posse de bola", "Contra-ataque", "Pressão alta", "Jogo direto", "Equilibrado"], "estilo")
    ritmo = pick("Ritmo", ["Lento", "Normal", "Rápido"], "ritmo")
    foco = pick("Foco de ataque", ["Meio", "Laterais", "Misto"], "foco_ataque")
    passe = pick("Tipo de passe", ["Curto", "Misto", "Direto"], "tipo_passe")
with right:
    st.subheader("Sem a bola")
    linha = pick("Linha defensiva", ["Baixa", "Normal", "Alta"], "linha_defensiva")
    pressao = pick("Pressão", ["Baixa", "Normal", "Alta"], "pressao")
    st.markdown("#### Leitura rápida")
    preview = Tactic(mentalidade, estilo, linha, pressao, ritmo, foco, passe)
    attack, defense, fatigue = tactic_modifiers(preview)
    creation = 50 + attack * 3 + (6 if estilo in {"Posse de bola", "Pressão alta"} else 0)
    counter_risk = 35 + max(0, attack - defense) * 3 + (12 if linha == "Alta" else -5 if linha == "Baixa" else 0)
    cols = st.columns(5)
    cols[0].metric("Ataque", f"{attack:+.0f}")
    cols[1].metric("Defesa", f"{defense:+.0f}")
    cols[2].metric("Desgaste", f"{fatigue:.1f}×")
    cols[3].metric("Criação", f"{max(0,min(100,creation)):.0f}")
    cols[4].metric("Risco contra-ataque", f"{max(0,min(100,counter_risk)):.0f}")

st.subheader("Resumo Tático")
st.info(tactical_summary(preview))
if st.button("Salvar Tática", type="primary", width="stretch"):
    db.save_tactic(club["club_id"], {**current, "mentalidade": mentalidade, "estilo": estilo,
        "linha_defensiva": linha, "pressao": pressao, "ritmo": ritmo, "foco_ataque": foco, "tipo_passe": passe})
    st.success("Plano de jogo salvo.")
