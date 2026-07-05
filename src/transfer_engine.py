from datetime import date
import uuid


def evaluate_offer(player: dict, buyer: dict, value: float, salary: float) -> tuple[bool, str]:
    market = float(player.get("valor_mercado") or 0)
    current_salary = float(player.get("salario") or 0)
    if value < market * 0.8:
        return False, "O clube vendedor recusou: proposta abaixo do valor esperado."
    if value > float(buyer.get("orcamento_transferencias") or 0):
        return False, "O clube não possui orçamento de transferências suficiente."
    if salary < current_salary * 0.9:
        return False, "O jogador recusou a redução salarial."
    return True, "Proposta aceita."


def transfer_record(player_id: str, origin_id: str | None, destination_id: str,
                    value: float, salary: float, kind: str = "COMPRA") -> dict:
    return {"transfer_id": f"T-{uuid.uuid4().hex[:10]}", "player_id": player_id,
            "clube_origem_id": origin_id, "clube_destino_id": destination_id,
            "valor": value, "salario_novo": salary, "data": date.today().isoformat(), "tipo": kind}


def active_transfer_window(database, on_date, operation="compra"):
    field = {"compra": "permite_compra", "venda": "permite_venda", "emprestimo": "permite_emprestimo"}[operation]
    rows = database.query(
        f"SELECT * FROM transfer_windows WHERE ativa=1 AND {field}=1 AND ? BETWEEN data_inicio AND data_fim ORDER BY data_inicio",
        (on_date,),
    )
    return rows[0] if rows else None


def create_player_loan(database, player_id, origin_id, destination_id, start, end,
                       destination_salary_percent, fee=0, purchase_option=None):
    import uuid

    if not active_transfer_window(database, start, "emprestimo"):
        return False, "A janela de transferências está fechada para empréstimos."
    loan_id = f"PL-{uuid.uuid4().hex[:10]}"
    database.execute(
        "INSERT INTO player_loans(loan_id,player_id,clube_origem_id,clube_destino_id,data_inicio,data_fim,"
        "salario_pago_origem_percentual,salario_pago_destino_percentual,taxa_emprestimo,opcao_compra,"
        "valor_opcao_compra,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,'Ativo')",
        (loan_id, player_id, origin_id, destination_id, start, end, 100-destination_salary_percent,
         destination_salary_percent, fee, int(purchase_option is not None), purchase_option),
    )
    database.execute("UPDATE jogadores SET clube_id=? WHERE player_id=?", (destination_id, player_id))
    if fee:
        database.add_finance(origin_id, "Empréstimo", f"Taxa de empréstimo {player_id}", fee, start)
        database.add_finance(destination_id, "Empréstimo", f"Taxa de empréstimo {player_id}", -fee, start)
    return True, "Empréstimo de jogador registrado."


def return_expired_player_loans(database, on_date):
    loans = database.query("SELECT * FROM player_loans WHERE status='Ativo' AND data_fim<=?", (on_date,))
    for loan in loans:
        database.execute("UPDATE jogadores SET clube_id=? WHERE player_id=?", (loan["clube_origem_id"], loan["player_id"]))
        database.execute("UPDATE player_loans SET status='Encerrado' WHERE loan_id=?", (loan["loan_id"],))
    return len(loans)
