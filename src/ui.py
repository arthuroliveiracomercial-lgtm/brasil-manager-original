from html import escape
from pathlib import Path
import os

import pandas as pd
import streamlit as st

from .data_loader import bootstrap_game
from .database import Database
from .match_engine import player_rating
from .models import FORMATIONS, Tactic
from .formation_view import render_pitch as formation_render_pitch
from .expansion import seed_expansion

COLORS = {"navy": "#071B2B", "green": "#0D5C4A", "lime": "#34D399", "gold": "#F4B942", "muted": "#8EA5B5"}


def inject_css():
    st.markdown("""
    <style>
    .stApp {background:linear-gradient(145deg,#F4F7F8 0%,#E8F0EF 100%);color:#112A36}
    [data-testid="stSidebar"] {background:#071B2B}
    [data-testid="stSidebar"] * {color:#EAF4F2}
    [data-testid="stSidebarNav"] span {font-weight:650}
    .block-container {max-width:1240px;padding-top:1.8rem;padding-bottom:4rem}
    h1,h2,h3 {letter-spacing:-.025em;color:#0A2633}
    div.stButton > button {min-height:46px;border-radius:10px;font-weight:750;border:1px solid #0D5C4A}
    div.stButton > button[kind="primary"] {background:linear-gradient(90deg,#0D5C4A,#087A62);color:white;box-shadow:0 8px 20px #0D5C4A30}
    [data-testid="stMetric"] {background:white;border:1px solid #D8E4E2;border-radius:14px;padding:16px;box-shadow:0 5px 18px #153A4510}
    [data-testid="stDataFrame"] {border:1px solid #D8E4E2;border-radius:12px;overflow:hidden}
    .bm-header {background:linear-gradient(115deg,#071B2B,#0D5C4A);padding:24px 28px;border-radius:18px;color:white;margin-bottom:20px;box-shadow:0 12px 30px #071B2B25}
    .bm-header h1 {color:white;margin:0;font-size:2rem}.bm-header p{margin:.35rem 0 0;color:#B9D9D2}
    .bm-card {background:white;border:1px solid #D8E4E2;border-radius:14px;padding:17px 19px;box-shadow:0 6px 18px #173E4810;height:100%}
    .bm-label {color:#637D89;text-transform:uppercase;font-size:.72rem;font-weight:800;letter-spacing:.08em}
    .bm-value {font-size:1.45rem;font-weight:800;color:#0A2633;margin-top:5px}.bm-sub{color:#637D89;font-size:.82rem}
    .bm-match {background:#071B2B;color:white;border-radius:16px;padding:20px;text-align:center}.bm-score{font-size:2.4rem;font-weight:900;color:#F4B942}
    .bm-badge {display:inline-block;padding:4px 9px;border-radius:99px;background:#DDF7EF;color:#0D5C4A;font-size:.74rem;font-weight:800}
    .pitch {position:relative;min-height:650px;border-radius:20px;background:repeating-linear-gradient(90deg,#087A52 0,#087A52 12.5%,#09704D 12.5%,#09704D 25%);border:4px solid #E7FFF4;box-shadow:0 12px 25px #073B2B35;overflow:hidden}
    .pitch:before {content:"";position:absolute;inset:4%;border:2px solid #FFFFFF90;border-radius:3px}
    .pitch:after {content:"";position:absolute;left:50%;top:4%;bottom:4%;border-left:2px solid #FFFFFF90}
    .player-chip {position:absolute;transform:translate(-50%,-50%);width:132px;background:#071B2BEE;color:white;border:2px solid #34D399;border-radius:12px;padding:7px;text-align:center;z-index:2;box-shadow:0 5px 12px #0018}
    .player-chip.warn {border-color:#F4B942}.player-pos{font-size:.65rem;color:#7FE2C4;font-weight:900}.player-name{font-size:.78rem;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.player-role{font-size:.61rem;color:#B9CDD5}.player-rate{color:#F4B942;font-weight:900}
    .mobile-nav {display:none}
    @media (max-width: 700px) {
      .block-container {padding:1rem .65rem 5.5rem;max-width:100%}
      .bm-header {padding:18px 17px;border-radius:14px;margin-bottom:14px}
      .bm-header h1 {font-size:1.55rem}.bm-header p{font-size:.86rem}
      [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:.55rem}
      [data-testid="stHorizontalBlock"] > div {min-width:calc(50% - .4rem);flex:1 1 calc(50% - .4rem)}
      [data-testid="stMetric"] {padding:11px}
      .bm-card {padding:13px 14px;border-radius:12px}.bm-value{font-size:1.15rem}
      .bm-match {padding:14px}.bm-score{font-size:1.8rem}
      div.stButton > button, [data-testid="stLinkButton"] a {width:100%;min-height:44px}
      [data-testid="stDataFrame"] {max-width:100%;overflow-x:auto;font-size:.78rem}
      .pitch {min-height:510px;border-width:2px}
      .player-chip {width:74px;padding:5px 3px;border-radius:9px}
      .player-name {font-size:.66rem}.player-role{display:none}.player-rate{font-size:.72rem}
      .player-pos{font-size:.58rem}
      h1{font-size:1.65rem}h2{font-size:1.3rem}h3{font-size:1.08rem}
      .mobile-nav {display:flex;position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#071B2B;
        justify-content:space-around;padding:8px 4px calc(8px + env(safe-area-inset-bottom));box-shadow:0 -5px 18px #0016}
      .mobile-nav a {color:#EAF4F2;text-decoration:none;font-size:.68rem;font-weight:750;text-align:center;padding:4px 7px}
      .mobile-nav span {display:block;font-size:1.05rem}
    }
    </style>""", unsafe_allow_html=True)


