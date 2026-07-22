# 品質チェック結果（quality-check3）

`~/.claude/commands/quality-check.md`（GitHub `claude-config` にバックアップ済み）に沿って実施。

対象は `docs/quality-check.md` の「4回目：Low優先度項目の対応（2026-07-22）」で選定された対応ファイルのうち、以下2グループ。マージ済みPRの実装内容を、実装セッションとは別に軽く確認する。

- フロントエンド（PR #93）: `frontend/src/api/client.js`, `frontend/src/components/AppSidebar.vue`, `frontend/src/views/ExpensesView.vue`
- バックエンド（PR #95・#97）: `backend/requirements.txt`, `backend/pyproject.toml`, `backend/app/routers/budgets.py`, `backend/tests/test_budgets.py`

## 検出した技術スタック

- フロントエンド: Vue 3 + Vite（ESLint導入済み）
- バックエンド: FastAPI + SQLAlchemy（ruff導入済み、pytest）
- DB: MySQL（Docker Compose、`plannerwithexpense-backend-1` コンテナ上で実行）

## チェック結果

| カテゴリ | チェック項目 | 結果 | 備考 |
|---|---|---|---|
| フロントエンド | Lint（`npm run lint`） | ✅ | エラーなし |
| フロントエンド | ビルド（`npm run build`） | ✅ | 105 modules変換、正常終了 |
| フロントエンド | テスト（`npm run test`） | ✅ | vitest 8件パス（既存分、対象ファイルへの単体テストはなし） |
| フロントエンド | コードパターン | ✅ | 下記詳細参照 |
| バックエンド | Lint（`ruff check app tests`） | ✅ | All checks passed! |
| バックエンド | テスト（`pytest tests/test_budgets.py`） | ✅ | 3 passed |
| バックエンド | テスト（`pytest` 全体） | ✅ | 17 passed（回帰なし） |
| バックエンド | コードパターン | ✅ | 下記詳細参照 |
| 共通 | シークレット漏洩 | ✅ | 対象7ファイルに該当なし |
| 共通 | デバッグコード残存（`console.log`/`print`/`debugger`） | ✅ | 該当なし |
| 共通 | TODOコメント残存 | ✅ | 該当なし |

### フロントエンド コードパターン詳細

- `client.js`: 401時に既存の `auth.logout()` に加えて `router.push({ name: "login" })` を追加。レスポンスインターセプター内で同期的に呼んでおり、`Promise.reject(error)` より前に実行されるため画面遷移の意図通り。問題なし。
- `AppSidebar.vue`: サイドバー開閉ボタン・カレンダー/家計簿の年月ナビゲーションchevron（計3箇所）の `aria-label` が `sidebar.isOpen` / `expandedSection` の状態に応じて日本語で正しく切り替わることを確認。問題なし。
- `ExpensesView.vue`: `handleDelete` / `handleDeleteFromModal` をtry/catchで囲み、失敗時は既存の `loadError` にメッセージをセットする実装。`fetchExpenses` 成功時に `loadError.value = ""` でクリアされるため、削除成功後の再取得でエラー表示が正しく消える。問題なし。

### バックエンド コードパターン詳細

- `requirements.txt` / `pyproject.toml`: `ruff==0.9.4` を追加し、`select = ["E4","E7","E9","F"]`（pyflakes + 明確なバグにつながるpycodestyleエラーのみ）に限定。フロントのESLint導入時と同じ「書式ルールは追加しない」方針が守られている。整合性あり。
- `budgets.py`: `get_yearly_summary` / `get_all_time_summary` をPython側集計からSQLAlchemyの `func.sum()` + `case()` + `group_by` によるDB側集計に変更。`get_all_time_summary` の `result.total_income or 0` / `result.total_expense or 0` はデータなし時に `result.start_year is None` で早期returnするため到達しないが、念のためのNone防御として妥当。
- `test_budgets.py`: 別年データが集計に含まれないこと、月次結果が0埋めされること、データなし時に `start_year`/`end_year` が `None` になることをそれぞれ検証しており、DB側集計への変更前後で挙動が変わっていないことを回帰テストとして確認できる内容になっている。

## 問題点一覧（優先度順）

検出なし: Critical / High / Medium / Low

今回確認した7ファイルの範囲では新たな指摘事項はなし。既存の未対応Low項目（`mypy`/`flake8`未導入、`on_event`非推奨API等）は `docs/quality-check.md` の「未対応項目一覧」を参照。
