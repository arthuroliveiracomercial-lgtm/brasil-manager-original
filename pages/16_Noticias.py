import streamlit as st

from src.career_engine import generate_news
from src.ui import get_database, page_title, require_club

db = get_database(); club = require_club(db)
page_title("Notícias", "Central de informações da carreira")
game_date = db.state().get("data_atual") or "2026-01-01"
generate_news(db, club["club_id"], game_date)
news = db.query("SELECT * FROM news_items WHERE club_id=? ORDER BY data DESC,news_id DESC", (club["club_id"],))
unread = sum(not item["lida"] for item in news)
st.metric("Não lidas", unread)
for item in news:
    with st.container(border=True):
        st.caption(f"{item['data']} · {item['categoria']}")
        st.subheader(("● " if not item["lida"] else "") + item["titulo"])
        st.write(item["conteudo"])
        if not item["lida"] and st.button("Marcar como lida", key=item["news_id"]):
            db.execute("UPDATE news_items SET lida=1 WHERE news_id=?", (item["news_id"],)); st.rerun()