@st.cache_resource
def get_database():
    database = Database(os.getenv("BRASIL_MANAGER_DB", "database/brasil_manager.db"))
    workbook = Path(__file__).resolve().parents[1] / "data" / "modelos" / "modelo_importacao_brasil_manager.xlsx"
    bootstrap_game(database, workbook)
    seed_expansion(database)
    return database


def selected_club(database):
    club_id = database.state().get("user_club_id")
    rows = database.query("SELECT * FROM clubes WHERE club_id=?", (club_id,)) if club_id else []
    return rows[0] if rows else None


def require_club(database):
    club = selected_club(database)
    if not club:
        st.warning("Escolha seu clube na página inicial antes de continuar.")
        st.page_link("app.py", label="Ir para o início", icon="🏠")
        st.stop()
    sidebar_profile(database, club)
    return club


def tactic_object(database, club_id):
    row = database.get_tactic(club_id)
    return row, Tactic(**{key: row[key] for key in ("mentalidade", "estilo", "linha_defensiva", "pressao", "ritmo", "foco_ataque", "tipo_passe")})


def automatic_lineup(database, club_id, formation=None):
    tactic = database.get_tactic(club_id)
    slots = FORMATIONS.get(formation or tactic["formacao"], FORMATIONS["4-3-3"])
    players = database.query("SELECT * FROM jogadores WHERE clube_id=? AND COALESCE(condicao_fisica,100)>20 AND COALESCE(status,'Disponível')<>'Lesionado'", (club_id,))
    chosen, used = [], set()
    for slot in slots:
        available = [p for p in players if p["player_id"] not in used]
        if not available:
            break
        best = max(available, key=lambda p: player_rating(p, slot))
        chosen.append(best); used.add(best["player_id"])
    return chosen, slots


def page_title(title, subtitle=""):
    inject_css()
    st.markdown(f'<div class="bm-header"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>', unsafe_allow_html=True)
    mobile_nav()


def card(label, value, subtitle="", accent=""):
    border = f"border-top:4px solid {accent};" if accent else ""
    st.markdown(f'<div class="bm-card" style="{border}"><div class="bm-label">{escape(str(label))}</div><div class="bm-value">{escape(str(value))}</div><div class="bm-sub">{escape(str(subtitle))}</div></div>', unsafe_allow_html=True)


def club_card(club):
    card(club["nome"], f"{club['estado']} · Série {club['divisao']}", club.get("estadio") or "Estádio não informado", COLORS["green"])


def player_card(player, slot=None):
    rating = round(player_rating(player, slot))
    card(player.get("apelido") or player["nome"], f"{player['posicao_principal']} · {rating}", f"Moral {player.get('moral') or 0} · Condição {player.get('condicao_fisica') or 0}")


def finance_card(label, value, subtitle=""):
    card(label, value, subtitle, COLORS["gold"])


def match_card(home, away, score="×", status="Próximo jogo"):
    st.markdown(f'<div class="bm-match"><div class="bm-label" style="color:#8FB5AD">{escape(status)}</div><h3 style="color:white">{escape(home)}</h3><div class="bm-score">{escape(score)}</div><h3 style="color:white">{escape(away)}</h3></div>', unsafe_allow_html=True)


