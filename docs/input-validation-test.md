# 入力バリデーション強化 動作検証記録

## 検証日
2026-07-16

## 対象
Issue #31 / PR #33（入力バリデーション強化）

## 検証環境
`docker compose up --build`（worktree: `PlannerwithExpense-validation`、フレッシュな新規ボリューム）

## 検証方法
ユーザー登録→取得したアクセストークンを使い、`curl`でバックエンドAPI（`/api/expenses`、`/api/schedules`、`/api/budgets`）に対して正常系・異常系のリクエストを送信し、期待どおりのステータスコード・エラーメッセージが返るかを確認した。

## 検証内容と結果

### 支出（`/api/expenses`）

| 項目 | 期待結果 | 実際の結果 |
|------|---------|-----------|
| 正常な支出登録（金額1000円、カテゴリ「食費」） | 201 | OK（201） |
| マイナス金額（-500） | 422で拒否 | OK（`amount: Input should be greater than 0`） |
| ゼロ金額（0） | 422で拒否 | OK（`amount: Input should be greater than 0`） |
| 上限超過の金額（999,999,999円） | 422で拒否 | OK（`amount: Input should be less than or equal to 100000000`） |
| 空白のみのカテゴリ | 422で拒否 | OK（`category: Value error, カテゴリを入力してください`） |
| 256文字のカテゴリ（上限255文字） | 422で拒否 | OK（`category: String should have at most 255 characters`） |
| 1001文字のメモ（上限1000文字） | 422で拒否 | OK（`memo: String should have at most 1000 characters`） |

### 予定（`/api/schedules`）

| 項目 | 期待結果 | 実際の結果 |
|------|---------|-----------|
| 正常な予定登録 | 201 | OK（201） |
| 終了日時が開始日時より前 | 422で拒否 | OK（`Value error, 終了日時は開始日時以降にしてください`） |
| 空白のみのタイトル | 422で拒否 | OK（`title: Value error, タイトルを入力してください`） |
| 繰り返し終了日が開始日より前 | 422で拒否 | OK（`Value error, 繰り返し終了日は開始日以降にしてください`） |

### 予算（`/api/budgets`）

| 項目 | 期待結果 | 実際の結果 |
|------|---------|-----------|
| 正常な予算登録（PUT） | 200 | OK（200） |
| 不正な月（13） | 422で拒否 | OK（`month: Input should be less than or equal to 12`） |
| マイナスの貯蓄目標 | 422で拒否 | OK（`savings_target: Input should be greater than or equal to 0`） |

### エラーレスポンス形式の統一

すべての異常系リクエストで、レスポンスの`detail`が単一の文字列で返ることを確認した（FastAPIの`RequestValidationError`用に追加した例外ハンドラが機能している）。これにより、既存の`HTTPException`（文字列の`detail`）とフロントエンド側で同じロジックで表示できる。

## 補足
- フロントエンド（Vueモーダル）でのエラーメッセージ表示は、上記のAPIレスポンス形式（`detail`が文字列）を前提にコーディングされていることをコードレビューで確認した。本検証環境にはブラウザ自動操作ツールがなく、実際のブラウザ画面上でのエラー表示の目視確認は実施していない。
- `npm run build`がエラーなく成功することは別途確認済み。
- 検証時、メインリポジトリ側の`docker compose`スタックは一時停止し、検証後に復旧している（ポート競合回避のため）。
