# トラブルシューティング記録　家族向け予定・家計簿アプリ（PlannerwithExpense）

---

## 1. 概要

初期スキャフォールディング(PR #8)〜カレンダー月次表示強化(PR #14)の実装・動作確認中に発生した問題と対処法をまとめる。同種の問題が再発した際の参照用。

---

## 2. 問題一覧

### 2-1. Docker Desktopのエンジンが起動直後に500エラーを返す

- **症状**: `docker compose up`実行時に`request returned 500 Internal Server Error ... dockerDesktopLinuxEngine`のエラーで失敗する
- **原因**: Docker Desktop自体がアップデート・起動処理の途中だった
- **対処**: Docker Desktopの起動完了を待ってから再実行

### 2-2. MySQL初回起動時、backendコンテナがDB接続に失敗して起動失敗する

- **症状**: `docker compose up`直後、backendコンテナのログに`sqlalchemy.exc.OperationalError: ... Connection refused`が出て起動に失敗する。mysqlコンテナのhealthcheckは通過済みなのに発生する
- **原因**: MySQLは初回起動時、初期化用の一時サーバーを起動→シャットダウン→本サーバーとして再起動、という2段階の起動シーケンスを踏む。healthcheck(`mysqladmin ping`)は一時サーバーの段階でも成功してしまうことがあり、その直後にbackendが接続を試みると再起動中で拒否される
- **対処**: `backend/app/main.py`の起動処理(`on_startup`)でDB接続をリトライするループを追加(最大10回、3秒間隔)

### 2-3. bcryptとpasslibのバージョン非互換によりユーザー登録が500エラーになる

- **症状**: `POST /api/auth/register`が500エラー。ログに`ValueError: password cannot be longer than 72 bytes`という、実際のパスワード長とは無関係なエラーが出る
- **原因**: passlib 1.7.4がbcryptバックエンドの自己診断(`detect_wrap_bug`)を行う際に、最新のbcryptパッケージ(4.1系以降)の内部仕様変更と噛み合わず例外を出す既知の非互換問題
- **対処**: `backend/requirements.txt`に`bcrypt==4.0.1`を明示的に追加してバージョンを固定

### 2-4. MySQLに保存した日本語が文字化けする

- **症状**: APIのレスポンス(JSON)では正しく日本語が表示されるが、`mysql`クライアントで直接テーブルを確認すると`????`のように文字化けして見える
- **原因**: SQLAlchemyの接続文字列(`DATABASE_URL`)に文字コード指定がなく、pymysqlがデフォルトの`latin1`で接続していた(`character_set_client`等が`latin1`になっていた)。実データはUTF-8のバイト列として正しく保存されていたが、接続時の文字コード解釈がずれていたため表示上文字化けして見えた
- **対処**: `DATABASE_URL`に`?charset=utf8mb4`を追加(`mysql+pymysql://app:app@mysql:3306/planner?charset=utf8mb4`)

### 2-5. Windows上のDocker DesktopでVite HMRがファイル変更を検知しない

- **症状**: `frontend/src`配下のファイルを編集しても、ブラウザ側に変更が反映されない。frontendコンテナのログにもHMR更新のメッセージが出ない
- **原因**: Windows上のDocker Desktopでバインドマウントしたファイルの変更が、コンテナ内のファイルシステムイベント通知(inotify等)に伝わらないことがある
- **対処**: `frontend/vite.config.js`の`server.watch`に`usePolling: true`を追加し、ポーリング方式でファイル変更を検知するようにした

### 2-6. カレンダーの予定が実際の日付より1日ずれて表示される

- **症状**: 7/14に予定を作成すると、カレンダー上では7/15のセルに表示される
- **原因**: 日付をキーとして比較する処理で`Date.prototype.toISOString()`を使っていたが、これはローカルタイムゾーンの日時をUTCに変換してから文字列化する。日本時間(UTC+9)の場合、ローカル日付の0時をUTCに変換すると前日の15時になり、`.slice(0, 10)`で取り出す日付がずれる
- **対処**: `toISOString()`を使わず、`getFullYear()`/`getMonth()`/`getDate()`からローカルの年月日を直接組み立てる方式に変更

### 2-7. 月送りボタンを連続クリックすると表示月とデータがずれる

- **症状**: 「前月」ボタンを連続でクリックすると、最終的に表示されている月と、実際にカレンダーに表示される予定・支出のデータの月がずれることがある
- **原因**: 月を切り替えるたびに`schedules`/`expenses`/`budget`を非同期で再取得しているが、複数のリクエストが並行して飛んだ場合、後から発行したリクエストの応答が先に発行したリクエストの応答より先に返ってくるとは限らない（ネットワークタイミング次第で順序が入れ替わる）。そのため、古いリクエストの応答が新しいリクエストの応答を上書きしてしまうことがあった
- **対処**: リクエストごとに連番(シーケンス番号)を振り、応答が返ってきた時点で最新のリクエストでなければ結果を破棄するようにした

### 2-8. (アプリのバグではない)Windows版curlで日本語を含むJSONボディを渡すと文字化け・パースエラーになる

- **症状**: `curl -d '{"title":"買い出し", ...}'`のように日本語を含むJSONを直接コマンドライン引数で渡すと、バックエンドから`{"detail":"There was an error parsing the body"}`のようなエラーが返る
- **原因**: Windows環境のシェル/curlがコマンドライン引数の日本語をUTF-8以外の文字コードとして解釈し、送信データが壊れていた。アプリケーション側の問題ではなく、動作確認に使ったコマンドラインツール側の制約
- **対処**: 日本語を含むリクエストボディはコマンドライン引数ではなく、UTF-8で保存したファイルから`--data-binary @file`で読み込むようにして回避
