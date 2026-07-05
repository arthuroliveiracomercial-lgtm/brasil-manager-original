from html import escape

import streamlit as st

from .match_engine import player_rating

FORMATION_COORDS = {
    "4-4-2": [(8,50),(25,12),(25,37),(25,63),(25,88),(52,14),(52,39),(52,61),(52,86),(80,34),(80,66)],
    "4-3-3": [(8,50),(25,12),(25,37),(25,63),(25,88),(50,25),(50,50),(50,75),(78,15),(82,50),(78,85)],
    "4-2-3-1": [(8,50),(24,12),(24,37),(24,63),(24,88),(43,35),(43,65),(63,18),(66,50),(63,82),(83,50)],
    "3-5-2": [(8,50),(25,22),(23,50),(25,78),(50,8),(45,34),(48,50),(45,66),(50,92),(80,35),(80,65)],
    "4-1-4-1": [(8,50),(23,12),(23,37),(23,63),(23,88),(41,50),(60,15),(58,39),(58,61),(60,85),(83,50)],
    "4-3-1-2": [(8,50),(23,12),(23,37),(23,63),(23,88),(48,24),(44,50),(48,76),(66,50),(82,34),(82,66)],
}

POSITION_COMPATIBILITY = {
    "GOL": {"GOL"}, "ZAG": {"ZAG"}, "LAT": {"LAT", "ALA"}, "ALA": {"ALA", "LAT"},
    "VOL": {"VOL", "MC"}, "MC": {"MC", "VOL", "MEI"}, "MEI": {"MEI", "MC", "PE", "PD"},
    "PE": {"PE", "PD", "MEI"}, "PD": {"PD", "PE", "MEI"}, "ATA": {"ATA", "PE", "PD"},
}


def is_out_of_position(player: dict, slot: str) -> bool:
    secondary = set(str(player.get("posicoes_secundarias") or "").replace(",", ";").split(";"))
    return player.get("posicao_principal") not in POSITION_COMPATIBILITY.get(slot, {slot}) and slot not in secondary


def pitch_html(formation, slots, players, roles):
    chips = []
    for index, (slot, player, role) in enumerate(zip(slots, players, roles)):
        vertical, horizontal = FORMATION_COORDS[formation][index]
        warning = is_out_of_position(player, slot)
        css = "player-chip warn" if warning else "player-chip"
        name = escape(player.get("apelido") or player["nome"].split()[0])
        chips.append(
            f'<div class="{css}" style="left:{horizontal}%;top:{100-vertical}%">'
            f'<div class="player-pos">{slot}{" ⚠" if warning else ""}</div>'
            f'<div class="player-name">{name}</div><div class="player-role">{escape(role)}</div>'
            f'<div class="player-rate">{player_rating(player, slot):.0f}</div></div>'
        )
    return '<div class="pitch">' + "".join(chips) + "</div>"


def render_pitch(formation, slots, players, roles):
    st.markdown(pitch_html(formation, slots, players, roles), unsafe_allow_html=True)

