# DBマイグレーション(Alembic)動作検証記録

## 検証日
2026-07-16

## 対象
Issue #30 / PR #34（Alembic導入）

## 検証環境
`docker compose up --build`（worktree: `PlannerwithExpense-alembic`、フレッシュな新規ボリューム）

## 検証内容と結果

| 項目 | 結果 |
|------|------|
| `docker compose up --build`でbackend/mysql/frontendが起動するか | OK |
| backend起動時に`alembic upgrade head`が自動実行されるか | OK（ログ: `Running upgrade  -> 0001, initial schema`） |
| `alembic current`が`0001 (head)`を指しているか | OK |
| MySQL上に`user`/`schedule`/`expense`/`budget`/`alembic_version`テーブルが作成されているか | OK（カラム定義・外部キー・ユニーク制約も想定通り） |
| APIヘルスチェック(`/api/health`) | OK（200） |
| ユーザー登録→ログイン→支出登録→一覧取得のE2E動作 | OK（新規DBから一連の操作が正常に完了） |

## 補足
- 初期マイグレーション(`0001_initial_schema.py`)は`alembic revision --autogenerate`ではなく、既存モデル定義から手動で作成したもの
- 検証時、メインリポジトリ側の`docker compose`スタックは一時停止し、検証後に復旧している(ポート競合回避のため)
- バリデーション強化・テスト導入の残り2項目についても、同様の手順でPR作成後に検証予定
