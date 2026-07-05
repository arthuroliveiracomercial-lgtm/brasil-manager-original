from pathlib import Path
import json
import pandas as pd
import streamlit as st

from src.career_engine import create_save_version, save_rule_preset
from src.ui import get_database, page_title, require_club, styled_table

db = get_database(); require_club(db)
page_title("Configurações e Saves", "Personalize regras e proteja sua carreira")
save_tab, rules_tab = st.tabs(["Versões do Save", "Regulamentos"])
with save_tab:
    name = st.text_input("Nome da versão", "Backup manual")
    note = st.text_area("Observação")
    if st.button("Criar Versão do Save", type="primary", width="stretch"):
        destination = create_save_version(db, Path(__file__).resolve().parents[1], name, note)
        st.success(f"Versão criada: {destination.name}")
    versions = db.query("SELECT criado_em,nome,temporada,rodada,observacao FROM save_versions ORDER BY criado_em DESC")
    if versions: styled_table(pd.DataFrame(versions))
with rules_tab:
    preset_name = st.text_input("Nome do regulamento", "Minha liga")
    kind = st.selectbox("Formato", ["Liga","Grupos + mata-mata","Mata-mata"])
    clubs = st.number_input("Número de clubes", 2, 128, 20)
    promoted = st.number_input("Promovidos", 0, 20, 0)
    relegated = st.number_input("Rebaixados", 0, 20, 4)
    two_legs = st.toggle("Confrontos de ida e volta")
    if st.button("Salvar Regulamento", type="primary", width="stretch"):
        save_rule_preset(db, preset_name, kind, {"clubes":clubs,"promovidos":promoted,"rebaixados":relegated,"ida_volta":two_legs})
        st.success("Regulamento próprio salvo.")
    presets = db.query("SELECT nome,tipo,configuracao,criado_em FROM competition_rule_presets ORDER BY criado_em DESC")
    if presets: styled_table(pd.DataFrame(presets))
