# 品質チェック実施記録

PlannerwithExpenseで実施した品質チェックの進め方・結果をまとめたもの。

## 進め方

1. ユーザーが新規チャットを3つ開く（フロントエンド用・バックエンド用・DB用）
2. それぞれのチャットで `/quality-check` を実行し、担当領域の品質チェックを行う（チェックのみ実行し、削除等の後片付けは行わない）
3. 各チャットの結果をマネージャー役セッションに持ち帰り、優先度確認・Issue化・修正を進める
4. マージ後、修正内容自体をフレッシュセッションでレビューする（下記「2回目」）

### なぜ新規チャットで実行するのか

実装済みのセッションでそのまま品質チェックをすると、セルフレビューバイアスがかかりやすい。
- 実装した本人（同じセッション）は無意識に自分のコードに甘くなる
- 「知っているから大丈夫」で細部の確認を省略しがちになる

第三者によるコードレビューが重視されるのと同じ理由で、品質チェック・レビューは実装内容を知らない新規セッションで行う。

### 3セクション並行作業時の注意点

3つとも「読み取り・診断のみ」（lint・ビルド確認・コードを読んでの確認・DBコンテナの状態確認）でファイルを書き換えないため、git上の競合は基本的に発生しない。ただし以下3点に注意する。

1. **足りないツールを勝手にインストールしない**（フロントエンドの`eslint`、バックエンドの`ruff`/`flake8`/`mypy`等。インストールの判断はマネージャー役セッションでまとめて行う）
2. **Dockerコンテナを止める操作はしない**（状態確認はOKだが、`restart`/`down`のような操作は他セッションに影響するため避ける）
3. **`npm run build`はやや重い処理**（3セッション同時実行でPCがもたつく可能性はあるが致命的ではない）

## 1回目：3セクション並行実施（2026-07-21）

フロント・バックエンド・DBの3セッションで実施。

| 領域 | Lint | 型チェック | ビルド/テスト | コードパターン | 共通（シークレット・デバッグコード等） |
|---|---|---|---|---|---|
| フロントエンド | ⚠️ ESLint未導入 | - (TS未使用) | ✅ build成功 / ✅ vitest 8件パス | ⚠️ 下記参照 | ✅ 問題なし |
| バックエンド | ⚠️ ruff/flake8/mypy未導入 | ⚠️ 同上 | ✅ pytest 11件パス | ⚠️ 下記参照 | ✅ 問題なし |
| DB/インフラ | - | - | ✅ マイグレーション整合性OK | ✅ 問題なし | ✅ 問題なし |

3領域とも重大（Critical/High）な問題は検出されなかった。

### Medium（すべて対応済み）

1. ✅ **（フロント）初期データ取得のエラーハンドリングがない** — `CalendarView.vue`の`fetchMonthData`、`ExpensesView.vue`の`fetchExpenses`、`ScheduleListView.vue`の`fetchSchedules`、`YearlyBudgetView.vue`の`fetchYearData`/`fetchAllTimeSummary`にtry/catchがなく、API通信失敗時にUnhandled Promise Rejectionとなり、ユーザーに何もエラー表示されない → Issue #64 / PR #65で対応、マージ済み
2. ✅ **（バックエンド）会員登録パスワードに長さ・強度の制約がない** — `backend/app/schemas/auth.py`の`RegisterRequest.password`が単なる`str`で、空文字列や1文字でも登録できてしまう → Issue #66 / PR #67で対応（英数字8文字以上のバリデーションを追加）、マージ済み
3. ✅ **（フロント）ESLint未導入** — 静的解析の仕組みがなく、レビュー頼みになっている → Issue #68 / PR #69で対応（`eslint`+`eslint-plugin-vue`の`flat/essential`ルールセットを導入）、マージ済み

## 2回目：マージ後のPRレビュー（2026-07-21）

PR #65・#67・#69のマージ後、フレッシュセッションで`/quality-check`を使い、実装内容自体をレビュー。

| カテゴリ | チェック項目 | 結果 | 備考 |
|---|---|---|---|
| バックエンド | pytest（test_auth.py） | ✅ | 9 passed（PR #67追加の3件含む） |
| バックエンド | コードパターン（バリデーション） | ✅ | `Field(min_length=8)` + `field_validator`の組み合わせは妥当 |
| フロントエンド | Lint（eslint） | ✅ | エラーなし |
| フロントエンド | コードパターン（エラーハンドリング） | ⚠️ | 下記Medium参照 |
| 共通 | シークレット漏洩・デバッグコード残存 | ✅ | 該当なし |

