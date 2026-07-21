# 品質チェック結果（PR #67 / #65 / #69）

実施日: 2026-07-21
対象: マージ済みPR3件（Quality Checkスキルを使用）

- PR #67（`65837ee`）: `backend/app/schemas/auth.py` の `RegisterRequest` パスワードバリデーション追加
- PR #65（`f3089ce`）: `CalendarView.vue` / `ExpensesView.vue` / `ScheduleListView.vue` / `YearlyBudgetView.vue` のエラーハンドリング追加
- PR #69（`975b9d9`）: `frontend/eslint.config.js` ・ `package.json` へのESLint導入

## 検出した技術スタック

- フロントエンド: Vue 3 + Vite（ESLint導入済み）
- バックエンド: FastAPI + Pydantic v2（pytest）
- DB: MySQL（Docker）

## チェック結果

| カテゴリ | チェック項目 | 結果 | 備考 |
|---|---|---|---|
| バックエンド | pytest（test_auth.py） | ✅ | 9 passed（PR #67追加の3件含む） |
| バックエンド | コードパターン（バリデーション） | ✅ | `Field(min_length=8)` + `field_validator`の組み合わせは妥当 |
| フロントエンド | Lint（eslint） | ✅ | エラーなし |
| フロントエンド | コードパターン（エラーハンドリング） | ⚠️ | 下記Medium参照 |
| 共通 | シークレット漏洩 | ✅ | 該当なし |
| 共通 | デバッグコード残存 | ✅ | 該当なし |

## 問題点一覧（優先度順）

### 1. [Medium] `YearlyBudgetView.vue` の `loadError` クリア漏れ（PR #65）

`fetchAllTimeSummary()`（`frontend/src/views/YearlyBudgetView.vue:85-92`）は失敗時に `loadError` をセットするが、成功時に `loadError.value = ""` をクリアしていない。同ファイルの `fetchYearData()` や他3ファイルは成功時にクリアしている中で、この関数だけ抜けている。

再現例: `getAllTimeSummary` が一時的に失敗（エラーメッセージ表示）→ 再試行や再マウントで成功しても、古いエラーメッセージが画面に残り続ける。

### 2. [Low] `ExpensesView.vue` の削除処理に依然エラーハンドリングなし（PR #65の範囲外）

`handleDelete` / `handleDeleteFromModal`（`frontend/src/views/ExpensesView.vue:194-205`）は `deleteExpense` を try/catch なしで呼んでいる。今回のPRは初期表示の読み込みのみが対象なのでスコープ外だが、削除失敗時に未処理のPromise rejectionになる点は今後の課題として残る。

### 3. [Low] パスワードバリデーションのテストカバレッジに1点抜け（PR #67）

8文字未満かつ複雑さ要件も満たさないケース（例: `"abc"`）のテストはないが、`min_length=8` 制約で確実に弾かれるため実害はなし。参考程度の指摘。

## 総評

PR #67・#69は実装・テストともに意図通りで問題なし。PR #65は概ね良い実装だが、`YearlyBudgetView.vue`の`fetchAllTimeSummary`だけ成功時クリアが漏れているのが唯一の実質的な不具合。
