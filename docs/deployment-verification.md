# AWSデプロイ(Terraform: EC2+RDS)動作検証記録

## 検証日
2026-07-22

## 対象
Issue #83 / PR「本番Docker化・AWSデプロイ・ドキュメント更新」

## 検証環境
`terraform apply`で新規構築したEC2(t3.micro) + RDS MySQL(db.t3.micro)。`docker-compose.prod.yml`で本番用イメージをビルドして起動。EIPは構築のたびに変わるため、以下では`<public_ip>`と表記する（実際のIPアドレスは記録しない）。

## 検証内容と結果

| 項目 | 結果 |
|------|------|
| `terraform apply`でEC2・RDS・SG等7リソースが作成されるか | OK |
| SSHで自分のIPからEC2に接続できるか | OK |
| `http://<public_ip>/`でフロントエンドが表示されるか | OK（200） |
| `http://<public_ip>/api/health`が正常応答するか | OK（`{"status":"ok"}`） |
| ユーザー登録がCORSエラーなく成功するか | OK（`access-control-allow-origin`に`http://<public_ip>`が返る） |
| ログイン・JWT発行・認証付きAPI呼び出し | OK |
| 予定の登録がRDSに永続化されるか（一覧取得で確認） | OK |
| `docker compose restart backend`後もRDSのデータが残っているか | OK |
| RDSがパブリックアクセス不可か（ローカルから直接接続を試行） | OK（タイムアウトし接続不可を確認） |
| セキュリティグループがSSH/HTTPとも自分のIPのみに制限されているか | OK（`describe-security-groups`で`/32`指定を確認） |
| バックエンド起動時にAlembicマイグレーションがRDSに対して自動実行されるか | OK（ログで`0001`→`0002`適用を確認） |

## 発生した問題と対処

| 問題 | 原因 | 対処 |
|------|------|------|
| `docker compose`コマンドが見つからない | AL2023の`dnf`リポジトリに`docker-compose-plugin`が存在しない | GitHub公式リリースのバイナリを`/usr/libexec/docker/cli-plugins/docker-compose`に直接配置するようuser_dataを修正 |
| `compose build requires buildx 0.17.0 or later` | 同様に`docker-buildx-plugin`が存在しない | `docker-buildx`バイナリも同様に配置 |
| イメージビルド中に`no space left on device` | AMIの既定ルートボリュームが2GBしかない | `aws_instance`に`root_block_device { volume_size = 20 }`を追加（無料枠のEBS月間上限30GB以内） |
| nginx経由のPOSTで`There was an error parsing the body` | 検証環境(Windows)のcurlが日本語文字列を含むJSONペイロードのエンコーディングを崩していたため（既知の問題、[docs/07_troubleshooting.md](07_troubleshooting.md)参照） | ASCII文字列のペイロードで再検証し、nginx・アプリ側の問題でないことを確認。デプロイ自体に不具合はない |
| nginxのデフォルトserverブロックと`conf.d`の設定が重複 | AL2023のnginxパッケージは`/etc/nginx/nginx.conf`内にデフォルトserverブロックを直接埋め込んでいる | 当該ブロックをコメントアウトしてから`plannerwithexpense.conf`を配置 |

## 補足
- 上記の対処内容は`infra/terraform/ec2.tf`のuser_data・`docs/08_deployment.md`に反映済み
- 検証後、Terraformで構築したリソースは実運用に必要になるまで`terraform destroy`で削除する想定（学習用アプリのため常時稼働はさせない）
