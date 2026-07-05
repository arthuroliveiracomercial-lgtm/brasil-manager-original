import streamlit as st

from src.ui import get_database, page_title, require_club

db = get_database(); require_club(db)
page_title("Mais", "Carreira, análise e administração")
items = [
    ("pages/6_Classificacao.py", "🏆 Classificação"),
    ("pages/15_Treino.py", "🏋️ Treino"),
    ("pages/16_Noticias.py", "📰 Notícias"),
    ("pages/17_Olheiros.py", "🔎 Olheiros"),
    ("pages/18_Replays.py", "🎬 Replays"),
    ("pages/19_Configuracoes.py", "⚙️ Configurações e Saves"),
    ("pages/12_Competições.py", "🌎 Competições"),
    ("pages/8_Financas.py", "💰 Finanças"),
]
for target, label in items:
    st.page_link(target, label=label, use_container_width=True)

