# PlannerwithExpense

家族向け予定・家計簿アプリ。

## アーキテクチャ

3層構成。フロントエンドはMySQLに直接アクセスせず、必ずバックエンドAPI経由でデータを操作する。

```
ブラウザ (Vue3 + Vite, :5173)
   │  fetch/axios → /api/*
   ▼
バックエンドAPI (FastAPI, :8000)
   │  SQLAlchemy
   ▼
MySQL (:3306)
```

## 主な機能

- ユーザー認証(メール＋パスワードでの新規登録・ログイン、JWT)
- カレンダー(月表示/週表示切り替え、月送り・週送りナビゲーション、日付セルの集約表示「予定あり/支出あり/収入あり」、日別詳細モーダルでの予定・家計簿の追加・編集・削除)
- 予定管理(繰り返し予定の登録(毎週・毎月、終了日指定可)、月別一覧表示)
- 家計簿(収入・支出の区分管理、カテゴリのプリセット選択/自由入力、追加・編集・削除、CSVエクスポート、年月フィルタ一覧)
- 財務状況管理(月ごとの貯蓄目標設定、実際の収入・支出・貯蓄額との比較表示、年別/全期間の財務状況サマリー)
- ナビゲーション(折りたたみ式サイドバー、カレンダー・家計簿の年→月階層ナビゲーション)

## 技術スタック

| 種類 | 技術 |
|------|------|
| フロントエンド | Vue3 + Vite + Pinia + vue-router |
| バックエンド | FastAPI + SQLAlchemy + JWT認証 |
| データベース | MySQL 8.0 |
| インフラ | Docker Compose |

## 起動方法

```
cp .env.example .env
docker compose up --build
```

- フロントエンド: http://localhost:5173
- バックエンドAPI(Swagger UI): http://localhost:8000/docs

## 環境変数

| 変数名 | 説明 | 既定値 |
|--------|------|--------|
| JWT_SECRET | JWT署名用シークレット | devsecret-change-me(本番では必ず変更) |

## DBマイグレーション

スキーマ変更はAlembicで管理する(`backend/alembic/`)。バックエンド起動時に自動で`alembic upgrade head`が実行されるため、`docker compose up`するだけで最新スキーマが適用される。

モデル(`backend/app/models/`)を変更した場合は、以下の手順でマイグレーションファイルを作成しコミットする。

```
docker compose exec backend alembic revision --autogenerate -m "変更内容の説明"
```

生成されたファイルは`backend/alembic/versions/`配下に作成される。適用はバックエンド再起動時に自動で行われる(手動で適用したい場合は`docker compose exec backend alembic upgrade head`)。

> **移行時の注意**: Alembic導入前に`create_all()`で作成された(Alembic管理外の)DBが残っている環境では、次回`docker compose up`前に一度だけ`docker compose down -v`でボリュームを削除してから起動すること。以降はマイグレーションで管理されるため`down -v`は不要になる。

## 入力バリデーション

金額・自由入力テキストに対するバリデーションをバックエンド・フロントエンド両方に実装している。

- 金額系フィールド(支出・収入の金額、貯蓄目標): マイナス・ゼロを禁止し、上限値を設定
- 自由入力フィールド(カテゴリ・タイトル・メモ): 文字数制限(DBカラムサイズと整合)、前後の空白除去、空文字を禁止
- 予定の開始日時・終了日時・繰り返し終了日の前後関係チェック
- バックエンドのバリデーションエラー(422)は、既存の`HTTPException`と同じ形式(`detail`が文字列)で返るよう統一し、フロントエンドの各モーダルで保存失敗時にエラーメッセージを表示する

検証内容・結果は[docs/input-validation-test.md](docs/input-validation-test.md)を参照。

## 今後の課題

- テスト導入(backend: pytest、frontend: vitest)
- AWS環境へのデプロイ

開発中に発生した問題と対処法は[docs/07_troubleshooting.md](docs/07_troubleshooting.md)を参照。
