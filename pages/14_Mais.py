import streamlit as st

from src.ui import get_database, page_title, require_club

db = get_database(); require_club(db)
page_title("Mais", "Carreira, análise e administração")
items = [
    ("🏆 Classificação", "/Classificacao"),
    ("🏋️ Treino", "/Treino"),
    ("📰 Notícias", "/Noticias"),
    ("🔎 Olheiros", "/Olheiros"),
    ("🎬 Replays", "/Replays"),
    ("⚙️ Configurações e Saves", "/Configuracoes"),
    ("🌎 Competições", "/Competições"),
    ("💰 Finanças", "/Financas"),
]
for label, target in items:
    st.link_button(label, target, width="stretch")

