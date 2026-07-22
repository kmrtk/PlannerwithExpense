# Terraform 品質チェック結果

2026-07-22実施。対象: `infra/terraform/`（`main.tf` / `ec2.tf` / `rds.tf` / `variables.tf` / `outputs.tf` / `terraform.tfvars` / `terraform.tfvars.example` / `.gitignore`）。`/quality-check` の Step 4.5（Terraform / IaC チェック）に基づく。

## チェック結果

| チェック項目 | 結果 | 備考 |
|---|---|---|
| fmt（`terraform fmt -check -recursive`） | ✅ | 差分なし |
| validate（`terraform validate`） | ✅ | `Success! The configuration is valid.` |
| 認証情報の変数化・sensitive設定 | ✅ | `db_password` は `variables.tf` で `variable` 化・`sensitive = true` 設定済み。`.tf`ファイル内への直書きなし |
| .gitignore除外（tfvars/tfstate） | ✅ | `infra/terraform/.gitignore` で `terraform.tfvars` / `*.tfstate*` / `.terraform/` を除外。`git ls-files infra/terraform/` で実値入りの `terraform.tfvars` と `terraform.tfstate` が追跡対象に含まれていないことを確認済み（追跡されているのは `terraform.tfvars.example` のみ） |
| セキュリティグループ（0.0.0.0/0の不必要な使用） | ✅ | EC2用SG（`plannerwithexpense-sg`）のingressは`var.my_ip_cidr`（自分のIP）限定。RDS用SG（`plannerwithexpense-rds-sg`）のingressはEC2のSG参照のみで自分のIPからも直接到達不可。egressの`0.0.0.0/0`は一般的な設定のため対象外 |
| terraform plan（意図しない削除・再作成） | ⚠️ | `0 to add, 1 to change, 0 to destroy` で削除・再作成は含まれないが、`aws_instance.app`の`user_data`が実際に適用済みの値と差分あり（下記Medium参照） |
| 共通（シークレット漏洩・TODO残存） | ✅ | `.tf`ファイル内にシークレットの直書き・TODOコメントなし |

## 問題点一覧（優先度順）

1. [Medium] **`aws_instance.app`の`user_data`がデプロイ済みインスタンスと乖離** — `terraform plan`で`user_data`のハッシュ値に差分が検出された（`ec2.tf`の内容を編集した後、EC2インスタンスに対して`apply`していない状態）。EC2の`user_data`は起動時にのみ実行されるため、`apply`しても稼働中インスタンスへは反映されない。放置してもコード上の記述と実インスタンスの初期化スクリプトの乖離が続くため、次にインスタンスを作り直す機会（再作成やリストア等）に反映されることを認識した上で運用する、または意図的に`apply`して`.tfstate`上の記録を最新化するか判断が必要

検出なし: Critical / High / Low

## 参照

- 品質チェックコマンド本体: `https://github.com/kmrtk/claude-config/blob/master/commands/quality-check.md`
