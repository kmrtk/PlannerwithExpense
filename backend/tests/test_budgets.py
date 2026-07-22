from tests.conftest import auth_headers, register_user


def create_expense(client, token, *, type_, amount, expense_date, category="テスト"):
    response = client.post(
        "/api/expenses",
        json={"type": type_, "amount": amount, "date": expense_date, "category": category},
        headers=auth_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_yearly_summary_aggregates_income_and_expense_by_month(client):
    token = register_user(client, "yearly-summary@example.com")
    create_expense(client, token, type_="income", amount=1000, expense_date="2026-03-01")
    create_expense(client, token, type_="income", amount=500, expense_date="2026-03-15")
    create_expense(client, type_="expense", amount=300, expense_date="2026-03-20", token=token)
    create_expense(client, token, type_="expense", amount=200, expense_date="2026-07-01")
    # 別年のデータは集計に含まれないこと
    create_expense(client, token, type_="income", amount=9999, expense_date="2025-03-01")

    response = client.get("/api/budgets/yearly", params={"year": 2026}, headers=auth_headers(token))
    assert response.status_code == 200
    summary = {row["month"]: row for row in response.json()}

    assert summary[3]["actual_income"] == 1500
    assert summary[3]["actual_expense"] == 300
    assert summary[7]["actual_income"] == 0
    assert summary[7]["actual_expense"] == 200
    # データのない月は0で埋まっていること
    assert summary[1]["actual_income"] == 0
    assert summary[1]["actual_expense"] == 0


def test_all_time_summary_aggregates_across_years(client):
    token = register_user(client, "all-time-summary@example.com")
    create_expense(client, token, type_="income", amount=2000, expense_date="2024-01-01")
    create_expense(client, token, type_="expense", amount=500, expense_date="2024-06-01")
    create_expense(client, token, type_="income", amount=1000, expense_date="2026-12-31")

    response = client.get("/api/budgets/all-time-summary", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()

    assert body["start_year"] == 2024
    assert body["end_year"] == 2026
    assert body["total_savings"] == 2000 - 500 + 1000


def test_all_time_summary_with_no_expenses_returns_none_years(client):
    token = register_user(client, "no-expenses@example.com")

    response = client.get("/api/budgets/all-time-summary", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.json()

    assert body["start_year"] is None
    assert body["end_year"] is None
    assert body["total_savings"] == 0
