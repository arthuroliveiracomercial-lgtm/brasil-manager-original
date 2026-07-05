from pathlib import Path
import sqlite3
from contextlib import closing
import json

import pandas as pd

from .schemas import PRIMARY_KEYS

TABLES_SQL = """
CREATE TABLE IF NOT EXISTS clubes (
  club_id TEXT PRIMARY KEY, nome TEXT NOT NULL, nome_curto TEXT, estado TEXT NOT NULL,
  cidade TEXT NOT NULL, divisao TEXT NOT NULL, estadio TEXT, capacidade_estadio INTEGER NOT NULL,
  reputacao INTEGER NOT NULL, orcamento_transferencias REAL NOT NULL,
  folha_salarial_maxima REAL NOT NULL, saldo_caixa REAL, categoria_base INTEGER,
  rival_1 TEXT, rival_2 TEXT
);
CREATE TABLE IF NOT EXISTS jogadores (
  player_id TEXT PRIMARY KEY, nome TEXT NOT NULL, apelido TEXT, clube_id TEXT NOT NULL,
  idade INTEGER NOT NULL, nascimento TEXT, nacionalidade TEXT, posicao_principal TEXT NOT NULL,
  posicoes_secundarias TEXT, pe_preferido TEXT, altura REAL, peso REAL, valor_mercado REAL NOT NULL,
  salario REAL NOT NULL, contrato_inicio TEXT, contrato_fim TEXT, reputacao INTEGER, potencial INTEGER,
  moral INTEGER, condicao_fisica INTEGER, ritmo INTEGER, finalizacao INTEGER, passe INTEGER,
  tecnica INTEGER, marcacao INTEGER, desarme INTEGER, cruzamento INTEGER, drible INTEGER,
  cabeceio INTEGER, forca INTEGER, resistencia INTEGER, velocidade INTEGER, aceleracao INTEGER,
  decisao INTEGER, trabalho_equipe INTEGER, lideranca INTEGER, goleiro_reflexos INTEGER,
  goleiro_posicionamento INTEGER, goleiro_jogo_maos INTEGER,
  FOREIGN KEY(clube_id) REFERENCES clubes(club_id)
);
CREATE TABLE IF NOT EXISTS competicoes (
  competition_id TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, pais TEXT,
  divisao TEXT, formato TEXT NOT NULL, numero_times INTEGER NOT NULL, acesso INTEGER,
  rebaixamento INTEGER, premio_campeao REAL, premio_participacao REAL
);
CREATE TABLE IF NOT EXISTS calendario (
  match_id TEXT PRIMARY KEY, competition_id TEXT NOT NULL, rodada INTEGER NOT NULL, data TEXT NOT NULL,
  mandante_id TEXT NOT NULL, visitante_id TEXT NOT NULL, estadio TEXT, jogado INTEGER,
  gols_mandante INTEGER, gols_visitante INTEGER
);
CREATE TABLE IF NOT EXISTS transferencias (
  transfer_id TEXT PRIMARY KEY, player_id TEXT NOT NULL, clube_origem_id TEXT, clube_destino_id TEXT,
  valor REAL NOT NULL, salario_novo REAL, data TEXT NOT NULL, tipo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS importacoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT DEFAULT CURRENT_TIMESTAMP,
  arquivo TEXT NOT NULL, tabela TEXT NOT NULL, registros INTEGER NOT NULL, modo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS game_state (
  id INTEGER PRIMARY KEY CHECK(id=1), user_club_id TEXT, temporada INTEGER NOT NULL DEFAULT 2026,
  rodada_atual INTEGER NOT NULL DEFAULT 1, iniciado INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS escalacao (
  club_id TEXT NOT NULL, slot INTEGER NOT NULL, posicao TEXT NOT NULL, player_id TEXT NOT NULL,
  titular INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(club_id, slot)
);
CREATE TABLE IF NOT EXISTS taticas (
  club_id TEXT PRIMARY KEY, formacao TEXT NOT NULL DEFAULT '4-3-3',
  mentalidade TEXT NOT NULL DEFAULT 'Equilibrada', estilo TEXT NOT NULL DEFAULT 'Equilibrado',
  linha_defensiva TEXT NOT NULL DEFAULT 'Normal', pressao TEXT NOT NULL DEFAULT 'Normal',
  ritmo TEXT NOT NULL DEFAULT 'Normal', foco_ataque TEXT NOT NULL DEFAULT 'Misto',
  tipo_passe TEXT NOT NULL DEFAULT 'Misto'
);
CREATE TABLE IF NOT EXISTS classificacao (
  competition_id TEXT NOT NULL, club_id TEXT NOT NULL, jogos INTEGER DEFAULT 0,
  vitorias INTEGER DEFAULT 0, empates INTEGER DEFAULT 0, derrotas INTEGER DEFAULT 0,
  gols_pro INTEGER DEFAULT 0, gols_contra INTEGER DEFAULT 0, saldo INTEGER DEFAULT 0,
  pontos INTEGER DEFAULT 0, PRIMARY KEY(competition_id, club_id)
);
CREATE TABLE IF NOT EXISTS eventos_partida (
  id INTEGER PRIMARY KEY AUTOINCREMENT, match_id TEXT NOT NULL, ordem INTEGER NOT NULL, evento TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS detalhes_partida (
  match_id TEXT PRIMARY KEY, estatisticas TEXT NOT NULL DEFAULT '{}',
  melhor_jogador TEXT, artilheiros TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS movimentos_financeiros (
  id INTEGER PRIMARY KEY AUTOINCREMENT, club_id TEXT NOT NULL, data TEXT NOT NULL,
  tipo TEXT NOT NULL, descricao TEXT NOT NULL, valor REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS competitions (
  competition_id TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, regiao TEXT,
  temporada INTEGER NOT NULL, divisao TEXT, formato TEXT NOT NULL, numero_clubes INTEGER,
  fase_atual TEXT, regras_classificacao TEXT, regras_desempate TEXT, premiacao REAL DEFAULT 0,
  vagas TEXT, promovidos INTEGER DEFAULT 0, rebaixados INTEGER DEFAULT 0, ativa INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS competition_phases (
  phase_id TEXT PRIMARY KEY, competition_id TEXT NOT NULL, nome TEXT NOT NULL, ordem INTEGER,
  tipo TEXT NOT NULL, ida_volta INTEGER DEFAULT 0, classificados INTEGER
);
CREATE TABLE IF NOT EXISTS competition_groups (
  group_id TEXT PRIMARY KEY, phase_id TEXT NOT NULL, nome TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS competition_matches (
  match_id TEXT PRIMARY KEY, competition_id TEXT NOT NULL, phase_id TEXT, group_id TEXT,
  data TEXT, mandante_id TEXT, visitante_id TEXT, rodada INTEGER, perna INTEGER DEFAULT 1,
  gols_mandante INTEGER, gols_visitante INTEGER, status TEXT DEFAULT 'Pendente'
);
CREATE TABLE IF NOT EXISTS transfer_windows (
  window_id TEXT PRIMARY KEY, temporada INTEGER NOT NULL, nome TEXT NOT NULL,
  data_inicio TEXT NOT NULL, data_fim TEXT NOT NULL, tipo TEXT,
  permite_compra INTEGER DEFAULT 1, permite_venda INTEGER DEFAULT 1,
  permite_emprestimo INTEGER DEFAULT 1, permite_inscricao INTEGER DEFAULT 1, ativa INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS player_loans (
  loan_id TEXT PRIMARY KEY, player_id TEXT NOT NULL, clube_origem_id TEXT NOT NULL,
  clube_destino_id TEXT NOT NULL, data_inicio TEXT NOT NULL, data_fim TEXT NOT NULL,
  salario_pago_origem_percentual REAL DEFAULT 0, salario_pago_destino_percentual REAL DEFAULT 100,
  taxa_emprestimo REAL DEFAULT 0, opcao_compra INTEGER DEFAULT 0, valor_opcao_compra REAL,
  status TEXT DEFAULT 'Ativo'
);
CREATE TABLE IF NOT EXISTS financial_loans (
  financial_loan_id TEXT PRIMARY KEY, clube_id TEXT NOT NULL, valor_principal REAL NOT NULL,
  juros_mensal REAL NOT NULL, prazo_meses INTEGER NOT NULL, parcela_mensal REAL NOT NULL,
  saldo_devedor REAL NOT NULL, data_inicio TEXT NOT NULL, data_fim TEXT NOT NULL,
  parcelas_pagas INTEGER DEFAULT 0, status TEXT DEFAULT 'Ativo'
);
CREATE TABLE IF NOT EXISTS financial_transactions (
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, clube_id TEXT NOT NULL, data TEXT NOT NULL,
  tipo TEXT NOT NULL, categoria TEXT NOT NULL, descricao TEXT NOT NULL,
  valor REAL NOT NULL, saldo_apos REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS match_substitutions (
  substitution_id INTEGER PRIMARY KEY AUTOINCREMENT, match_id TEXT NOT NULL, club_id TEXT NOT NULL,
  minuto INTEGER NOT NULL, player_out_id TEXT NOT NULL, player_in_id TEXT NOT NULL, funcao_nova TEXT
);
CREATE TABLE IF NOT EXISTS in_match_tactical_changes (
  change_id INTEGER PRIMARY KEY AUTOINCREMENT, match_id TEXT NOT NULL, club_id TEXT NOT NULL,
  minuto INTEGER NOT NULL, campo TEXT NOT NULL, valor_anterior TEXT, valor_novo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS season_calendar (
  event_id TEXT PRIMARY KEY, temporada INTEGER NOT NULL, data TEXT NOT NULL, tipo TEXT NOT NULL,
  competition_id TEXT, club_id TEXT, descricao TEXT, prioridade INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS club_season_registration (
  competition_id TEXT NOT NULL, temporada INTEGER NOT NULL, club_id TEXT NOT NULL,
  status TEXT DEFAULT 'Inscrito', PRIMARY KEY(competition_id,temporada,club_id)
);
CREATE TABLE IF NOT EXISTS season_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT, temporada INTEGER, club_id TEXT,
  competition_id TEXT, posicao TEXT, resultado TEXT, premio REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS training_plans (
  plan_id TEXT PRIMARY KEY, club_id TEXT NOT NULL, semana TEXT NOT NULL,
  foco TEXT NOT NULL, intensidade TEXT NOT NULL, descanso INTEGER DEFAULT 1,
  status TEXT DEFAULT 'Planejado'
);
CREATE TABLE IF NOT EXISTS news_items (
  news_id TEXT PRIMARY KEY, data TEXT NOT NULL, categoria TEXT NOT NULL,
  titulo TEXT NOT NULL, conteudo TEXT NOT NULL, club_id TEXT, lida INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS scouting_reports (
  report_id TEXT PRIMARY KEY, club_id TEXT NOT NULL, player_id TEXT NOT NULL,
  data TEXT NOT NULL, conhecimento INTEGER DEFAULT 25, nota_estimada REAL,
  potencial_estimado REAL, recomendacao TEXT, status TEXT DEFAULT 'Observando'
);
CREATE TABLE IF NOT EXISTS save_versions (
  version_id TEXT PRIMARY KEY, criado_em TEXT NOT NULL, nome TEXT NOT NULL,
  temporada INTEGER, rodada INTEGER, arquivo TEXT NOT NULL, observacao TEXT
);
CREATE TABLE IF NOT EXISTS competition_rule_presets (
  preset_id TEXT PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL,
  configuracao TEXT NOT NULL, criado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS match_replays (
  replay_id TEXT PRIMARY KEY, match_id TEXT NOT NULL, criado_em TEXT NOT NULL,
  placar TEXT NOT NULL, eventos TEXT NOT NULL, estatisticas TEXT NOT NULL
);
INSERT OR IGNORE INTO game_state(id, temporada, rodada_atual, iniciado) VALUES(1, 2026, 1, 0);
"""


