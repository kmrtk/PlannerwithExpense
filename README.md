# PlannerwithExpense

家族向け予定・家計簿アプリ。

## デモ

ログイン画面

<img width="1355" height="634" alt="ログイン画面" src="https://github.com/user-attachments/assets/f8d89385-2f61-43e1-8ece-fe95dd3c8167" />

ログイン後の操作デモ

https://github.com/user-attachments/assets/d43f8059-c6fa-43f8-8c49-d0bda23732fb

CSVエクスポート結果（ダミーデータ）

<img width="1365" height="647" alt="CSVエクスポート結果" src="https://github.com/user-attachments/assets/e8553442-d1dd-4dd8-b5ff-28df560aadb2" />

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

- ユーザー認証(メール＋パスワードでの新規登録・ログイン、JWT、認証エラー時のログイン画面への自動遷移)
- カレンダー(月表示/週表示切り替え、月送り・週送りナビゲーション、日付セルの集約表示「予定あり/支出あり/収入あり」、日別詳細モーダルでの予定・家計簿の追加・編集・削除)
- 予定管理(繰り返し予定の登録(毎週・毎月、終了日指定可)、月別一覧表示)
- 家計簿(収入・支出の区分管理、カテゴリのプリセット選択/自由入力、追加・編集・削除、CSVエクスポート、年月フィルタ一覧(月/週表示切り替え)、日付での並び替え・黒字/赤字抽出、同じ日の予定との紐付け(任意)、金額はキーボード直接入力に加え電卓ボタンからの入力にも対応)
- 財務状況管理(月ごとの貯蓄目標設定、実際の収入・支出・貯蓄額との比較表示、年別/全期間の財務状況サマリー)
- ナビゲーション(折りたたみ式サイドバー、カレンダー・家計簿の年→月階層ナビゲーション)
- UI(Google Fonts「M PLUS Rounded 1c」による丸ゴシック系フォントで統一)

## 技術スタック

| 種類 | 技術 |
|------|------|
| フロントエンド | Vue3 + Vite + Pinia + vue-router |
| バックエンド | FastAPI + SQLAlchemy + JWT認証 |
| データベース | MySQL 8.0 |
| インフラ | Docker Compose（ローカル）／ AWS EC2 + RDS（Terraform、本番相当デプロイ） |

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
| ENVIRONMENT | 実行環境(development/production) | development |
| CORS_ORIGINS | 許可するオリジン(カンマ区切りで複数指定可) | http://localhost:5173 |

`ENVIRONMENT=production`かつ`JWT_SECRET`が既定値のままの場合、起動時にエラーとなりアプリが立ち上がらない(既知の値でのトークン偽造を防ぐため)。他人がアクセスできる環境にデプロイする際は、`JWT_SECRET`を強力な値に変更した上で`ENVIRONMENT=production`を設定すること。

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

## テスト

バックエンド(pytest)・フロントエンド(vitest)ともに自動テストを導入している。

- バックエンド: ユーザー登録・ログイン、所有者スコープ(他ユーザーのデータが見えないこと)のテスト。テスト用のDB接続はSQLite等の代替ではなく、アプリの通常のDB設定(実質MySQL)を使用し、テストごとにトランザクションをロールバックすることで実DBを汚さない
- フロントエンド: `scheduleOccursOnDate`(`frontend/src/utils/recurrence.js`)などの純粋関数の単体テスト

```
docker compose exec backend pytest
docker compose exec frontend npm test
```

検証内容・結果は[docs/test.md](docs/test.md)を参照。

## Lint

フロントエンドはESLint(`eslint-plugin-vue`)を導入している。既存コードのスタイル(1タグに複数属性を書く等)を変えないため、フォーマット系ルールを含む`flat/recommended`ではなく、Vueの正確性チェックに絞った`flat/essential`を採用している。

```
docker compose exec frontend npm run lint
```

バックエンドは`ruff`を導入している。デフォルトの`E4`/`E7`/`E9`/`F`(pyflakes+明確なバグにつながるpycodestyleエラー)のみを対象にし、import順序等の書式ルールは追加していない(`backend/pyproject.toml`)。

```
docker compose exec backend ruff check .
```

`requirements.txt`を変更した場合は`docker compose up --build backend`でイメージを再ビルドする必要がある。

## 品質チェック

フロントエンド・バックエンド・DBそれぞれ独立したセッションで`/quality-check`コマンドによる品質チェックを実施した。進め方・結果は[docs/quality-check.md](docs/quality-check.md)を参照。

## セキュリティ

- ログイン・登録API(`/api/auth/login`・`/api/auth/register`)には`slowapi`によるIPベースのレート制限を設定している(login: 5回/分、register: 3回/分)。上限を超えると429を返す
- 登録パスワードは英字・数字を両方含む8文字以上を必須とする(`backend/app/schemas/auth.py`)
- JWT_SECRETについては上記「環境変数」を参照

## AWSデプロイ

Terraformで構築したEC2(t3.micro) + RDS MySQL(db.t3.micro)に本番相当のデプロイができる（無料枠の範囲。学習用個人アプリのため常時稼働はさせず、必要時のみ`terraform apply`/`terraform destroy`する運用を想定）。

- Terraformリソース: `infra/terraform/`
- 構成・デプロイ手順の詳細: [docs/08_deployment.md](docs/08_deployment.md)
- E2E動作確認の記録: [docs/deployment-verification.md](docs/deployment-verification.md)

開発中に発生した問題と対処法は[docs/07_troubleshooting.md](docs/07_troubleshooting.md)を参照。
