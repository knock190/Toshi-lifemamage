# GASをチャットから更新する仕組み（引き継ぎメモ）

書き手：Ω（2026-09-25 としやすが共有したメモをそのまま置いた）。**このリポジトリは公開なので、ウェブアプリの URL とトークンの実値は絶対に書かない**（下はプレースホルダのまま）。

Claude（チャット側）がGoogleドライブ経由でGASプロジェクトを更新している仕組みのまとめ。
Claude Code 側で同じことをする、または続きを開発するための情報。

---

## 全体像

```
Claude ──(Drive API)──> 「GAS更新」フォルダ（ソース置き場）
                              │
本人が更新役のリンクを1タップ  │
                              ▼
                        「GAS更新役」GAS
                              │ (Apps Script API)
                              ▼
                        対象GASプロジェクト（本番コード）
```

ポイント:

- Claude は GAS プロジェクトを直接さわれない。Drive にソースを置くだけ。
- 実際の書き込みは「GAS更新役」という別の GAS プロジェクトが行う。
- 承認の必要な操作（本番反映）は必ず本人のタップを挟む設計。
- スプレッドシートは Drive 経由で直接読めるので、データ確認はチャットで完結する。

---

## 1. 更新役GAS

汎用。ターゲットを URL パラメータで指定するので、ツールごとに作る必要はない。

- プロジェクト名: `GAS更新役`
- 置き場所: Drive「だんごカンパニー」（ID: `1qmUK52bfRePBU9PO_rvj96ke2Cj4yHe5`）直下
- GCP プロジェクト番号: `842527543723`
- ウェブアプリ URL: `<UPDATER_URL>`
- トークン: `<UPDATER_TOKEN>`（スクリプトプロパティ保存。コードには書かない）

### アクション

| action | 内容 |
| --- | --- |
| `update` | Drive のソースをターゲットへ反映 |
| `rollback` | 直前のバックアップへ戻す |
| `version` | 現在の版を確認 |
| `create` | 新規ターゲット作成 |
| `targets` | 登録ターゲット一覧 |
| `settarget` / `deltarget` | ターゲット登録・削除 |
| `deployments` | デプロイ一覧 |

呼び出し例:

```
<UPDATER_URL>?token=<UPDATER_TOKEN>&action=update&target=supplement
```

### 挙動

- 反映前に自動バックアップ（`GAS更新/backup` フォルダ、10世代）。
- `deploymentId` を登録したターゲットは、反映と同時に新バージョンを作成し `/exec` にも反映される。
- 承認切れエラーが出たら、更新役の `checkSetup` を再実行する。

---

## 2. ソース置き場

- フォルダ名: `GAS更新`（旧名「サプリ更新」）
- フォルダ ID: `1SmwsYVL7zx36UTYOPZN096vB7n9nIQyj`
- 置き場所: 「だんごカンパニー」直下
- 形式: `text/plain`、Google形式への変換は無効にする
- ファイル名は各ターゲットのソース名と一致させる（例: `supplement_tracker.gs`）

---

## 3. 登録ターゲット

| target | 内容 | ソースファイル名 |
| --- | --- | --- |
| `supplement` | サプリ記録GAS（scriptId: `1wfSdt_CW4y7cqor-Ht7rNdTKR622rjCjFWOfr6FEJz04tvDJohX94Usc`、deploymentId 登録済み） | `supplement_tracker.gs` |
| `filemgr` | ファイル管理ツール（scriptId: `1ChDJVurlMf4JXDOelqyH9HsEy6_BfehY5MUmCCiHZCJX50KBWLrwNdh-`、中身は未実装） | `main.gs` |

---

## 4. サプリ記録GAS（ターゲット例）