### Medium（対応済み）

1. ✅ **`YearlyBudgetView.vue`の`loadError`クリア漏れ（PR #65）** — `fetchAllTimeSummary()`は失敗時に`loadError`をセットするが、成功時に`loadError.value = ""`をクリアしていなかった（同ファイルの`fetchYearData()`や他3ビューは成功時にクリアしている中でこの関数だけ抜けていた）。一度エラーが出た後に成功しても古いエラーメッセージが残り続ける不具合があった → Issue #76 / PR #77で対応、マージ済み

PR #67・#69は実装・テストともに意図通りで問題なし。

## 3回目：Terraformチェック（2026-07-22）

AWSデプロイ環境構築（PR #84〜#87）のマージ後、フレッシュセッションで`/quality-check`のStep 4.5（Terraform/IaCチェック）を実施。対象: `infra/terraform/`（`main.tf` / `ec2.tf` / `rds.tf` / `variables.tf` / `outputs.tf` / `terraform.tfvars` / `terraform.tfvars.example` / `.gitignore`）。

| チェック項目 | 結果 | 備考 |
|---|---|---|
| fmt（`terraform fmt -check -recursive`） | ✅ | 差分なし |
| validate（`terraform validate`） | ✅ | `Success! The configuration is valid.` |
| 認証情報の変数化・sensitive設定 | ✅ | `db_password`は`variables.tf`で`variable`化・`sensitive = true`設定済み。`.tf`ファイル内への直書きなし |
| .gitignore除外（tfvars/tfstate） | ✅ | `infra/terraform/.gitignore`で`terraform.tfvars` / `*.tfstate*` / `.terraform/`を除外。`git ls-files infra/terraform/`で実値入りの`terraform.tfvars`と`terraform.tfstate`が追跡対象に含まれていないことを確認済み（追跡されているのは`terraform.tfvars.example`のみ） |
| セキュリティグループ（0.0.0.0/0の不必要な使用） | ✅ | EC2用SG（`plannerwithexpense-sg`）のingressは`var.my_ip_cidr`（自分のIP）限定。RDS用SG（`plannerwithexpense-rds-sg`）のingressはEC2のSG参照のみで自分のIPからも直接到達不可。egressの`0.0.0.0/0`は一般的な設定のため対象外 |
| terraform plan（意図しない削除・再作成） | ⚠️ | `0 to add, 1 to change, 0 to destroy`で削除・再作成は含まれないが、`aws_instance.app`の`user_data`が実際に適用済みの値と差分あり（下記Medium参照） |
| 共通（シークレット漏洩・TODO残存） | ✅ | `.tf`ファイル内にシークレットの直書き・TODOコメントなし |

検出なし: Critical / High / Low

### Medium（対応済み）

1. ✅ **`aws_instance.app`の`user_data`がデプロイ済みインスタンスと乖離** — `terraform plan`で`user_data`のハッシュ値に差分が検出された（実機検証で判明した問題への対応として`ec2.tf`を編集した後、EC2インスタンスに対して`apply`していない状態だった）。EC2の`user_data`は起動時にのみ実行されるため、`apply`しても稼働中インスタンスへは反映されないが、コード上の記述と`.tfstate`上の記録が乖離したまま残る問題があった → `terraform apply`を再実行してstateを最新化し、`terraform plan`で差分ゼロを確認して解消

## 4回目：Low優先度項目の対応（2026-07-22）

ユーザーと相談の上、Low項目のうち5件に対応した。

1. ✅ **（フロント）401エラー時に自動でログイン画面へ遷移しない** — `frontend/src/api/client.js`のレスポンスインターセプターに、401時の`auth.logout()`に加えて`router.push({ name: "login" })`を追加 → Issue #92 / PR #93で対応、マージ済み
2. ✅ **（フロント）アイコンのみのボタンに`aria-label`がない** — `AppSidebar.vue`のサイドバー開閉ボタン・年月ナビゲーションのchevronボタン（計3箇所）に状態に応じた`aria-label`を追加 → Issue #92 / PR #93で対応、マージ済み
3. ✅ **（フロント）`ExpensesView.vue`の削除処理にエラーハンドリングがない** — `handleDelete`/`handleDeleteFromModal`をtry/catchで囲み、既存の`loadError`で失敗時にエラーメッセージを表示するようにした → Issue #92 / PR #93で対応、マージ済み
4. ✅ **（バックエンド）`ruff`未導入** — `ruff==0.9.4`を導入。フロントのESLint導入時と同じ方針で、デフォルトの`E4`/`E7`/`E9`/`F`（pyflakes+明確なバグにつながるpycodestyleエラー）のみを対象にし、書式ルールは追加していない（`backend/pyproject.toml`） → Issue #94 / PR #95で対応、マージ済み
5. ✅ **（DB）`budgets.py`の年間・累計集計がPython側集計** — `get_yearly_summary`/`get_all_time_summary`を、SQLAlchemyの`func.sum()`/`case()`/`group_by`によるDB側集計に変更。回帰テスト（`test_budgets.py`）を追加し、動作が変わっていないことを確認 → Issue #96 / PR #97で対応、マージ済み