class Database:
    def __init__(self, path: str | Path = "database/brasil_manager.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as conn:
            conn.executescript(TABLES_SQL)
            self._migrate(conn)

    def run_migrations(self) -> None:
        with closing(self.connect()) as conn:
            conn.executescript(TABLES_SQL)
            self._migrate(conn)

    @staticmethod
    def _migrate(conn) -> None:
        """Migrações aditivas: preservam integralmente saves existentes."""
        migrations = [
            ("jogadores", "status", "TEXT NOT NULL DEFAULT 'Disponível'"),
            ("escalacao", "funcao", "TEXT NOT NULL DEFAULT 'Função Padrão'"),
            ("game_state", "data_atual", "TEXT NOT NULL DEFAULT '2026-01-01'"),
            ("calendario", "fase", "TEXT"),
            ("calendario", "perna", "INTEGER NOT NULL DEFAULT 1"),
            ("calendario", "prioridade", "INTEGER NOT NULL DEFAULT 1"),
        ]
        for table, column, definition in migrations:
            columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
            if column not in columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def existing_ids(self) -> dict[str, set]:
        with closing(self.connect()) as conn:
            result = {}
            for table, pk in PRIMARY_KEYS.items():
                result[table] = {row[0] for row in conn.execute(f"SELECT {pk} FROM {table}")}
            return result

    def import_frames(self, data: dict[str, pd.DataFrame], filename: str, mode: str = "atualizar") -> dict[str, int]:
        counts = {}
        order = ("clubes", "competicoes", "jogadores", "calendario", "transferencias")
        with closing(self.connect()) as conn:
            try:
                conn.execute("BEGIN")
                for table in order:
                    if table not in data:
                        continue
                    df = data[table].copy()
                    for column in df.columns:
                        if pd.api.types.is_datetime64_any_dtype(df[column]):
                            df[column] = df[column].dt.strftime("%Y-%m-%d")
                    df = df.astype(object).where(pd.notna(df), None)
                    columns = list(df.columns)
                    placeholders = ", ".join("?" for _ in columns)
                    quoted = ", ".join(f'"{c}"' for c in columns)
                    pk = PRIMARY_KEYS[table]
                    if mode == "substituir":
                        conn.execute(f"DELETE FROM {table}")
                    if mode == "atualizar":
                        updates = ", ".join(f'"{c}"=excluded."{c}"' for c in columns if c != pk)
                        sql = f'INSERT INTO {table} ({quoted}) VALUES ({placeholders}) ON CONFLICT("{pk}") DO UPDATE SET {updates}'
                    else:
                        sql = f"INSERT INTO {table} ({quoted}) VALUES ({placeholders})"
                    conn.executemany(sql, df.itertuples(index=False, name=None))
                    conn.execute("INSERT INTO importacoes(arquivo,tabela,registros,modo) VALUES(?,?,?,?)", (filename, table, len(df), mode))
                    counts[table] = len(df)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return counts

    def replace_all_data(self, data: dict[str, pd.DataFrame], filename: str) -> dict[str, int]:
        """Substitui a base esportiva inteira e inicia um save limpo, em uma transação."""
        counts = {}
        insert_order = ("clubes", "competicoes", "jogadores", "calendario", "transferencias")
        delete_order = (
            "eventos_partida", "detalhes_partida", "movimentos_financeiros", "escalacao",
            "taticas", "classificacao", "transferencias", "calendario", "jogadores",
            "competicoes", "clubes",
        )
        with closing(self.connect()) as conn:
            try:
                conn.execute("BEGIN")
                for table in delete_order:
                    conn.execute(f"DELETE FROM {table}")
                for table in insert_order:
                    if table not in data:
                        continue
                    frame = data[table].copy()
                    for column in frame.columns:
                        if pd.api.types.is_datetime64_any_dtype(frame[column]):
                            frame[column] = frame[column].dt.strftime("%Y-%m-%d")
                    frame = frame.astype(object).where(pd.notna(frame), None)
                    columns = list(frame.columns)
                    if frame.empty:
                        counts[table] = 0
                        continue
                    placeholders = ", ".join("?" for _ in columns)
                    quoted = ", ".join(f'"{column}"' for column in columns)
                    conn.executemany(
                        f"INSERT INTO {table} ({quoted}) VALUES ({placeholders})",
                        frame.itertuples(index=False, name=None),
                    )
                    counts[table] = len(frame)
                    conn.execute(
                        "INSERT INTO importacoes(arquivo,tabela,registros,modo) VALUES(?,?,?,'substituir')",
                        (filename, table, len(frame)),
                    )
                competition = conn.execute(
                    "SELECT competition_id FROM competicoes ORDER BY competition_id LIMIT 1"
                ).fetchone()
                if competition:
                    club_ids = [row[0] for row in conn.execute("SELECT club_id FROM clubes ORDER BY club_id")]
                    conn.executemany(
                        "INSERT INTO classificacao(competition_id,club_id) VALUES(?,?)",
                        [(competition[0], club_id) for club_id in club_ids],
                    )
                conn.execute(
                    "UPDATE game_state SET user_club_id=NULL,temporada=2026,rodada_atual=1,iniciado=0 WHERE id=1"
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return counts

    def table_counts(self) -> dict[str, int]:
        with closing(self.connect()) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in PRIMARY_KEYS}

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        with closing(self.connect()) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def execute(self, sql: str, params: tuple = ()) -> None:
        with closing(self.connect()) as conn:
            conn.execute(sql, params)
            conn.commit()

    def executemany(self, sql: str, rows: list[tuple]) -> None:
        with closing(self.connect()) as conn:
            conn.executemany(sql, rows)
            conn.commit()

    def state(self) -> dict:
        return self.query("SELECT * FROM game_state WHERE id=1")[0]

    def choose_club(self, club_id: str) -> None:
        self.execute("UPDATE game_state SET user_club_id=?, iniciado=1 WHERE id=1", (club_id,))

    def save_tactic(self, club_id: str, tactic: dict) -> None:
        columns = ("formacao", "mentalidade", "estilo", "linha_defensiva", "pressao", "ritmo", "foco_ataque", "tipo_passe")
        values = tuple(tactic[column] for column in columns)
        updates = ", ".join(f"{column}=excluded.{column}" for column in columns)
        self.execute(
            f"INSERT INTO taticas(club_id,{','.join(columns)}) VALUES(?,{','.join('?' for _ in columns)}) "
            f"ON CONFLICT(club_id) DO UPDATE SET {updates}", (club_id, *values),
        )

    def get_tactic(self, club_id: str) -> dict:
        rows = self.query("SELECT * FROM taticas WHERE club_id=?", (club_id,))
        if rows:
            return rows[0]
        default = {"club_id": club_id, "formacao": "4-3-3", "mentalidade": "Equilibrada",
                   "estilo": "Equilibrado", "linha_defensiva": "Normal", "pressao": "Normal",
                   "ritmo": "Normal", "foco_ataque": "Misto", "tipo_passe": "Misto"}
        self.save_tactic(club_id, default)
        return default

    def save_lineup(self, club_id: str, formation: str, slots: list[str], player_ids: list[str], roles: list[str] | None = None) -> None:
        tactic = self.get_tactic(club_id)
        with closing(self.connect()) as conn:
            conn.execute("DELETE FROM escalacao WHERE club_id=?", (club_id,))
            conn.executemany(
                "INSERT INTO escalacao(club_id,slot,posicao,player_id,titular,funcao) VALUES(?,?,?,?,1,?)",
                [(club_id, index, position, player_id, (roles or ["Função Padrão"] * 11)[index - 1])
                 for index, (position, player_id) in enumerate(zip(slots, player_ids), 1)],
            )
            tactic["formacao"] = formation
            columns = ("formacao", "mentalidade", "estilo", "linha_defensiva", "pressao", "ritmo", "foco_ataque", "tipo_passe")
            conn.execute(
                f"INSERT OR REPLACE INTO taticas(club_id,{','.join(columns)}) VALUES(?,{','.join('?' for _ in columns)})",
                (club_id, *(tactic[column] for column in columns)),
            )
            conn.commit()

    def lineup(self, club_id: str) -> list[dict]:
        return self.query(
            "SELECT e.*,j.* FROM escalacao e JOIN jogadores j ON j.player_id=e.player_id "
            "WHERE e.club_id=? ORDER BY e.slot", (club_id,),
        )

    def next_user_match(self, club_id: str) -> dict | None:
        rows = self.query(
            "SELECT c.*,m.nome mandante_nome,v.nome visitante_nome FROM calendario c "
            "JOIN clubes m ON m.club_id=c.mandante_id JOIN clubes v ON v.club_id=c.visitante_id "
            "WHERE c.jogado=0 AND (c.mandante_id=? OR c.visitante_id=?) ORDER BY c.rodada,c.data LIMIT 1",
            (club_id, club_id),
        )
        return rows[0] if rows else None

    def record_match(self, result, events: tuple[str, ...]) -> None:
        with closing(self.connect()) as conn:
            try:
                conn.execute("BEGIN")
                pending = conn.execute("SELECT jogado FROM calendario WHERE match_id=?", (result.match_id,)).fetchone()
                if not pending or pending["jogado"]:
                    raise ValueError("Esta partida já foi simulada.")
                conn.execute(
                    "UPDATE calendario SET jogado=1,gols_mandante=?,gols_visitante=? WHERE match_id=?",
                    (result.home_goals, result.away_goals, result.match_id),
                )
                conn.executemany(
                    "INSERT INTO eventos_partida(match_id,ordem,evento) VALUES(?,?,?)",
                    [(result.match_id, index, event) for index, event in enumerate(events)],
                )
                conn.execute(
                    "INSERT OR REPLACE INTO detalhes_partida(match_id,estatisticas,melhor_jogador,artilheiros) VALUES(?,?,?,?)",
                    (result.match_id, json.dumps(result.statistics, ensure_ascii=False),
                     result.best_player, json.dumps(result.scorers, ensure_ascii=False)),
                )
                self._update_standing(conn, result.home_id, result.home_goals, result.away_goals)
                self._update_standing(conn, result.away_id, result.away_goals, result.home_goals)
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    @staticmethod
    def _update_standing(conn, club_id: str, goals_for: int, goals_against: int) -> None:
        win, draw, loss = int(goals_for > goals_against), int(goals_for == goals_against), int(goals_for < goals_against)
        conn.execute(
            "UPDATE classificacao SET jogos=jogos+1,vitorias=vitorias+?,empates=empates+?,derrotas=derrotas+?,"
            "gols_pro=gols_pro+?,gols_contra=gols_contra+?,saldo=saldo+?,pontos=pontos+? WHERE club_id=?",
            (win, draw, loss, goals_for, goals_against, goals_for - goals_against, win * 3 + draw, club_id),
        )

    def add_finance(self, club_id: str, kind: str, description: str, value: float, when: str) -> None:
        with closing(self.connect()) as conn:
            conn.execute(
                "INSERT INTO movimentos_financeiros(club_id,data,tipo,descricao,valor) VALUES(?,?,?,?,?)",
                (club_id, when, kind, description, value),
            )
            conn.execute("UPDATE clubes SET saldo_caixa=saldo_caixa+? WHERE club_id=?", (value, club_id))
            conn.commit()

    def complete_transfer(self, record: dict) -> None:
        with closing(self.connect()) as conn:
            try:
                conn.execute("BEGIN")
                buyer = conn.execute("SELECT * FROM clubes WHERE club_id=?", (record["clube_destino_id"],)).fetchone()
                if not buyer or buyer["orcamento_transferencias"] < record["valor"]:
                    raise ValueError("Orçamento insuficiente.")
                conn.execute(
                    "INSERT INTO transferencias(transfer_id,player_id,clube_origem_id,clube_destino_id,valor,salario_novo,data,tipo)"
                    " VALUES(:transfer_id,:player_id,:clube_origem_id,:clube_destino_id,:valor,:salario_novo,:data,:tipo)", record,
                )
                conn.execute(
                    "UPDATE jogadores SET clube_id=?,salario=? WHERE player_id=?",
                    (record["clube_destino_id"], record["salario_novo"], record["player_id"]),
                )
                conn.execute(
                    "UPDATE clubes SET orcamento_transferencias=orcamento_transferencias-?,saldo_caixa=saldo_caixa-? WHERE club_id=?",
                    (record["valor"], record["valor"], record["clube_destino_id"]),
                )
                if record["clube_origem_id"]:
                    conn.execute(
                        "UPDATE clubes SET saldo_caixa=saldo_caixa+? WHERE club_id=?",
                        (record["valor"], record["clube_origem_id"]),
                    )
                conn.executemany(
                    "INSERT INTO movimentos_financeiros(club_id,data,tipo,descricao,valor) VALUES(?,?,?,?,?)",
                    [
                        (record["clube_destino_id"], record["data"], "Transferência", f"Compra de {record['player_id']}", -record["valor"]),
                        (record["clube_origem_id"], record["data"], "Transferência", f"Venda de {record['player_id']}", record["valor"]),
                    ] if record["clube_origem_id"] else [
                        (record["clube_destino_id"], record["data"], "Transferência", f"Contratação de {record['player_id']}", -record["valor"])
                    ],
                )
                conn.execute("DELETE FROM escalacao WHERE player_id=?", (record["player_id"],))
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def new_save(self) -> None:
        """Reinicia somente o progresso; clubes e jogadores importados são preservados."""
        with closing(self.connect()) as conn:
            try:
                conn.execute("BEGIN")
                conn.execute("UPDATE calendario SET jogado=0,gols_mandante=NULL,gols_visitante=NULL")
                conn.execute("UPDATE classificacao SET jogos=0,vitorias=0,empates=0,derrotas=0,gols_pro=0,gols_contra=0,saldo=0,pontos=0")
                for table in ("eventos_partida", "detalhes_partida", "movimentos_financeiros", "escalacao", "taticas"):
                    conn.execute(f"DELETE FROM {table}")
                conn.execute("UPDATE jogadores SET moral=70,condicao_fisica=95,status='Disponível'")
                conn.execute("UPDATE game_state SET user_club_id=NULL,rodada_atual=1,iniciado=0 WHERE id=1")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
