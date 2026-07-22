# AWSデプロイ（Terraform: EC2 + RDS）

## アーキテクチャ

学習用個人アプリのため、無料枠の範囲に収まる最小構成とする。ロードバランサー・オートスケーリング・HTTPS/独自ドメイン・CI/CDは対象外。

```
ブラウザ
   │  http://<EC2パブリックIP>/
   ▼
EC2 (t3.micro, Elastic IP)
   ├─ nginx (ホストにインストール、リバースプロキシ)
   │    ├─ /api/* → backendコンテナ (127.0.0.1:8000)
   │    └─ /*     → frontendコンテナ (127.0.0.1:5173)
   ├─ backendコンテナ (FastAPI, docker-compose.prod.yml)
   └─ frontendコンテナ (Vite build を `serve` で配信)
        │
        ▼
RDS MySQL 8.0 (db.t3.micro, publicly_accessible=false)
```

- EC2・RDSともデフォルトVPCを使用
- セキュリティグループ：SSH(22)・HTTP(80)は自分のIPのみ許可、RDS(3306)はEC2のセキュリティグループからのみ許可
- nginxはコンテナ化せず、EC2のuser_dataでホストに直接インストール（frontend/backendコンテナへのリバースプロキシと静的配信の両方を担う）

## Terraformリソース（`infra/terraform/`）

命名規則は`plannerwithexpense-*`で統一。

| ファイル | 内容 |
|---|---|
| `main.tf` | terraformブロック・awsプロバイダ |
| `ec2.tf` | デフォルトVPC・AL2023 AMI・SG・キーペア・EC2インスタンス・Elastic IP |
| `rds.tf` | DBサブネットグループ・SG・RDS(MySQL 8.0)インスタンス |
| `variables.tf` | リージョン・インスタンスタイプ・SSH公開鍵パス・自分のIP・DB名/ユーザー名/パスワード |
| `outputs.tf` | `public_ip`・`ssh_command`・`rds_endpoint` |
| `terraform.tfvars.example` | tfvarsのひな形（コミット対象） |

`terraform.tfvars`・`.terraform/`・`*.tfstate*`はgitignore対象（`infra/terraform/.gitignore`）。

## デプロイ手順

### 前提
- Terraform >= 1.9.0、AWS CLI（認証設定済み）
- SSH鍵ペアを生成：`ssh-keygen -t ed25519 -f ~/.ssh/plannerwithexpense`
- 自分のグローバルIPを確認：`curl -4 ifconfig.me`

### 1. インフラ構築
```
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# ssh_public_key_path・my_ip_cidr・db_username・db_passwordを編集
terraform init
terraform plan
terraform apply
terraform output   # public_ip・rds_endpointを控える
```

### 2. EC2へのアプリ配置
本リポジトリはGitHub上でパブリックなため、EC2上で直接`git clone`する。

```
ssh -i ~/.ssh/plannerwithexpense ec2-user@<public_ip>
git clone https://github.com/kmrtk/PlannerwithExpense.git app
sudo cp app/infra/nginx/plannerwithexpense.conf /etc/nginx/conf.d/plannerwithexpense.conf
```

nginxの初期設定（`/etc/nginx/nginx.conf`内に埋め込まれたデフォルトserverブロック）が同じ`listen 80; server_name _;`で重複するため、コメントアウトまたは削除してから`nginx -t`で構文確認し、`systemctl reload nginx`する。

### 3. 本番用`.env`の作成（EC2上、コミットしない）
`.env.prod.example`を参考に、EC2上の`~/app/.env`を作成する。

```
DATABASE_URL=mysql+pymysql://<db_username>:<db_password>@<rds_endpoint>/planner?charset=utf8mb4
JWT_SECRET=<openssl rand -hex 32 等で生成した強力な値>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ENVIRONMENT=production
CORS_ORIGINS=http://<public_ip>
```

`JWT_SECRET`を既定値のままにすると`ENVIRONMENT=production`の起動時バリデーションで落ちるため必須（`backend/app/config.py`参照）。

### 4. 起動
```
cd ~/app
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml logs backend   # Alembicマイグレーション成功を確認
```

## 実機で判明した注意点

- **AL2023のdnfリポジトリに`docker-compose-plugin`・`docker-buildx-plugin`が存在しない**。`ec2.tf`のuser_dataで、GitHub公式リリースのバイナリを`/usr/libexec/docker/cli-plugins/`に直接配置している
- **AMIの既定ルートボリュームは2GBしかなく、Dockerイメージのビルドで容量不足になる**。`ec2.tf`の`aws_instance`に`root_block_device { volume_size = 20 }`を明記して対応（無料枠の月間EBS上限30GB以内）
- nginxの組み込みデフォルトserverブロックとの重複に注意（上記手順参照）

## 再デプロイ手順（コード変更時）

`docker-compose.prod.yml`はソースのbind-mountを行わないため、コード変更時はEC2上で再取得＋再ビルドが必要。

```
cd ~/app
git pull
docker compose -f docker-compose.prod.yml up --build -d
```

## シークレット管理

- `terraform.tfvars`（DBパスワード等）・EC2上の`.env`（JWT_SECRET・DATABASE_URL等）はいずれもgitignore対象で、リポジトリにはコミットしない
- SSH秘密鍵はローカルのみで保管する

## 検証結果

E2E動作確認の結果は[docs/deployment-verification.md](deployment-verification.md)を参照。
