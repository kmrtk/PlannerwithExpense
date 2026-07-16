from tests.conftest import auth_headers, register_user


def test_user_cannot_access_another_users_expense(client):
    token_a = register_user(client, "expense-owner@example.com")
    token_b = register_user(client, "expense-other@example.com")

    create_response = client.post(
        "/api/expenses",
        json={"type": "expense", "amount": 1000, "date": "2026-07-01", "category": "food"},
        headers=auth_headers(token_a),
    )
    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    get_response = client.get("/api/expenses", headers=auth_headers(token_b))
    assert get_response.status_code == 200
    assert expense_id not in [e["id"] for e in get_response.json()]

    update_response = client.put(
        f"/api/expenses/{expense_id}",
        json={"type": "expense", "amount": 2000, "date": "2026-07-01", "category": "food"},
        headers=auth_headers(token_b),
    )
    assert update_response.status_code == 404

    delete_response = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers(token_b))
    assert delete_response.status_code == 404


def test_user_cannot_access_another_users_schedule(client):
    token_a = register_user(client, "schedule-owner@example.com")
    token_b = register_user(client, "schedule-other@example.com")

    create_response = client.post(
        "/api/schedules",
        json={"title": "打ち合わせ", "start_datetime": "2026-07-01T10:00:00"},
        headers=auth_headers(token_a),
    )
    assert create_response.status_code == 201
    schedule_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/schedules/{schedule_id}",
        json={"title": "乗っ取り", "start_datetime": "2026-07-01T10:00:00"},
        headers=auth_headers(token_b),
    )
    assert update_response.status_code == 404

    delete_response = client.delete(f"/api/schedules/{schedule_id}", headers=auth_headers(token_b))
    assert delete_response.status_code == 404
