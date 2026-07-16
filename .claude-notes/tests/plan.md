# テスト導入（概要）

作成日: 2026-07-15

## 何をするか
バックエンド・フロントエンドの両方に自動テストの仕組みを導入する。

## 背景
現状、backend・frontendともに自動テストが一切なく、動作確認は毎回使い捨てのPlaywrightスクリプト（セッション終了で消える）に頼っている。

## 何を導入するか
- バックエンド：pytest、httpx（FastAPIのテストクライアント用）
- フロントエンド：vitest

## 何を作るか
- バックエンド：テスト用のディレクトリ・fixture一式。最低限、ユーザー登録・ログインのテストと、所有者スコープ（他ユーザーのデータが見えないこと）のテストを用意する
- フロントエンド：テスト実行環境一式。最低限、`scheduleOccursOnDate`（`frontend/src/utils/recurrence.js`）のような純粋関数の単体テストを用意する
- READMEへのテスト実行方法の追記

## 進め方
このドキュメントは概要のみ。実装セッションでは、このファイルを参照した上でプランモードで詳細な実装計画を作成し、承認を得てから実装すること。大規模なテストスイートを一度に作る必要はなく、今後拡充していく土台になれば十分。GitHubフロー（Issue作成→ブランチ→実装→PR、マージなし）は通常通り従うこと。

## 並行実装・検証方針（2026-07-16追記）
- この項目は、Alembic導入・入力バリデーション強化と合わせて**3項目をgit worktreeで並行実装**する（それぞれ独立したブランチ・作業ディレクトリ）
- **docker composeでの実地動作確認（pytest実行含む）は、3項目とも実装・PR作成が完了した後、1つずつ順番に行う**（同時に複数worktreeでdocker composeを起動するとポート・DBが衝突するため）
- **pytestのテスト用DB接続は、SQLite等の代替ではなく、アプリの通常のDB設定（`backend/app/config.py`のDATABASE_URL、実質MySQL）を使う前提でテストコードを書く**。実装フェーズではdockerが使えずpytestを実際に実行できなくても構わない。検証フェーズでdockerを起動してから初めて`pytest`を実行し、本番と同じMySQL環境でテストが通ることを確認する（本番相当の環境で検証する、という当初の目的を損なわないための方針）
- 作業用worktree：`c:\Users\kimur\Takacursor\PlannerwithExpense-tests`（`.claude-notes/`はgitignore対象のため、worktree作成後に本体（`c:\Users\kimur\Takacursor\PlannerwithExpense\.claude-notes\`）から手動でコピーする必要がある）
- **後片付け**：この項目のPRがマージされたら、`git worktree remove c:\Users\kimur\Takacursor\PlannerwithExpense-tests`でworktreeを削除し、不要になったブランチも`git branch -d`で削除する
- **マージ時に競合した場合の対応**：この項目は`backend/requirements.txt`（pytest・httpx追加）と`README.md`（テスト実行方法追記）を変更する。Alembic導入の項目も同じ2ファイルに追記するため、どちらかを先にマージした後、もう一方のPRで軽い競合が発生する見込み。発生したら以下の手順で対応する：
  1. `git fetch origin && git merge origin/master`（または`git rebase origin/master`）を実行し、競合ファイルを確認する
  2. 競合ファイル（`backend/requirements.txt`／`README.md`）を開き、`<<<<<<<`〜`=======`〜`>>>>>>>`のマーカー部分を探す
  3. これは実装ロジックの衝突ではなく**両方の追加行が別々に存在するだけ**なので、マーカーを削除して**両方の追加内容を残す**（例：`requirements.txt`なら`pytest==...`/`httpx==...`の行と、Alembic項目が追加した`alembic==...`の行を両方残す）
  4. `git add`で解決済みとしてステージし、`git commit`（rebaseの場合は`git rebase --continue`）で完了させる
  5. プッシュしてPRの競合表示が消えたことを確認する