def styled_table(frame, height=None):
    options = {"width": "stretch", "hide_index": True}
    if height is not None:
        options["height"] = height
    st.dataframe(frame, **options)


def condition_label(value):
    return "🟢 Excelente" if value >= 85 else "🟡 Atenção" if value >= 65 else "🔴 Baixa"


PITCH_COORDS = {
    "4-4-2": [(8,50),(25,12),(25,37),(25,63),(25,88),(52,14),(52,39),(52,61),(52,86),(80,34),(80,66)],
    "4-3-3": [(8,50),(25,12),(25,37),(25,63),(25,88),(50,25),(50,50),(50,75),(78,15),(82,50),(78,85)],
    "4-2-3-1": [(8,50),(24,12),(24,37),(24,63),(24,88),(43,35),(43,65),(63,18),(66,50),(63,82),(83,50)],
    "3-5-2": [(8,50),(25,22),(23,50),(25,78),(50,8),(45,34),(48,50),(45,66),(50,92),(80,35),(80,65)],
    "4-1-4-1": [(8,50),(23,12),(23,37),(23,63),(23,88),(41,50),(60,15),(58,39),(58,61),(60,85),(83,50)],
    "4-3-1-2": [(8,50),(23,12),(23,37),(23,63),(23,88),(48,24),(44,50),(48,76),(66,50),(82,34),(82,66)],
}


def render_pitch(formation, slots, players, roles):
    chips = []
    coords = PITCH_COORDS[formation]
    for index, (slot, player, role) in enumerate(zip(slots, players, roles)):
        x, y = coords[index]
        off = player.get("posicao_principal") not in {slot} and slot not in str(player.get("posicoes_secundarias") or "")
        css = "player-chip warn" if off else "player-chip"
        name = escape(player.get("apelido") or player["nome"].split()[0])
        chips.append(f'<div class="{css}" style="left:{y}%;top:{100-x}%"><div class="player-pos">{slot}</div><div class="player-name">{name}</div><div class="player-role">{escape(role)}</div><div class="player-rate">{player_rating(player, slot):.0f}</div></div>')
    st.markdown('<div class="pitch">' + "".join(chips) + "</div>", unsafe_allow_html=True)


# Implementação centralizada no módulo de formação; o alias preserva compatibilidade.
render_pitch = formation_render_pitch


def progress_bar(label, value, color="#34D399"):
    safe = max(0, min(100, int(value or 0)))
    st.markdown(
        f'<div class="bm-label">{escape(label)}</div><div style="height:9px;background:#DDE8E6;border-radius:9px;overflow:hidden;margin:5px 0 12px">'
        f'<div style="height:100%;width:{safe}%;background:{color}"></div></div>', unsafe_allow_html=True,
    )


def alert(message, level="info"):
    colors = {"info": ("#E8F1FF", "#235A9F"), "warning": ("#FFF3C4", "#7A5700"), "danger": ("#FFE7E7", "#A52A2A")}
    background, foreground = colors.get(level, colors["info"])
    st.markdown(
        f'<div style="padding:12px 15px;border-radius:10px;background:{background};color:{foreground};font-weight:650">{escape(message)}</div>',
        unsafe_allow_html=True,
    )


def round_panel(title, rows):
    content = "".join(
        f"<div style='padding:8px 0;border-bottom:1px solid #E4ECEA'>{escape(str(row))}</div>" for row in rows
    )
    st.markdown(f'<div class="bm-card"><div class="bm-label">{escape(title)}</div>{content}</div>', unsafe_allow_html=True)


def event_panel(events):
    round_panel("Eventos ao vivo", events[-8:] or ["A bola ainda não rolou."])


def sidebar_profile(database, club):
    next_match = database.next_user_match(club["club_id"])
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### ⚽ {club['nome']}")
        st.caption(f"Temporada {database.state()['temporada']} · Rodada {next_match['rodada'] if next_match else 'Final'}")


def mobile_nav():
    st.markdown(
        '<nav class="mobile-nav">'
        '<a href="/" target="_self"><span>🏠</span>Início</a>'
        '<a href="/Elenco" target="_self"><span>👥</span>Elenco</a>'
        '<a href="/Escalacao" target="_self"><span>📋</span>Time</a>'
        '<a href="/Partida" target="_self"><span>▶️</span>Jogar</a>'
        '<a href="/Mais" target="_self"><span>•••</span>Mais</a>'
        '</nav>',
        unsafe_allow_html=True,
    )
