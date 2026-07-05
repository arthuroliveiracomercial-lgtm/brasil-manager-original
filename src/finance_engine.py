def match_revenue(club: dict, home_goals: int, away_goals: int) -> float:
    capacity = float(club.get("capacidade_estadio") or 20000)
    reputation = float(club.get("reputacao") or 50)
    occupancy = min(0.95, 0.35 + reputation / 150 + (0.05 if home_goals > away_goals else 0))
    return round(capacity * occupancy * (25 + reputation * 0.25), 2)


def monthly_payroll(players: list[dict]) -> float:
    return sum(float(player.get("salario") or 0) for player in players)


def format_brl(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def loan_installment(principal, monthly_rate, months):
    rate = monthly_rate / 100
    if rate == 0:
        return principal / months
    return principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)


def request_financial_loan(database, club_id, principal, months, monthly_rate, start_date):
    from datetime import date
    import uuid

    club = database.query("SELECT * FROM clubes WHERE club_id=?", (club_id,))[0]
    limit = max(500_000, club["reputacao"] * max(1, club["saldo_caixa"]) * 0.08)
    if principal > limit:
        return False, f"Crédito negado. Limite estimado: {format_brl(limit)}"
    installment = loan_installment(principal, monthly_rate, months)
    end_year = int(start_date[:4]) + (int(start_date[5:7]) - 1 + months) // 12
    end_month = (int(start_date[5:7]) - 1 + months) % 12 + 1
    loan_id = f"FL-{uuid.uuid4().hex[:10]}"
    database.execute(
        "INSERT INTO financial_loans(financial_loan_id,clube_id,valor_principal,juros_mensal,prazo_meses,"
        "parcela_mensal,saldo_devedor,data_inicio,data_fim) VALUES(?,?,?,?,?,?,?,?,?)",
        (loan_id, club_id, principal, monthly_rate, months, installment, principal,
         start_date, f"{end_year:04d}-{end_month:02d}-01"),
    )
    database.add_finance(club_id, "Crédito", "Empréstimo bancário", principal, start_date)
    return True, f"Crédito liberado. Parcela mensal: {format_brl(installment)}"


def processar_fechamento_mensal(database, club_id, closing_date):
    month_key = closing_date[:7]
    already = database.query(
        "SELECT 1 FROM financial_transactions WHERE clube_id=? AND categoria='Fechamento mensal' AND substr(data,1,7)=?",
        (club_id, month_key),
    )
    if already:
        return {"processado": False, "mensagem": "Este mês já foi processado."}
    club = database.query("SELECT * FROM clubes WHERE club_id=?", (club_id,))[0]
    players = database.query("SELECT salario FROM jogadores WHERE clube_id=?", (club_id,))
    payroll = monthly_payroll(players)
    maintenance = float(club["capacidade_estadio"] or 20000) * 8
    operations = max(100_000, float(club["reputacao"] or 50) * 7_500)
    sponsorship = max(250_000, float(club["reputacao"] or 50) * 22_000)
    items = [("Receita", "Patrocínio", sponsorship), ("Despesa", "Salários", -payroll),
             ("Despesa", "Manutenção do estádio", -maintenance), ("Despesa", "Custos operacionais", -operations)]
    loans = database.query("SELECT * FROM financial_loans WHERE clube_id=? AND status='Ativo'", (club_id,))
    for loan in loans:
        payment = min(loan["parcela_mensal"], loan["saldo_devedor"])
        items.append(("Despesa", f"Parcela {loan['financial_loan_id']}", -payment))
        database.execute(
            "UPDATE financial_loans SET saldo_devedor=MAX(0,saldo_devedor-?),parcelas_pagas=parcelas_pagas+1,"
            "status=CASE WHEN saldo_devedor-?<=0 THEN 'Quitado' ELSE status END WHERE financial_loan_id=?",
            (payment, payment, loan["financial_loan_id"]),
        )
    balance = float(club["saldo_caixa"])
    for kind, category, value in items:
        balance += value
        database.execute("UPDATE clubes SET saldo_caixa=? WHERE club_id=?", (balance, club_id))
        database.execute(
            "INSERT INTO financial_transactions(clube_id,data,tipo,categoria,descricao,valor,saldo_apos)"
            " VALUES(?,?,?,?,?,?,?)",
            (club_id, closing_date, kind, "Fechamento mensal", category, value, balance),
        )
    return {"processado": True, "receitas": sponsorship, "despesas": payroll + maintenance + operations + sum(-x[2] for x in items[4:]),
            "saldo": balance, "itens": items}
