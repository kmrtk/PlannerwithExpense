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

## テスト実行方法

バックエンド(pytest、実際のMySQLに接続してテストごとにトランザクションをロールバックする):

```
docker compose exec backend pytest
```

フロントエンド(vitest):

```
docker compose exec frontend npm test
```

## 環境変数

| 変数名 | 説明 | 既定値 |
|--------|------|--------|
| JWT_SECRET | JWT署名用シークレット | devsecret-change-me(本番では必ず変更) |

## 今後の課題

- Alembicによるマイグレーション管理の導入(現状はスキーマ変更のたびに`docker compose down -v`でDBを再作成している)
- 入力バリデーションの強化
- AWS環境へのデプロイ

開発中に発生した問題と対処法は[docs/07_troubleshooting.md](docs/07_troubleshooting.md)を参照。