- ウェブアプリ URL: `<SUPPLEMENT_URL>`
- トークン: `<SUPPLEMENT_TOKEN>`
- データ: スプレッドシート「サプリ管理DB」（ID: `106DCKP2WDetEIdR77fMQ9Tc_LKdaR4I_v6lGNngKC68`）
  - `master` シート: サプリ名 / 週の目標回数 / 木曜チェック
  - `log` シート: 日時 / サプリ名
- 置き場所: 「だんごカンパニー/サプリメント」（ID: `1wqRhhv_12VHm2KVBcAaHNGa60oJFShjU`）

### API（POST は JSON、GET も可）

| action | 内容 |
| --- | --- |
| `list` | 登録サプリ一覧 |
| `record` (`name`) | 1回記録 |
| `cancel` (`name`) | 今週の最新1回を取り消し |
| `status` | 今週の全サプリの回数 |
| `zero` | 木曜チェックONで今週0回のサプリ |
| `month` / `lastmonth` | 今月 / 先月の集計 |
| `add` (`name`, `target`, `thursday`) | サプリ追加 |
| `remove` (`name`) | サプリ削除（log の記録は残る） |
| `ping` | 動作確認（コードの版を返す） |
| `dashboard` (GETのみ、`month`, `name`) | グラフ付きページ |

### 設計上の注意

- 週は月曜 0:00 開始、日曜終わり。
- 週の目標回数はコードではなくシートに持つ。変更はセル書き換えのみで即反映される。
- 週ごとの目標は履歴を持たないので、目標を変えると過去の週も現在の目標で再判定される。
- 記録の重複防止はなし。押し間違いは `cancel` で戻す。
- 通知は iPhone のオートメーションから叩く（木曜20時 → `zero`、日曜18時 → `status`）。

---

## 5. 運用フロー（コード修正時）

1. コード全文を書く。
2. `GAS更新` フォルダに `text/plain`・変換なしで置く（同名で新規追加）。
3. `action=update&target=<名前>` のリンクを本人に渡す。
4. 本人がタップして反映。
5. 問題があれば `action=rollback`。

---

## 6. Code側から直接叩く場合

チャット側と違い、Code側は端末から HTTP を直接投げられる。本人のタップを挟まずに反映まで完結できる。

### 事前準備

#### トークンとURL

環境変数に置く。リポジトリには入れない。

```bash
# ~/.zshrc など（リポジトリ外）
export GAS_UPDATER_URL="https://script.google.com/macros/s/xxxx/exec"
export GAS_UPDATER_TOKEN="xxxx"
export SUPPLEMENT_URL="https://script.google.com/macros/s/yyyy/exec"
export SUPPLEMENT_TOKEN="yyyy"
```

#### rclone（Drive接続）

Code 側は最初から Drive につながっていないので、一度だけ認証しておく。チャット側の Drive 接続は引き継がれない。

```bash
brew install rclone   # macOS
rclone config
```

対話で聞かれる項目:

| 項目 | 答え |
| --- | --- |
| `n/s/q` | `n`（新規） |
| `name` | `gdrive` |
| `Storage` | `drive` |
| `client_id` / `client_secret` | 空のままEnter（自分のOAuthクライアントを使う場合のみ入力） |
| `scope` | `1`（フルアクセス。書き込みが必要） |
| `service_account_file` | 空のままEnter |
| `Edit advanced config` | `n` |
| `Use web browser to authenticate` | `y`（ブラウザが開くのでGoogleアカウントを許可） |
| `Configure this as a Shared Drive` | `n` |

確認:

```bash
rclone lsd gdrive:だんごカンパニー
rclone ls gdrive:だんごカンパニー/GAS更新
```

`GAS更新` の中身（`supplement_tracker.gs` など）が見えれば準備完了。

補足:

- `client_id` を空にすると rclone 共用のOAuthクライアントを使うため、混雑時に遅くなることがある。気になるなら Google Cloud で自分のクライアントIDを作って入れる。
- 認証情報は `~/.config/rclone/rclone.conf` に入る。このファイルはリポジトリに入れない。
- SSH越しなど、ブラウザが開けない環境では `rclone authorize drive` を手元のPCで実行してトークンを貼る。

