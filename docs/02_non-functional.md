# 要件定義書　家族向け予定・家計簿アプリ（PlannerwithExpense）

# ③ 非機能要件

---

## ③ 非機能要件

| カテゴリ | 内容 |
|---------|------|
| 対応ブラウザ | 未定（次回検討） |
| 対応デバイス | 未定（次回検討。PC・スマホどちらでの利用を想定するか要相談） |
| データ保持 | MySQLに永続化 |
| セキュリティ | JWT_SECRETは環境変数`ENVIRONMENT=production`かつ既定値のままだと起動を拒否する（既知の値でのトークン偽造を防止）。ログイン・登録APIにはIPベースのレート制限（login: 5回/分、register: 3回/分）を設定し、総当たり攻撃・登録スパムに備える。登録パスワードは英字・数字を両方含む8文字以上を必須とする。本番デプロイ時はJWT_SECRETを強力な値に変更し、CORS_ORIGINSをデプロイ先オリジンに設定する（詳細は[docs/08_deployment.md](08_deployment.md)参照）。RDSはpublicly_accessible=falseとし、EC2のセキュリティグループからのみ接続を許可する |
| デザイン | フォントはGoogle Fonts「M PLUS Rounded 1c」を採用し、丸ゴシック系のやわらかい印象で統一する |
