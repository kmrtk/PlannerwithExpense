import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app import models  # noqa: F401  (テーブル登録のためimportが必要)
from app.database import Base, engine
from app.routers import auth, budgets, expenses, schedules

app = FastAPI(title="PlannerwithExpense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 既存のHTTPExceptionはdetailが文字列のため、フロントエンドが同じ形式で
    # 表示できるようバリデーションエラーも1つの文字列にまとめて返す
    messages = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        messages.append(f"{field}: {error['msg']}" if field else error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": " / ".join(messages)},
    )


@app.on_event("startup")
def on_startup():
    # MySQLは初回起動時に一時サーバーでの初期化→本サーバーへの再起動という
    # 2段階を踏むため、healthcheck通過直後でも接続拒否されることがある。
    # 起動直後の一時的な接続失敗を吸収するためリトライする。
    last_error: Exception | None = None
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(3)
    raise last_error


app.include_router(auth.router)
app.include_router(schedules.router)
app.include_router(expenses.router)
app.include_router(budgets.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
