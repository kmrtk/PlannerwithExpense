# Alembic導入（概要）

作成日: 2026-07-15

## 何をするか
バックエンド（FastAPI + SQLAlchemy + MySQL）にAlembicを導入し、DBスキーマ変更をマイグレーションで管理できるようにする。

## 背景
現状、`backend/app/main.py`起動時に`Base.metadata.create_all()`でテーブルを自動作成しており、マイグレーション管理の仕組みがない。そのためスキーマ変更のたびに`docker compose down -v`でDBを丸ごと削除・再作成する運用が続いている（既に6回前後発生）。

## 何を導入するか
- Alembic本体（`backend/requirements.txt`に追加）
- `backend/alembic/`ディレクトリ一式（`alembic.ini`、`env.py`、マイグレーションファイル）

## 何を作るか
- 現在のモデル定義（`backend/app/models/`：user, schedule, expense, budget）を反映した初期マイグレーション
- 今後のスキーマ変更をマイグレーションで運用する体制（`main.py`の`create_all()`の扱いを含めて判断）
- READMEまたはdocsへの運用手順の追記（`docker compose down -v`前提の記載があれば更新）

## 進め方
このドキュメントは概要のみ。実装セッションでは、このファイルを参照した上でプランモードで詳細な実装計画を作成し、承認を得てから実装すること。GitHubフロー（Issue作成→ブランチ→実装→PR、マージなし）は通常通り従うこと。

## 並行実装・検証方針（2026-07-16追記）
- この項目は、入力バリデーション強化・テスト導入と合わせて**3項目をgit worktreeで並行実装**する（それぞれ独立したブランチ・作業ディレクトリ）
- **docker composeでの実地動作確認（マイグレーション適用含む）は、3項目とも実装・PR作成が完了した後、1つずつ順番に行う**（同時に複数worktreeでdocker composeを起動するとポート・DBが衝突するため）
- そのため、実装フェーズでは`alembic revision --autogenerate`が実行できない可能性がある。その場合は現在のモデル定義から手動でマイグレーションファイルを作成し、PRに「autogenerateではなく手動作成、docker検証は未実施」と明記する。検証フェーズで実際にdockerを起動し、マイグレーションが正しく適用されるか確認してから正式に完了とする
- 作業用worktree：`c:\Users\kimur\Takacursor\PlannerwithExpense-alembic`（`.claude-notes/`はgitignore対象のため、worktree作成後に本体（`c:\Users\kimur\Takacursor\PlannerwithExpense\.claude-notes\`）から手動でコピーする必要がある）
- **後片付け**：この項目のPRがマージされたら、`git worktree remove c:\Users\kimur\Takacursor\PlannerwithExpense-alembic`でworktreeを削除し、不要になったブランチも`git branch -d`で削除する
- **マージ時に競合した場合の対応**：この項目は`backend/requirements.txt`（Alembic追加）と`README.md`（運用手順追記）を変更する。テスト導入の項目も同じ2ファイルに追記するため、どちらかを先にマージした後、もう一方のPRで軽い競合が発生する見込み。発生したら以下の手順で対応する：
  1. `git fetch origin && git merge origin/master`（または`git rebase origin/master`）を実行し、競合ファイルを確認する
  2. 競合ファイル（`backend/requirements.txt`／`README.md`）を開き、`<<<<<<<`〜`=======`〜`>>>>>>>`のマーカー部分を探す
  3. これは実装ロジックの衝突ではなく**両方の追加行が別々に存在するだけ**なので、マーカーを削除して**両方の追加内容を残す**（例：`requirements.txt`なら`alembic==...`の行と、テスト項目が追加した`pytest==...`の行を両方残す）
  4. `git add`で解決済みとしてステージし、`git commit`（rebaseの場合は`git rebase --continue`）で完了させる
  5. プッシュしてPRの競合表示が消えたことを確認する
