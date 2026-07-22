# 要件定義書　家族向け予定・家計簿アプリ（PlannerwithExpense）

# ⑥ 技術スタック・⑦ 開発期間

---

## ⑥ 技術スタック

前回プロジェクト（`task-manager-personal`: React + Java/Spring Boot + PostgreSQL）との差別化として、以下に変更する。

### 1. フロントエンド

| 項目 | 技術 |
| --- | --- |
| フレームワーク | Vue.js（SPA） |
| ビルドツール | Vite |

### 2. バックエンド

| 項目 | 技術 |
| --- | --- |
| 言語 | Python |
| フレームワーク | FastAPI |
| 認証 | 自前実装（JWT、メール＋パスワード） |
| API形式 | REST API |

### 3. データベース

| 項目 | 技術 |
| --- | --- |
| RDBMS | MySQL |

### 4. インフラ・開発ツール

| 項目 | 技術 |
| --- | --- |
| ローカル開発 | Docker Compose |
| デプロイ先 | AWS（EC2 t3.micro + RDS MySQL db.t3.micro、Terraformで構築。無料枠の範囲。主に課題提出用の公開先という位置づけで、日常利用はローカル運用を想定。構成・手順の詳細は[docs/08_deployment.md](08_deployment.md)を参照） |
| バージョン管理 | Git + GitHub |
| IaC | Terraform（`infra/terraform/`） |

---

## ⑦ 開発期間

未定（次回検討）