なお、（バックエンド）CORSオリジンのハードコードについては、AWSデプロイ対応（PR #84〜#87）の過程で`CORS_ORIGINS`環境変数から読み込む実装（`backend/app/config.py`の`cors_origins`/`cors_origins_list`）に既に変更済みであることを確認した。追加対応は不要。

## 5回目：マージ済みPRの軽量レビュー（2026-07-22）

「4回目」で対応したPR #93（フロント）・PR #95/#97（バックエンド）について、実装セッションとは別の新規セッションで、対象ファイルに絞った軽量な`/quality-check`レビューを実施（`docs/quality-check3.md`として一旦ドキュメント化、内容はこのファイルに統合し原本は削除）。

対象：`frontend/src/api/client.js`・`frontend/src/components/AppSidebar.vue`・`frontend/src/views/ExpensesView.vue`・`backend/requirements.txt`・`backend/pyproject.toml`・`backend/app/routers/budgets.py`・`backend/tests/test_budgets.py`

| カテゴリ | チェック項目 | 結果 | 備考 |
|---|---|---|---|
| フロントエンド | Lint（`npm run lint`） | ✅ | エラーなし |
| フロントエンド | ビルド（`npm run build`） | ✅ | 105 modules変換、正常終了 |
| フロントエンド | テスト（`npm run test`） | ✅ | vitest 8件パス |
| フロントエンド | コードパターン | ✅ | 401リダイレクト・aria-label・削除エラーハンドリングとも実装通りで問題なし |
| バックエンド | Lint（`ruff check app tests`） | ✅ | All checks passed! |
| バックエンド | テスト（`pytest`） | ✅ | 17 passed（回帰なし。うち`test_budgets.py`3件） |
| バックエンド | コードパターン | ✅ | ruff設定（書式ルール未追加の方針維持）、DB集計変更のNone防御、回帰テストの網羅性とも妥当 |
| 共通 | シークレット漏洩・デバッグコード・TODO残存 | ✅ | 該当なし |

検出なし: Critical / High / Medium / Low（今回確認した7ファイルの範囲では新規指摘事項なし）

## 未対応項目一覧（Low・着手時期未定）

1. （バックエンド）`mypy`/`flake8`未導入（`ruff`は導入済み） — **理由**：まず1ツール（ruff）から導入する方針で合意し、追加のツール導入は今回のスコープ外としたため
2. （バックエンド）`@app.on_event("startup")`が非推奨API（`lifespan`への移行が将来的に必要） — **理由**：非推奨警告が出るのみで現状の動作に支障はなく、FastAPIの将来バージョンで削除されるまでは対応不要と判断したため
3. （バックエンド）パスワードバリデーションのテストカバレッジに1点抜け（8文字未満かつ複雑さ要件も満たさないケースのテストはない） — **理由**：`min_length=8`制約で確実に弾かれるため実害がなく、テスト追加の優先度が低いと判断したため
4. （DB）`Schedule`モデルに`expense`への逆参照`relationship`がない — **理由**：予定に紐づく支出／支出に紐づく予定は同じ関係を逆方向から見ているだけで、現状のAPI実装ではその逆引きを使う画面・機能がなく、追加しても使い道がないため

着手する場合はマネージャー役セッションでユーザーと相談の上、Issue化する。

## 対応不要と判断した項目（参考として記載）

- （フロント）Piniaストアのstate直接代入 — Options Store actionsの正しい書き方
- （バックエンド）`datetime.utcnow()`非推奨警告 — 依存ライブラリ（python-jose）内部の警告で自プロジェクトのコード対象外

## 参照

- 品質チェックコマンド本体: `~/.claude/commands/quality-check.md`（バックアップ: `https://github.com/kmrtk/claude-config` の `commands/quality-check.md`、ローカルクローン: `C:/Users/kimur/Takacursor/claude-config`）
