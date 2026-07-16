# テスト（pytest/vitest）導入 動作検証記録

## 検証日
2026-07-16

## 対象
Issue #32 / PR #35（backend/frontendへのテスト導入）、Issue #44（本検証記録）

## 検証環境
`docker compose up --build`（worktree: `PlannerwithExpense-tests`、フレッシュな新規ボリューム）

## 検証内容と結果

| 項目 | 結果 |
|------|------|
| `docker compose up --build`でbackend/mysql/frontendが起動するか | OK |
| APIヘルスチェック(`/api/health`) | OK（200） |
| フロントエンド(`http://localhost:5173`)の応答 | OK（200） |
| `docker compose exec backend pytest -v`（本番同様のMySQL環境） | OK（6 passed） |
| `docker compose exec frontend npm test`（vitest） | OK（8 passed） |
| pytestのテストデータがロールバックされ、実DBに残らないか（`SELECT COUNT(*) FROM user`で確認） | OK（0件） |
| ユーザー登録→ログイン→支出登録→一覧取得のE2E動作（`curl`で確認） | OK（新規DBから一連の操作が正常に完了） |

### pytest内訳（`backend/tests/`）

| テストファイル | テスト内容 | 結果 |
|----------------|-----------|------|
| `test_auth.py::test_register_returns_access_token` | ユーザー登録が201・アクセストークンを返す | PASSED |
| `test_auth.py::test_login_with_registered_user_succeeds` | 登録したユーザーでログインできる | PASSED |
| `test_auth.py::test_register_with_duplicate_email_fails` | 重複メールでの登録が失敗する | PASSED |
| `test_auth.py::test_login_with_wrong_password_fails` | 誤ったパスワードでのログインが失敗する | PASSED |
| `test_ownership.py::test_user_cannot_access_another_users_expense` | 他ユーザーの支出をGET一覧に含まない・PUT/DELETEが404になる | PASSED |
| `test_ownership.py::test_user_cannot_access_another_users_schedule` | 他ユーザーの予定へのPUT/DELETEが404になる | PASSED |

### vitest内訳（`frontend/src/utils/recurrence.test.js`）

`scheduleOccursOnDate`について、繰り返しなし／起点日より前／`recurrence_end`境界／毎週／毎月／月またぎで該当日が存在しないケース／未知の`recurrence_type`の8パターンをすべて確認し、全てパス。

## 検証時に発見・修正した不具合
`docker compose exec backend pytest`を実行すると`collected 0 items`となりテストが一つも実行されなかった。原因は`backend/Dockerfile`が`app`ディレクトリのみをイメージにコピーしており、`tests/`・`pytest.ini`が含まれていなかったため。`Dockerfile`に`tests`・`pytest.ini`のコピーを追加し、`docker-compose.yml`にも`app`と同様に`tests`ディレクトリのbind mountを追加することで解消した（コード変更のたびに再ビルド不要にするため）。この修正はPR #35に追加コミットとして反映済み。

## 補足
- pytestは、テストごとにSAVEPOINTでロールバックする方式（`backend/tests/conftest.py`）で実DB（MySQL）に接続しているが、上記の通り実際にテストデータが残らないことを確認した。
- MySQLの`AUTO_INCREMENT`はトランザクションのロールバック対象外のため、テスト実行後にID採番が飛ぶことがあるが、これは想定内の挙動でありデータ漏れではない。
- 検証時、メインリポジトリ側の`docker compose`スタックは一時停止し、検証後に復旧している（ポート競合回避のため）。
