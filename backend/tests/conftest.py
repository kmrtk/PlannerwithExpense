import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app import models  # noqa: F401  (テーブル登録のためimportが必要)
from app.database import Base, engine, get_db
from app.main import app
from app.rate_limit import limiter


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # app/limiterはテストセッション全体で共有されるため、テスト間で
    # レート制限の状態が持ち越されないようにリセットする
    limiter.reset()
    yield


@pytest.fixture
def db_session():
    # アプリのエンドポイントはリクエストごとに db.commit() を呼ぶため、
    # 外側のトランザクションをSAVEPOINTでラップし、commitのたびに
    # 新しいSAVEPOINTを開始し直すことでテスト全体のロールバックを保証する。
    # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def register_user(client: TestClient, email: str, password: str = "password123", name: str | None = None) -> str:
    payload = {"email": email, "password": password}
    if name is not None:
        payload["name"] = name
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
