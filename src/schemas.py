from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Field:
    required: bool = True
    kind: str = "text"
    nullable: bool = False
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple[str, ...] = field(default_factory=tuple)
    default: Any = None


RATING = Field(kind="int", minimum=0, maximum=100)
MONEY = Field(kind="float", minimum=0)
POSICOES = ("GOL", "ZAG", "LAT", "ALA", "VOL", "MC", "MEI", "PE", "PD", "ATA")

SCHEMAS: dict[str, dict[str, Field]] = {
    "clubes": {
        "club_id": Field(kind="id"),
        "nome": Field(),
        "nome_curto": Field(required=False, nullable=True),
        "estado": Field(),
        "cidade": Field(),
        "divisao": Field(),
        "estadio": Field(required=False, nullable=True),
        "capacidade_estadio": Field(kind="int", minimum=0),
        "reputacao": RATING,
        "orcamento_transferencias": MONEY,
        "folha_salarial_maxima": MONEY,
        "saldo_caixa": Field(required=False, kind="float", minimum=0, default=0),
        "categoria_base": Field(required=False, kind="int", minimum=0, maximum=100, default=50),
        "rival_1": Field(required=False, kind="id", nullable=True),
        "rival_2": Field(required=False, kind="id", nullable=True),
    },
    "jogadores": {
        "player_id": Field(kind="id"),
        "nome": Field(),
        "apelido": Field(required=False, nullable=True),
        "clube_id": Field(kind="id"),
        "idade": Field(kind="int", minimum=15, maximum=50),
        "nascimento": Field(required=False, kind="date", nullable=True),
        "nacionalidade": Field(required=False, default="Brasil"),
        "posicao_principal": Field(choices=POSICOES),
        "posicoes_secundarias": Field(required=False, nullable=True),
        "pe_preferido": Field(required=False, choices=("D", "E", "AMBOS"), nullable=True),
        "altura": Field(required=False, kind="float", minimum=1.4, maximum=2.3, nullable=True),
        "peso": Field(required=False, kind="float", minimum=45, maximum=130, nullable=True),
        "valor_mercado": MONEY,
        "salario": MONEY,
        "contrato_inicio": Field(required=False, kind="date", nullable=True),
        "contrato_fim": Field(required=False, kind="date", nullable=True),
        **{name: Field(required=False, kind="int", minimum=0, maximum=100, nullable=True)
           for name in (
               "reputacao potencial moral condicao_fisica ritmo finalizacao passe tecnica "
               "marcacao desarme cruzamento drible cabeceio forca resistencia velocidade "
               "aceleracao decisao trabalho_equipe lideranca goleiro_reflexos "
               "goleiro_posicionamento goleiro_jogo_maos"
           ).split()},
    },
    "competicoes": {
        "competition_id": Field(kind="id"),
        "nome": Field(),
        "tipo": Field(choices=("LIGA", "COPA")),
        "pais": Field(required=False, default="Brasil"),
        "divisao": Field(required=False, nullable=True),
        "formato": Field(),
        "numero_times": Field(kind="int", minimum=2, maximum=200),
        "acesso": Field(required=False, kind="int", minimum=0, default=0),
        "rebaixamento": Field(required=False, kind="int", minimum=0, default=0),
        "premio_campeao": Field(required=False, kind="float", minimum=0, default=0),
        "premio_participacao": Field(required=False, kind="float", minimum=0, default=0),
    },
    "calendario": {
        "match_id": Field(kind="id"),
        "competition_id": Field(kind="id"),
        "rodada": Field(kind="int", minimum=1),
        "data": Field(kind="date"),
        "mandante_id": Field(kind="id"),
        "visitante_id": Field(kind="id"),
        "estadio": Field(required=False, nullable=True),
        "jogado": Field(required=False, kind="bool", default=False),
        "gols_mandante": Field(required=False, kind="int", minimum=0, nullable=True),
        "gols_visitante": Field(required=False, kind="int", minimum=0, nullable=True),
    },
    "transferencias": {
        "transfer_id": Field(kind="id"),
        "player_id": Field(kind="id"),
        "clube_origem_id": Field(kind="id", nullable=True),
        "clube_destino_id": Field(kind="id", nullable=True),
        "valor": Field(kind="float", minimum=0),
        "salario_novo": Field(required=False, kind="float", minimum=0, nullable=True),
        "data": Field(kind="date"),
        "tipo": Field(choices=("COMPRA", "EMPRESTIMO", "LIVRE")),
    },
}

PRIMARY_KEYS = {
    "clubes": "club_id",
    "jogadores": "player_id",
    "competicoes": "competition_id",
    "calendario": "match_id",
    "transferencias": "transfer_id",
}

