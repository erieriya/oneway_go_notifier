# oneway_go_notifier

トヨタレンタカーの「片道GO!」（区間限定 特別料金プラン）ページを定期的に監視し、新着掲載をDiscordへ通知する非公式ツールです。

> **注意（非公式・無保証）**
> このツールはトヨタ自動車株式会社およびトヨタレンタカー各社とは一切関係のない非公式のものです。公開ページ（https://cp.toyota.jp/rentacar/ ）を定期的に取得して内容を通知するだけで、予約や在庫確保を行う機能はありません。掲載内容の正確性・最新性は保証しません。ページ構造の変更により動作しなくなる可能性があります。利用は自己責任でお願いします。

## できること

- 5分間隔（cron設定上。実際の発火間隔はGitHub Actionsの仕様上おおむね1時間に1回程度になります）でページを取得
- 前回取得時との差分から新着掲載のみを検知（重複通知しない）
- 受付終了（サイト側のCSSオーバーレイ表示。DOM上にテキストは存在しない）の掲載は通知しない
- Discord Webhookへ通知（スレッド指定も可能）
- 出発店舗・返却店舗名の部分一致条件で、スレッドごとに異なる絞り込み設定が可能（例:「関東→関西」「関西→関東」）
- 絞り込み条件に一致した掲載について、初出・最終確認・掲載終了日時などの履歴を`data/route_history.json`に保存
- 実行のたびに取得件数・新着件数・エラー内容などを`data/run_log.jsonl`に記録

## 構成

取得(`scraper.py`)・解析(`parser.py`)・状態管理(`state.py`)・通知(`notifier.py`)・フィルタ(`filters.py`)・複数スレッド設定(`targets.py`)・履歴(`history.py`)・ログ(`runlog.py`)を分離しています。サイトのHTML構造が変わった場合は基本的に`parser.py`の修正だけで対応できるはずです。

```
monitor.py          エントリポイント
src/
  scraper.py         HTTP取得
  parser.py          HTML解析 → Listing
  models.py          Listingデータモデル
  state.py           data/state.json の読み書き（前回スナップショット）
  filters.py         店舗名の部分一致フィルタ（OR条件対応）
  targets.py         スレッドごとの通知設定(NOTIFY_TARGETS)
  notifier.py         Discord Webhook送信
  history.py          data/route_history.json（掲載履歴）
  runlog.py           data/run_log.jsonl（実行ログ）
tests/               pytest（fixtureは実際のHTML構造を元にしたもの）
.github/workflows/monitor.yml   GitHub Actionsでの定期実行
```

## セットアップ

### 1. Discord Webhookを作成

投稿したいチャンネルの「連携サービス → ウェブフックを作成」でWebhook URLを発行します。

### 2. フォーク/このリポジトリをベースに自分のリポジトリを用意

### 3. GitHubのSecretsとVariablesを設定

`Settings → Secrets and variables → Actions`

**Secrets**（暗号化され、登録後は誰にも見えなくなる）

| Name | 内容 |
|---|---|
| `DISCORD_WEBHOOK_URL` | 手順1で発行したWebhook URL（必須） |
| `DISCORD_THREAD_ID`（任意） | 単一スレッドに投稿したい場合のスレッドID。`NOTIFY_TARGETS`を設定した場合はそちらが優先されます |

**Variables**（機密ではない設定値。Secretsタブの隣にある**Variables**タブ）

もっとも単純な「全件を1つのスレッドに通知」構成なら、`NOTIFY_TARGETS`は不要で以下だけで動きます。

| Name | 内容 |
|---|---|
| `ROUTE_FILTERS`（任意） | 絞り込み条件。未設定なら全件通知 |

スレッドを分けたい・絞り込みを複数持ちたい場合は`NOTIFY_TARGETS`にJSON配列を設定します（後述）。

### 4. GitHub Actionsの権限設定

`Settings → Actions → General → Workflow permissions` を **Read and write permissions** にしてください（`data/*.json`の自動コミットに必要です）。

### 5. 動作確認

`Actions` タブ → `monitor` ワークフロー → `Run workflow` で手動実行できます。

### 6. 定期実行を有効にする

`.github/workflows/monitor.yml`の`schedule`はコメントアウトしてあります（Secrets未設定のまま自動実行されて失敗し続けるのを防ぐためです）。1〜5の設定が終わって手動実行が問題なく動くことを確認したら、コメントを外して`schedule`を有効にしてください。

```yaml
on:
  workflow_dispatch: {}
  schedule:
    - cron: "*/5 * * * *"
```

## NOTIFY_TARGETS（複数スレッド・条件別通知）

`filters`は `出発店舗の部分一致条件:返却店舗の部分一致条件` の形式で、`,`区切りで複数ルール、各辺は`|`区切りでOR条件を書けます。店舗名は運営会社名（例:「トヨタレンタリース大阪」）の部分一致で判定します。

```json
[
  {
    "name": "関東→関西",
    "thread_id": "スレッドID",
    "filters": "トヨタモビリティサービス|トヨタレンタリース神奈川:トヨタレンタリース大阪|トヨタレンタリース京都"
  },
  {
    "name": "全件（絞り込みなし）",
    "thread_id": "別のスレッドID",
    "filters": ""
  }
]
```

`thread_id`はDiscordの開発者モードでスレッドを右クリック→「IDをコピー」で取得できます。`filters`を空にすると絞り込みなし（全件）になります。1件の新着が複数エントリの条件に合致すれば、それぞれのスレッドに投稿されます。

## 既知の制限

- GitHub Actionsの`schedule`イベントは「ベストエフォート」で、頻繁な間隔（5分毎など）を指定しても実際にはシステム負荷により1時間に1回程度まで間引かれることがあります。リアルタイム性が必要な場合は、外部のcronサービス（例: cron-job.org）からGitHub APIの`workflow_dispatch`を呼び出す構成に切り替えることを検討してください
- サイトのHTML構造（クラス名等）が変更されると`src/parser.py`の修正が必要になります

## ライセンス

MIT License. `LICENSE`を参照してください。