### 反映スクリプト

`scripts/gas-deploy.sh` として置く想定。

```bash
#!/usr/bin/env bash
set -euo pipefail

# 使い方: ./gas-deploy.sh <target> [action]
#   ./gas-deploy.sh supplement          # 反映
#   ./gas-deploy.sh supplement version  # 版の確認
#   ./gas-deploy.sh supplement rollback # 戻す

target="${1:?target を指定してください}"
action="${2:-update}"

: "${GAS_UPDATER_URL:?GAS_UPDATER_URL が未設定}"
: "${GAS_UPDATER_TOKEN:?GAS_UPDATER_TOKEN が未設定}"

curl -sSL -G "$GAS_UPDATER_URL" \
  --data-urlencode "token=$GAS_UPDATER_TOKEN" \
  --data-urlencode "action=$action" \
  --data-urlencode "target=$target"
echo
```

`-L` は必須。Apps Script のウェブアプリはリダイレクトを返す。

### ソースの正本はDrive

このツールのソースは Drive の「GAS更新」フォルダが正本。Git には入れない。

- 実質1ファイル、作業者は1人。Git を挟む理由がない。
- スマホだけで完結することがこの仕組みの狙い。Git を正本にすると、その場でスマホから直せなくなる。
- Drive と Git の二重管理は、入れ忘れた版が出た時点で Git が嘘をつく。
- 履歴と復旧は更新役のバックアップ（10世代）とロールバックでまかなう。

Code 側で編集するときも、Drive のファイルを取ってきて、直して、Drive へ戻す。ローカルのファイルは作業用のコピーにすぎない。

**Drive へ上げる（rclone）**

```bash
# 取ってくる
rclone copyto gdrive:だんごカンパニー/GAS更新/supplement_tracker.gs \
  ./work/supplement_tracker.gs

# 直したら戻して反映
rclone copyto ./work/supplement_tracker.gs \
  gdrive:だんごカンパニー/GAS更新/supplement_tracker.gs
./scripts/gas-deploy.sh supplement
```

**clasp で直接pushしない**

`clasp push` は Drive も更新役も経由しないので、バックアップに残らず、ロールバックも効かず、Drive のソースと本番がずれる。この仕組みでは使わない。

### 記録GASを叩く

```bash
# 動作確認
curl -sSL -G "$SUPPLEMENT_URL" \
  --data-urlencode "token=$SUPPLEMENT_TOKEN" \
  --data-urlencode "action=ping"

# 今週の状況
curl -sSL -G "$SUPPLEMENT_URL" \
  --data-urlencode "token=$SUPPLEMENT_TOKEN" \
  --data-urlencode "action=status"

# POST（JSON）
curl -sSL -X POST "$SUPPLEMENT_URL" \
  -H 'Content-Type: application/json' \
  -d "{\"token\":\"$SUPPLEMENT_TOKEN\",\"action\":\"record\",\"name\":\"クレアチン\"}"
```

### 注意

- 直接叩けるということは、確認なしで本番が書き換わるということ。`update` の前に `version` で今の版を控える癖をつける。
- 反映後は必ず `ping` で版を確認する。コードの `CODE_VERSION` を毎回書き換えておくと、反映されたか一目で分かる。
- 必ず Drive 経由で更新する。Drive を飛ばすと、チャット側と本番がずれる。
- バックアップは10世代の窓なので、古い版は順に消える。長く残したい版があるときだけ、別途コピーを取る。

---

## 7. 秘密情報の扱い

- トークンはこのファイルにはプレースホルダで置いてある。実値はスクリプトプロパティとチャット側の記憶にある。
- このメモをリポジトリへ置く場合も、実値は書かず環境変数に持たせる。
- ウェブアプリ URL はトークンとセットで実行権限になるので、URL も公開しない。
