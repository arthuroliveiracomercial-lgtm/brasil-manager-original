from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_update import validate_upload
from src.finance_engine import format_brl, monthly_payroll
from src.schemas import SCHEMAS
from src.ui import card, club_card, get_database, inject_css, match_card, page_title, selected_club

st.set_page_config(page_title="Brasil Manager", page_icon="⚽", layout="wide")
inject_css()
db = get_database()
state = db.state()
club = selected_club(db)

page_title("Brasil Manager", f"Temporada {state['temporada']} · o futebol brasileiro nas suas mãos")

if club:
    next_match = db.next_user_match(club["club_id"])
    league_comp = db.competition_for_club(club["club_id"])
    position = db.query(
        "SELECT COUNT(*)+1 posicao FROM classificacao c WHERE c.competition_id=? AND c.pontos>(SELECT pontos FROM classificacao WHERE club_id=? AND competition_id=?)",
        (league_comp, club["club_id"], league_comp),
    )[0]["posicao"]
    top = st.columns(4)
    with top[0]: card("Clube", club["nome"], f"{club['estado']} · Série {club['divisao']}", "#0D5C4A")
    with top[1]: card("Classificação", f"{position}º lugar", f"{next_match['competition_nome'] if next_match else 'Temporada finalizada'}", "#F4B942")
    with top[2]: card("Saldo em caixa", format_brl(club["saldo_caixa"]), "Finanças do clube", "#34D399")
    with top[3]: card("Reputação", club["reputacao"], club["estadio"], "#3B82F6")
    players = db.query("SELECT salario,moral,condicao_fisica FROM jogadores WHERE clube_id=?", (club["club_id"],))
    average_moral = sum((player["moral"] or 70) for player in players) / max(1, len(players))
    average_condition = sum((player["condicao_fisica"] or 90) for player in players) / max(1, len(players))
    secondary = st.columns(4)
    with secondary[0]: card("Orçamento", format_brl(club["orcamento_transferencias"]), "Transferências")
    with secondary[1]: card("Folha salarial", format_brl(monthly_payroll(players)), "Custo mensal")
    with secondary[2]: card("Moral média", f"{average_moral:.0f}%", "Ambiente do elenco")
    with secondary[3]: card("Condição média", f"{average_condition:.0f}%", "Prontidão física")
    st.subheader("Agenda do treinador")
    left, right = st.columns([1.1, 1])
    with left:
        if next_match:
            match_card(next_match["mandante_nome"], next_match["visitante_nome"], "×", f"Rodada {next_match['rodada']} · {next_match['data']}")
        else:
            st.success("Temporada encerrada.")
            if st.button("Iniciar próxima temporada", type="primary", width="stretch"):
                new_season = db.advance_season()
                st.cache_resource.clear()
                st.success(f"Temporada {new_season} criada. Boa sorte!")
                st.rerun()
    with right:
        if next_match:
            st.page_link("pages/5_Partida.py", label="Ir para Próxima Partida", icon="▶️", use_container_width=True)
        else:
            if st.button("▶️ Começar temporada seguinte", width="stretch"):
                new_season = db.advance_season()
                st.cache_resource.clear()
                st.success(f"Temporada {new_season} criada. Boa sorte!")
                st.rerun()
        st.page_link("pages/2_Escalacao.py", label="Revisar Escalação", icon="📋", use_container_width=True)
        st.page_link("pages/3_Tatica.py", label="Ajustar Tática", icon="🧠", use_container_width=True)
        st.page_link("pages/6_Classificacao.py", label="Ver Classificação", icon="🏆", use_container_width=True)
    recent = db.query(
        "SELECT c.*,m.nome mandante,v.nome visitante FROM calendario c "
        "JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
        "WHERE c.jogado=1 AND (c.mandante_id=? OR c.visitante_id=?) ORDER BY c.rodada DESC LIMIT 5",
        (club["club_id"], club["club_id"]),
    )
    if recent:
        st.subheader("Últimos resultados")
        st.markdown(" · ".join(
            f"**{row['mandante']} {row['gols_mandante']}×{row['gols_visitante']} {row['visitante']}**"
            for row in recent
        ))
    with st.expander("Novo save"):
        st.warning("Criar um novo save reinicia resultados, finanças, escalação e tática. Clubes e jogadores importados são preservados.")
        confirm = st.checkbox("Entendo e quero apagar o progresso desta carreira")
        if st.button("Criar Novo Save", disabled=not confirm):
            db.new_save(); st.cache_resource.clear(); st.rerun()
else:
    st.subheader("Começar uma carreira")
    clubs = db.query("SELECT * FROM clubes ORDER BY reputacao DESC,nome")
    options = {row["club_id"]: row for row in clubs}
    choice = st.selectbox("Escolha o clube", options, format_func=lambda key: options[key]["nome"])
    preview = options[choice]
    cols = st.columns(4)
    with cols[0]: card("Estado", preview["estado"], preview["cidade"])
    with cols[1]: card("Estádio", preview["estadio"], f"{preview['capacidade_estadio']:,} lugares".replace(",", "."))
    with cols[2]: card("Reputação", preview["reputacao"], "Força institucional")
    with cols[3]: card("Orçamento", format_brl(preview["orcamento_transferencias"]), "Transferências")
    if st.button("Começar Carreira", type="primary", width="stretch"):
        db.choose_club(choice); st.rerun()

with st.expander("Importar Dados por Excel ou CSV"):
    template = Path("data/modelos/modelo_importacao_brasil_manager.xlsx")
    if template.exists(): st.download_button("Baixar planilha-modelo", template.read_bytes(), template.name)
    uploaded = st.file_uploader("Arquivo de dados", type=["xlsx", "xlsm", "csv"])
    dataset = st.selectbox("Tipo de conteúdo do CSV", list(SCHEMAS)) if uploaded and uploaded.name.lower().endswith(".csv") else None
    if uploaded:
        try:
            result = validate_upload(uploaded.name, uploaded.getvalue(), db, dataset)
            issues = pd.DataFrame([issue.as_dict() for issue in result.issues])
            if result.can_import and st.button("Importar Dados", type="primary"):
                db.import_frames(result.data, uploaded.name, "atualizar"); st.success("Dados importados.")
            elif not result.can_import: st.error("Corrija os erros antes de importar.")
            if not issues.empty: st.dataframe(issues, hide_index=True, width="stretch")
        except Exception as exc: st.error(str(exc))
