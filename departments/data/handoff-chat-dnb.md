# チャット側への引き継ぎ：習慣データGAS（DNBの記録）を動かす

書き手：データ部（Claude Code 側）。2026-09-25。
このメモをチャット側の Claude に渡し、としやすと一緒に作業を最後まで進めてもらう。

---

## 1. なぜ作るのか

- としやすは『超効率勉強法』（メンタリストDaiGo）6章のアクションプランとして、**DNB（デュアルNバック）を1日15分・1か月（〜10/24）** やっている
- 伸びは IQ テストではなく **アプリの成績（N と正解率）** で見ると決めた。初回は 2026-09-25 14:00、**N=1・正解率45%**
- 記録は **Git に貯めない**（としやすの判断）。スプレッドシートに貯め、グラフのページと毎朝の報告で見えるようにする
- 習慣のデータ（DNB・サプリ・体重・筋トレ…）は、**1つのスプレッドシート「習慣データ」にシートで分けて** 貯める。持ち主は新しく作った **データ部**（だんごカンパニーの「部門」）
- 入力は **iPhone ショートカット → GAS → スプレッドシート**（サプリと同じ形）。Claude はドライブの道具ではスプレッドシートに行を足せないため、書き込みは GAS にやらせる
- GAS は、**チャットから作る仕組み（GAS更新役）** で作る

## 2. Code 側で終わっていること

| もの | 場所・中身 |
|---|---|
| フォルダ「データ部」 | 「だんごカンパニー」直下（ID：`1tkTQt8myt1HLZahU5aBRQOQ-8veawjt-`） |
| スプレッドシート「習慣データ」 | 「データ部」の中（ID：`1BxLuhkWOdBczRrW2gf2GkhHN5c-znUSACOL5lt8ciPs`）。1枚目（シート名は今「Untitled」）に見出し `日時 / N / 正解率 / メモ` と初回 `2026/09/25 14:00 / 1 / 45 / 初回` |
| ソース `habit_data.gs` | 「GAS更新」フォルダ（ID：`1SmwsYVL7zx36UTYOPZN096vB7n9nIQyj`）。text/plain・変換なし |
| ソース `appsscript.json` | 同じフォルダ。タイムゾーン Asia/Tokyo、ウェブアプリ（全員アクセス・自分として実行） |

### habit_data.gs の中身（要点）
- スプレッドシートに **バインドして** 使う（`SpreadsheetApp.getActiveSpreadsheet()`）
- `setup()`：トークンを作ってスクリプトプロパティに保存し、ログに出す。シート「DNB」を用意する（1枚目の見出しが同じなら名前を「DNB」に付け替える）
- ウェブアプリの action（POST は JSON、GET も可。どれも `token` が必要）

| action | 内容 |
|---|---|
| `ping` | 動作確認。`{ok, version}`（版 `2026-09-25.1`） |
| `dnb`（`n`, `accuracy`, `memo`?） | DNB を1行足す。n は 1〜20 の整数、accuracy は 0〜100。返り値 `{ok, message}` |
| `dnb_undo` | DNB の最後の1行を消す |
| `dnb_last` | DNB の最後の記録を返す |

- エラーは `{ok:false, error}` で返る

### 更新役GASで確かめたこと（`gas_updater.gs` を読んだ）
- `create` は `title`・`name`・`parentId` を受け取る。`parentId` にスプレッドシートの ID を渡すと、**そのスプレッドシートにバインドした** プロジェクトができる
- `create` の `file` は1つしか登録されないので、ファイル2つは `update` のときに `file=appsscript.json,habit_data.gs`（カンマ区切り）で渡す
- 新しいプロジェクトの **最初のデプロイと承認は、エディタで手でやる必要がある**（更新役にはデプロイを新しく作る action がない。`update` は登録済みの deploymentId を差し替えるだけ）

## 3. チャット側にお願いしたい作業（としやすと一緒に）

実値の URL・トークンはチャット側の記憶にある前提。**リンクを組み立てて、としやすに渡してタップしてもらう。**

1. **プロジェクトを作る**（としやすがタップ）
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=create&title=習慣データGAS&name=habit&parentId=1BxLuhkWOdBczRrW2gf2GkhHN5c-znUSACOL5lt8ciPs`
   → 結果の `scriptId` とエディタのリンクを控える
2. **コードを入れる**（タップ）
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=update&target=habit&file=appsscript.json,habit_data.gs`
   → 「コードを反映しました」。2ファイルが出ていることを確かめる
3. **setup を実行**（としやすがエディタで）
   エディタを開く → 関数 `setup` を実行 → 承認 → 実行ログの **トークン** を控える
   → スプレッドシートの1枚目の名前が「DNB」に変わっていれば OK
4. **デプロイ**（としやすがエディタで）
   デプロイ → 新しいデプロイ → ウェブアプリ／自分として実行／全員 → **ウェブアプリの URL** を控える
5. **次から自動で反映されるように登録**（タップ2回）
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=deployments&target=habit` → HEAD 以外の deploymentId を見る →
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=settarget&name=habit&scriptId=<scriptId>&file=appsscript.json,habit_data.gs&deploymentId=<deploymentId>`
6. **動作確認**：`<ウェブアプリのURL>?token=<トークン>&action=ping` → `{"ok":true,"version":"2026-09-25.1"}`
7. **iPhone ショートカット「DNB記録」**（としやすと一緒に）
   1. 数値を尋ねる「N（何個前）」
   2. 数値を尋ねる「正解率（%）」
   3. URL の内容を取得：ウェブアプリの URL／POST／本文 JSON：`token`＝トークン、`action`＝`dnb`、`n`＝1つ目の数値、`accuracy`＝2つ目の数値
   4. 辞書の値を取得：`message`
   5. 通知を表示：4 の値
   - ホーム画面に置く。できれば、オートメーション「App → DNB アプリを閉じたとき → DNB記録を実行」も
8. **試す**：ショートカットで送る → 「DNBを記録しました」→ 習慣データの DNB シートに1行増える → 試しの行は `?token=<トークン>&action=dnb_undo` で消す

## 4. 守ってほしいこと

- **URL・トークンの実値は GitHub に書かない**（台帳のリポジトリ `knock190/Toshi-lifemamage` は公開）。チャット側の記憶とスクリプトプロパティだけに置く
- ソースの正本は Drive「GAS更新」。直すときは Drive のファイルを直して `update`（clasp で直接 push しない）
- 反映したら `ping` で版を確かめる。コードを直すときは `CODE_VERSION` を上げる
- 「GAS更新」の `appsscript.json` は、今は習慣データGAS（target=habit）用。ほかのターゲットでマニフェストを反映するときは、名前の重なりに注意する
- サプリ記録GAS（target=supplement）と「サプリ管理DB」には触らない

## 5. 終わったら Code 側（だんごカンパニーの秘書）に伝えること

秘密は書かずに、次の3つだけ：
- 「習慣データGAS、できた」
- `scriptId`（秘密ではない）と、`ping` の版
- 試しの記録を消したかどうか

→ 秘書が「習慣データ」を読んで確かめ、データ部が次（グラフのページ）に進む
